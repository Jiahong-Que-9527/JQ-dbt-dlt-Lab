# dlt + dbt Lab

一个面向生产环境熟练度的 dlt + dbt 学习沙箱，跑在 DuckDB 上。

按 [experiments/](experiments/) 里编号顺序做完 26 个 notebook，你应该能：
- 用 dlt 写出带增量游标、schema contract、secrets 管理的生产 pipeline
- 用 dbt 写出带 snapshot、自定义测试、source freshness、slim CI 的生产项目
- 把两者串成一个有可观测性、能进 CI 的工作流

## 目录

- [Prerequisites（运行前提）](#prerequisites)
- [快速开始：拉起环境](#快速开始拉起环境)
- [做实验的工作流](#做实验的工作流)
- [关闭与清理环境](#关闭与清理环境)
- [常见故障排查](#常见故障排查)
- [架构 / 项目结构 / Makefile / 学习路径](#架构)

---

## Prerequisites

在拉起环境前你需要：

| 依赖 | 检查命令 | 安装提示 |
|---|---|---|
| **`uv`**（包管理器） | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Python 3.11 或 3.12** | `python3 --version` | uv 会自动从 `.python-version` 装 |
| **`make`** | `make --version` | macOS：`xcode-select --install` / Linux：`apt install make` |
| **`duckdb` CLI**（可选） | `duckdb --version` | 不装也行，notebook 里都是用 Python 库 |
| 端口 **8888**（JupyterLab）| `lsof -i :8888` | 被占就关掉占用进程 |
| 端口 **8080**（dbt docs，可选）| `lsof -i :8080` | 同上 |
| 外网访问 | `curl https://api.frankfurter.app/latest` | dlt 要从 Frankfurter / JSONPlaceholder 拉数据 |

---

## 快速开始：拉起环境

**首次安装**（5 分钟）：

```bash
# 1. 装 Python 依赖（uv 会自动建 .venv 并按 pyproject.toml 安装）
make install

# 2. 装 dbt packages（dbt_utils 等）
make deps

# 3. 跑一次完整 pipeline，确认环境 OK
make all          # = make ingest + make build
```

**期望结果**：`make all` 末尾应看到类似 `Done. PASS=21 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=21`。如果出错请看 [常见故障排查](#常见故障排查)。

**启动 JupyterLab 做实验**：

```bash
make lab
```

它会启动 JupyterLab 在 `http://localhost:8888`，并把工作目录设为 `experiments/`。在终端会显示带 token 的 URL，复制粘贴到浏览器即可。

---

## 做实验的工作流

### 1. 推荐顺序

按 **01 → 26** 顺序做。前面的实验给后面铺垫数据和概念，跳着做容易遇到 “表不存在 / 状态不对” 的情况。

实验地图见 [experiments/README.md](experiments/README.md)。

### 2. 每个 notebook 的标准结构

每个 notebook 都包含：
1. **目标 + 关键概念**（markdown）
2. **可运行代码 cell**（按顺序执行）
3. **生产环境踩坑提示**
4. **思考题**

跑代码时一直按 **Shift+Enter** 顺序往下走即可。

### 3. 关于实验之间的状态依赖

- **`raw_ecb` schema 与 `main` schema 必须存在**。如果还没跑过 `make all`，先跑一次。
- 实验 16（snapshot）、17（seed）、19（custom test）会**留下产物**（`snapshots.snp_currencies`、`main.currency_regions`、audit 表等），是预期的，不需要清。
- 实验 09（incremental cursor）、12（nested JSON）、14（filesystem）会建独立的 schema（`raw_ecb_inc`、`raw_users`、本地 parquet 目录），不会污染 main。
- 部分实验会**临时改文件再还原**（比如 19 改 `_staging.yml`、22 改 `stg_ecb_rates.sql`）。每个这种实验最后都有"清理 cell"——一定要运行它再开下一个实验。如果忘了，跑 `git status` 看 diff，`git checkout -- <file>` 恢复。

### 4. ⚠️ DuckDB 文件锁（最常见的坑）

DuckDB 同一个文件**默认不允许多个写连接同时打开**。如果你：

- 在 JupyterLab 里跑了 `duckdb.connect('../data/sandbox.duckdb')`
- 然后又在另一个终端 `make ingest` 或 `make build`

会报 `Could not set lock on file ... Conflicting lock`。

**解决方法**（任选其一）：

| 方法 | 命令 | 适用 |
|---|---|---|
| 显式关连接 | `con.close()` 跑完一段就关 | 长 notebook 推荐 |
| 用只读连接做查询 | `duckdb.connect(..., read_only=True)` | 只查不写时 |
| 重启 kernel | JupyterLab 顶部 Kernel → Restart | 已经卡住时最快 |
| 关 JupyterLab 再跑 make | Ctrl-C 关 lab 进程 | 终端命令必须跑时 |

各 notebook 的代码已经尽量在每段结束 close 掉连接，但跑到一半中断的话连接会留着，重启 kernel 最干净。

### 5. 看 lineage / 数据

```bash
make docs              # dbt 文档站，含 lineage graph，开在 :8080
duckdb data/sandbox.duckdb     # CLI 查表
```

更多查询见末尾的 [常用 DuckDB CLI 命令](#常用-duckdb-cli-命令)。

---

## 关闭与清理环境

### 优雅停止当前 session

```bash
# 1. JupyterLab：在跑它的终端按 Ctrl-C 两次（或 File → Shut Down 后再 Ctrl-C）
#    这会关闭所有 kernel + 释放 DuckDB 文件锁

# 2. dbt docs serve（如开过）：在跑它的终端按 Ctrl-C

# 3. 清理 dbt 编译产物（可选；不影响数据）
make clean
```

### 完全重置到出厂状态

下面这套命令把项目还原到 `make install` 之后的状态：

```bash
# 1. 确认没有进程占着 DuckDB 文件
lsof data/sandbox.duckdb || echo "no lockers"

# 2. 清 dbt 产物 + 删数据库 + 删 parquet lake
make clean
make reset

# 3. （可选）还原临时改过的文件——以防某个实验的清理 cell 没跑完
git status                          # 看哪些文件被改过
git checkout -- <files-to-revert>   # 还原
git clean -fd dbt_project/analyses  # 删 notebook 临时创建的 analysis 文件
```

跑完 `make reset` 之后，下次再 `make all` 即可重新开始。

### 卸载整个项目

```bash
# 1. 关掉所有相关进程（JupyterLab、dbt docs serve）
# 2. 删 venv（uv 管理的）
rm -rf .venv
# 3. 删数据
make reset
# 4. （决定不要这个项目时）
cd .. && rm -rf JQ-dbt-dlt-Lab
```

---

## 常见故障排查

| 症状 | 原因 | 处理 |
|---|---|---|
| `Conflicting lock` on duckdb | 另一个进程开着连接 | 重启 JupyterLab kernel 或 `lsof data/sandbox.duckdb` 找到占用进程 kill |
| `dbt: command not found` | 没用 `uv run` | 一律用 `uv run dbt ...` 或 `make build` |
| `Profile not found` | `DBT_PROFILES_DIR` 没设 | Makefile target 已加；手动跑要 `cd dbt_project && DBT_PROFILES_DIR=. uv run dbt ...` |
| `relation "raw_ecb.daily_rates" does not exist` | 没跑过 ingest | `make ingest` 一次 |
| 实验 11 跑完 secrets.toml 残留 | 实验的清理 cell 没跑 | `rm .dlt/secrets.toml .dlt/config.toml` |
| JupyterLab 8888 端口被占 | 之前的 lab 没关干净 | `lsof -i :8888` 找 PID 后 `kill <PID>` |
| `make` 提示找不到目标 | 当前目录不对 | `cd` 到项目根目录（含 Makefile 的那个）|
| 网络拉不到 Frankfurter | 公司代理 / 离线环境 | dlt 支持 HTTP_PROXY 环境变量；或先离线缓存数据 |

---

## 架构

```
Frankfurter API ─┐
                 ├─→ dlt ─→ DuckDB (raw_* schemas) ─→ dbt ─→ DuckDB (main / main_prod)
JSONPlaceholder ─┘                                                  │
                                                                    └─→ snapshots / seeds / audit
```

版本：dlt 1.27+，dbt-core 1.11+，dbt-duckdb 1.10+，DuckDB 1.5+。

## 项目结构

```
JQ-dbt-dlt-Lab/
├── README.md
├── Makefile                       # convenience targets
├── orchestration.py               # 端到端 Python 入口（实验 15/26）
├── pyproject.toml                 # uv-managed deps
├── .dlt/
│   ├── config.toml.example        # dlt 公共配置示例
│   └── secrets.toml.example       # dlt 密钥示例（实际文件 gitignored）
├── data/                          # sandbox.duckdb + parquet lake（都 gitignored）
├── dlt_pipelines/
│   ├── ecb_rates.py               # 主 pipeline（实验 1–8）
│   ├── ecb_rates_incremental.py   # 增量游标版（实验 9）
│   └── users_nested.py            # 嵌套 JSON demo（实验 12）
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml               # dev + prod target
│   ├── packages.yml               # dbt_utils
│   ├── models/                    # staging + marts
│   ├── seeds/                     # currency_regions.csv（实验 17）
│   ├── snapshots/                 # snp_currencies.sql（实验 16）
│   ├── tests/                     # singular test（实验 19）
│   ├── macros/                    # 自定义 macros + generic test（实验 18/19）
│   └── analyses/
└── experiments/                   # 26 个学习 notebook
```

## Makefile targets

| Target | What it does |
|---|---|
| `make install` | uv sync —— 安装 Python 依赖 |
| `make deps` | 装 dbt_utils 等 dbt packages |
| `make ingest` | 跑主 dlt pipeline |
| `make ingest-incremental` | 跑增量游标 pipeline（实验 9） |
| `make ingest-nested` | 跑嵌套 JSON pipeline（实验 12） |
| `make seed` | dbt seed（实验 17） |
| `make snapshot` | dbt snapshot（实验 16） |
| `make freshness` | dbt source freshness（实验 20） |
| `make build` | dbt build = seed + snapshot + run + test |
| `make orchestrate` | 端到端 Python 入口（实验 15/26） |
| `make docs` | dbt docs generate + serve（端口 8080） |
| `make lab` | JupyterLab 跑实验（端口 8888） |
| `make all` | ingest + build |
| `make clean` | 清 dbt 编译产物，不动数据 |
| `make reset` | 删 DuckDB 文件 + parquet lake，回到出厂 |

## 学习路径

详见 [experiments/README.md](experiments/README.md)。简述：

- **01–08**：入门，过一遍工具的核心概念（merge / view-vs-table / lineage / 内部表）
- **09–15**：dlt 生产能力（增量游标 / schema contract / secrets / 嵌套 JSON / 测试 / 文件系统 / dlt-dbt 整合）
- **16–25**：dbt 生产能力（snapshot / seed / macro / 自定义测试 / freshness / hooks / slim CI / incremental 策略 / 多 target / dbt_utils）
- **26**：把以上全部串成端到端 + slim CI workflow

## 常用 DuckDB CLI 命令

```sql
duckdb data/sandbox.duckdb       -- 进入交互式

show all tables;
show tables from raw_ecb;
select * from main.fct_daily_rates limit 5;
select * from raw_ecb._dlt_loads;
select * from snapshots.snp_currencies;
select * from audit.dbt_runs order by started_at desc;

.exit                            -- 退出（释放文件锁！）
```

> 注意：DuckDB CLI 退出前请用 `.exit` 而不是直接关终端，否则文件锁可能没释放。

## Links

- [dlt 文档](https://dlthub.com/docs)
- [dbt 文档](https://docs.getdbt.com)
- [dbt_utils](https://github.com/dbt-labs/dbt-utils)
- [Frankfurter API](https://api.frankfurter.app)
- [JSONPlaceholder](https://jsonplaceholder.typicode.com)
