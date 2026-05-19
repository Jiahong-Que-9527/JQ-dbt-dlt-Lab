# dlt + dbt Sandbox 项目搭建任务清单

> 本文件根据 [dlt-dbt-sandbox-spec.md](dlt-dbt-sandbox-spec.md) 拆解。
> Code agent 每完成一项，就把对应 `[ ]` 改为 `[x]`。
> 顺序很重要：上游任务未完成前，不要跳到下游(例如 dlt 没跑通就别写 dbt models)。
> 核心原则:**simplicity > "future flexibility"**。任何时候想加新东西，先回去看 spec §11 "Out of Scope"。

---

## Phase 0 — 准备工作 & 环境检查

- [ ] **0.1** 确认当前目录是 `/root/Workspace-llm/Tutorialspace/JQ-dbt-dlt-Lab/`
- [ ] **0.2** 确认 `uv` 已安装:`uv --version`(若无,提示用户安装,不要自行 curl 脚本)
- [ ] **0.3** 确认 Python 3.11 或 3.12 可用:`uv python list`
- [ ] **0.4** 确认能访问 Frankfurter API:`curl -s https://api.frankfurter.app/latest` 应返回 JSON
- [ ] **0.5** 阅读 spec §11 (Out of Scope) 和 §12 (Final Note),把"不要做"的清单装进脑子

---

## Phase 1 — 根目录配置文件

### 1.1 `.python-version`
- [ ] 创建文件,内容为 `3.12`(或 `3.11`,选一个固定)

### 1.2 `pyproject.toml`
- [ ] 按 spec §7 创建,字段:
  - [ ] `name = "dlt-dbt-sandbox"`
  - [ ] `version = "0.1.0"`
  - [ ] `description = "Learning sandbox for dlt + dbt on DuckDB"`
  - [ ] `requires-python = ">=3.11,<3.13"`
  - [ ] dependencies: `dlt[duckdb]>=1.0`, `dbt-core>=1.7`, `dbt-duckdb>=1.7`, `requests>=2.31`
  - [ ] dev group: `ruff>=0.5`
- [ ] 运行 `uv sync`,确保无错误,生成 `.venv/` 和 `uv.lock`
- [ ] 在 README 待办里记录实际安装到的 dlt / dbt-core / dbt-duckdb 版本号

### 1.3 `.gitignore`
- [ ] 按 spec §9 逐行复制,确保包含:
  - [ ] `.venv/`
  - [ ] `__pycache__/`, `*.pyc`
  - [ ] `.python-version`
  - [ ] `data/*.duckdb`, `data/*.duckdb.wal`
  - [ ] `dbt_project/target/`, `dbt_project/dbt_packages/`, `dbt_project/logs/`
  - [ ] `.DS_Store`

---

## Phase 2 — 目录骨架

按 spec §3 的目录树创建空目录与占位文件。

- [ ] **2.1** 创建 `data/` 目录
- [ ] **2.2** 创建 `data/.gitkeep`(空文件)
- [ ] **2.3** 创建 `dlt_pipelines/` 目录
- [ ] **2.4** 创建 `dlt_pipelines/__init__.py`(空文件即可)
- [ ] **2.5** 创建 `dbt_project/` 目录
- [ ] **2.6** 创建 `dbt_project/models/staging/` 目录
- [ ] **2.7** 创建 `dbt_project/models/marts/` 目录
- [ ] **2.8** 创建 `dbt_project/seeds/` 目录(空,但目录要在)
- [ ] **2.9** 创建 `dbt_project/tests/` 目录(空,但目录要在)
- [ ] **2.10** 用 `tree -a -L 3 -I '.venv|__pycache__'` 或 `ls -R` 验证骨架与 spec §3 一致

---

## Phase 3 — dlt Pipeline 实现 (`dlt_pipelines/ecb_rates.py`)

参考 spec §4。**目标 ~80 行代码,超过 120 行说明过度工程化。**

### 3.1 文件骨架
- [ ] 创建 `dlt_pipelines/ecb_rates.py`
- [ ] import 必需:`dlt`, `requests`, `typing` 中需要的类型
- [ ] 顶部加一行模块 docstring,说明这是 ECB 汇率 ingestion

### 3.2 实现 `currencies_meta` resource
- [ ] 用 `@dlt.resource(write_disposition="replace", name="currencies_meta")` 装饰
- [ ] 函数返回 (yield) 5 个 dict:`USD/GBP/CHF/JPY/CNY`,字段 `code` 和 `name`
  - USD → US Dollar
  - GBP → British Pound
  - CHF → Swiss Franc
  - JPY → Japanese Yen
  - CNY → Chinese Yuan
- [ ] 一行 docstring + 返回类型注解

### 3.3 实现 `daily_rates` resource
- [ ] 用 `@dlt.resource(write_disposition="merge", primary_key=["date", "currency"], name="daily_rates")` 装饰
- [ ] 调用 Frankfurter 的范围端点 `https://api.frankfurter.app/2024-01-01..?to=USD,GBP,CHF,JPY,CNY` (基于 EUR)
  - 注意:Frankfurter `..` 范围端点不需要结束日期就会到 today
  - 若你选择写明结束日期,使用 `datetime.date.today().isoformat()`
- [ ] 解析返回 JSON 的 `rates` dict,按 (date, currency) 展开为 long format,每行字段:`date`, `currency`, `rate`
- [ ] yield 出每一行 dict
- [ ] 一行 docstring + 返回类型注解
- [ ] **不要**写 retry / rate limit / 复杂错误处理

### 3.4 实现 source
- [ ] 用 `@dlt.source(name="ecb")` 装饰一个函数,返回 `[daily_rates(), currencies_meta()]`
- [ ] 一行 docstring

### 3.5 主入口
- [ ] `if __name__ == "__main__":` 块内:
  - [ ] `pipeline = dlt.pipeline(pipeline_name="ecb_rates_pipeline", destination="duckdb", dataset_name="raw_ecb")`
  - [ ] 配置 duckdb destination 指向 `data/sandbox.duckdb`(可通过 `destination=dlt.destinations.duckdb("data/sandbox.duckdb")`)
  - [ ] `load_info = pipeline.run(...)`
  - [ ] 打印一段简短 summary,例如 `print(load_info)` 或行数统计

### 3.6 验证 dlt 跑通
- [ ] 运行 `uv run python dlt_pipelines/ecb_rates.py`
- [ ] 看到 `data/sandbox.duckdb` 文件生成
- [ ] 用 `uv run python -c "import duckdb; con=duckdb.connect('data/sandbox.duckdb'); print(con.execute('SHOW TABLES FROM raw_ecb').fetchall())"` 确认有 `daily_rates`, `currencies_meta` 表
- [ ] 确认 `daily_rates` 行数 > 100:
  `uv run python -c "import duckdb; print(duckdb.connect('data/sandbox.duckdb').execute('SELECT COUNT(*) FROM raw_ecb.daily_rates').fetchone())"`
- [ ] **再次**运行 ingest,行数不应翻倍 → 验证 merge disposition 工作

### 3.7 控制行数
- [ ] `wc -l dlt_pipelines/ecb_rates.py` ≤ 120 行;目标 ≤ 80 行。超了就回去简化

---

## Phase 4 — dbt 项目骨架配置

### 4.1 `dbt_project/dbt_project.yml`
- [ ] 按 spec §5 创建,必含字段:
  - [ ] `name: dlt_dbt_sandbox`
  - [ ] `version: '1.0.0'`
  - [ ] `profile: dlt_dbt_sandbox`
  - [ ] `model-paths: ["models"]`, `seed-paths: ["seeds"]`, `test-paths: ["tests"]`
  - [ ] `models:` 段:
    - `dlt_dbt_sandbox.staging.+materialized: view`
    - `dlt_dbt_sandbox.marts.+materialized: table`

### 4.2 `dbt_project/profiles.yml` (项目内,不放 ~/.dbt/)
- [ ] 按 spec §5 创建,内容:
  ```yaml
  dlt_dbt_sandbox:
    target: dev
    outputs:
      dev:
        type: duckdb
        path: ../data/sandbox.duckdb
        threads: 4
  ```

### 4.3 `dbt_project/packages.yml`
- [ ] 引入 `dbt-labs/dbt_utils`,使用当前最新兼容版本(查 dbt hub 或用 `>=1.1.0` 这种约束)

### 4.4 安装 dbt packages
- [ ] 在仓库根目录运行(注意 profile 路径):
  `cd dbt_project && DBT_PROFILES_DIR=. uv run dbt deps`
- [ ] 出现 `dbt_packages/dbt_utils/` 目录即成功

### 4.5 dbt 连接验证
- [ ] 运行 `cd dbt_project && DBT_PROFILES_DIR=. uv run dbt debug`
- [ ] 所有检查应为 OK,Connection test 通过

---

## Phase 5 — dbt Sources 声明

### 5.1 `dbt_project/models/staging/_sources.yml`
- [ ] 声明 source `raw_ecb`,database 字段可省略(duckdb 单文件)
- [ ] 在 source 下两个 tables:
  - [ ] `daily_rates`
    - 加 `description`
    - 在 `date` 列加 `not_null` 测试
    - 在 `currency` 列加 `not_null` 测试
  - [ ] `currencies_meta`
    - 加 `description`
    - 在 `code` 列加 `not_null` + `unique` 测试

### 5.2 验证 source 测试可识别
- [ ] 运行 `cd dbt_project && DBT_PROFILES_DIR=. uv run dbt test --select source:*`
- [ ] 应该看到 4+ 个测试通过

---

## Phase 6 — Staging 模型

### 6.1 `dbt_project/models/staging/stg_ecb_rates.sql`
- [ ] `SELECT` from `{{ source('raw_ecb', 'daily_rates') }}`
- [ ] 显式 CAST:`date::DATE AS rate_date`,`rate::DOUBLE AS rate`
- [ ] 保留 `currency`(若 dlt 列名为 camelCase 则改 snake_case)
- [ ] 增加 `_dlt_load_id` 透传,重命名为 `loaded_at_load_id`(展示 dlt metadata 如何流入 dbt)
- [ ] 文件顶部一行 SQL 注释说明用途

### 6.2 `dbt_project/models/staging/_staging.yml`
- [ ] 声明 model `stg_ecb_rates`,加 description
- [ ] 列级测试:
  - [ ] `rate_date`: `not_null`
  - [ ] `currency`: `not_null`
  - [ ] `rate`: `not_null`

### 6.3 验证 staging
- [ ] 运行 `cd dbt_project && DBT_PROFILES_DIR=. uv run dbt run --select stg_ecb_rates`
- [ ] 运行 `cd dbt_project && DBT_PROFILES_DIR=. uv run dbt test --select stg_ecb_rates`
- [ ] 应该全绿

---

## Phase 7 — Marts 模型

### 7.1 `dbt_project/models/marts/dim_currencies.sql`
- [ ] `SELECT` from `{{ source('raw_ecb', 'currencies_meta') }}`
- [ ] 重命名:`code AS currency_code`,`name AS currency_name`
- [ ] 简单 passthrough,无聚合

### 7.2 `dbt_project/models/marts/fct_daily_rates.sql`
- [ ] CTE 1:`stg` from `{{ ref('stg_ecb_rates') }}`
- [ ] CTE 2:`dim` from `{{ ref('dim_currencies') }}`
- [ ] Join on `stg.currency = dim.currency_code`
- [ ] 增加列 `rate_change_pct`:
  ```sql
  (rate - LAG(rate) OVER (PARTITION BY currency ORDER BY rate_date))
    / NULLIF(LAG(rate) OVER (PARTITION BY currency ORDER BY rate_date), 0)
    AS rate_change_pct
  ```
- [ ] 输出字段:`rate_date`, `currency`, `currency_name`, `rate`, `rate_change_pct`

### 7.3 `dbt_project/models/marts/_marts.yml`
- [ ] 声明两个 models,各加 description
- [ ] `dim_currencies`:
  - [ ] `currency_code`: `not_null` + `unique`
  - [ ] `currency_code`: `accepted_values` 列 `['USD','GBP','CHF','JPY','CNY']`
- [ ] `fct_daily_rates`:
  - [ ] model 级测试 `dbt_utils.unique_combination_of_columns` 用 `[rate_date, currency]`
  - [ ] `currency`: `not_null`
  - [ ] `rate`: `not_null`

### 7.4 验证 marts
- [ ] 运行 `cd dbt_project && DBT_PROFILES_DIR=. uv run dbt build`
- [ ] 所有 model 编译通过,所有 test 通过
- [ ] 用 duckdb CLI 或 python 抽查 `main.fct_daily_rates` 头 5 行,确认 `rate_change_pct` 有非空值

---

## Phase 8 — Makefile

按 spec §6 创建根目录 `Makefile`,所有 target 用 Tab 缩进(make 要求)。

- [ ] **8.1** 顶部 `.PHONY: install ingest transform test build docs deps clean reset all`
- [ ] **8.2** 在文件顶部 export `DBT_PROFILES_DIR=./dbt_project`(或在每个 target `cd dbt_project` 时让本地 profile 自动生效——二选一,简单优先)
- [ ] **8.3** target `install`: `uv sync`
- [ ] **8.4** target `deps`: `cd dbt_project && uv run dbt deps`
- [ ] **8.5** target `ingest`: `uv run python dlt_pipelines/ecb_rates.py`
- [ ] **8.6** target `transform`: `cd dbt_project && uv run dbt run`
- [ ] **8.7** target `test`: `cd dbt_project && uv run dbt test`
- [ ] **8.8** target `build`: `cd dbt_project && uv run dbt build`
- [ ] **8.9** target `docs`: `cd dbt_project && uv run dbt docs generate && uv run dbt docs serve`
- [ ] **8.10** target `all`: 依赖 `ingest build`
- [ ] **8.11** target `clean`: `rm -rf dbt_project/target dbt_project/dbt_packages dbt_project/logs`
- [ ] **8.12** target `reset`: `rm -f data/sandbox.duckdb`
- [ ] **8.13** 每个 target 注释 `## xxx`,使 `make help` 风格友好(可选)

### 8.14 Makefile 烟测
- [ ] `make clean && make reset && make install && make deps && make all` 全过
- [ ] `make test` 全绿

---

## Phase 9 — README.md

按 spec §8 撰写,**总长 ~150 行**。

- [ ] **9.1** 顶部一句话:"Learning sandbox for dlt + dbt on DuckDB. Not production."
- [ ] **9.2** Section "Architecture":ASCII 图
  ```
  Frankfurter API → dlt → DuckDB (raw_ecb schema) → dbt → DuckDB (main schema)
  ```
- [ ] **9.3** Section "Setup":三步走 `uv sync` → `make deps` → `make all`
- [ ] **9.4** Section "Project layout":粘贴 spec §3 的目录树
- [ ] **9.5** Section "What to try (learning prompts)":8 个实验,直接抄 spec §8.5 列表
- [ ] **9.6** Section "Useful DuckDB CLI commands":3-4 条
  - `duckdb data/sandbox.duckdb`
  - `SHOW TABLES;` / `SHOW TABLES FROM raw_ecb;`
  - `SELECT * FROM main.fct_daily_rates LIMIT 5;`
  - `SELECT * FROM raw_ecb._dlt_loads;`
- [ ] **9.7** Section "Links":dlt 文档、dbt 文档、Frankfurter API 文档(用 spec 中的 URL,不要自己编)
- [ ] **9.8** 整体语气:functional + direct,不写营销词,不写 "production-ready"

---

## Phase 10 — 端到端验收 (按 spec §10 Acceptance Criteria 逐条)

逐条勾选,任何一项失败就回到对应 Phase 修复。

- [x] **10.1** `uv sync` clean install,无错误
- [x] **10.2** `make deps` 安装 dbt_utils 无错误
- [x] **10.3** `make ingest` 生成 `data/sandbox.duckdb`,含 `raw_ecb.daily_rates` 与 `raw_ecb.currencies_meta`
- [x] **10.4** `daily_rates` 行数 > 100 (查询验证) — 实际 3030 行
- [x] **10.5** `make build` 同时跑通 run 与 test,全绿 (16/16 PASS)
- [ ] **10.6** `make docs` 在 http://localhost:8080 可见 lineage 图:source → staging → marts
  - 验证后用 `Ctrl-C` 退出 server
- [x] **10.7** 第二次 `make ingest` 不会让 `daily_rates` 行数翻倍 (merge 生效)
- [x] **10.8** `make reset && make all` 从干净状态跑通
- [x] **10.9** README 包含 spec §8 列出的所有 7 个 section

---

## Phase 11 — 收尾清理

- [x] **11.1** 删掉任何临时调试文件 / 注释 / `print` debug 语句
- [x] **11.2** 确认 `data/sandbox.duckdb` 没有被 git 跟踪 (`.gitignore` 生效)
- [x] **11.3** `wc -l dlt_pipelines/ecb_rates.py` = 60 行 ≤ 120 行
- [x] **11.4** SQL 文件 3 个,YAML 文件 3 个(_sources, _staging, _marts) + packages.yml
- [x] **11.5** 项目代码文件无 Iceberg / Docker / Dagster 等禁词
- [ ] **11.6** 把 task.md 中所有 `[x]` 状态 commit (若用户后续启用 git)

---

## 防误区清单 (Code Agent 务必复读)

> 出自 spec §11 + §12。任何想做这些事情的冲动,**忽略**。

- ❌ 不要加 Docker / docker-compose
- ❌ 不要加 Airflow / Dagster / Prefect
- ❌ 不要加 Iceberg / Parquet / S3 / MinIO
- ❌ 不要加 CI/CD / pre-commit / GitHub Actions
- ❌ 不要加多环境 (prod profile)
- ❌ 不要加 secrets 管理
- ❌ 不要加 LLM / AI 集成
- ❌ 不要给 dlt pipeline 加 CLI 参数 (硬编码即可,用户会改文件实验)
- ❌ 不要给 dlt pipeline 加 retry / 自定义 logging / rate limit
- ❌ 不要在 README/代码中出现 "production" / "compliance" / "enterprise" 类词

> **Spec §12 原话**: "Prioritize correctness over completeness, and completeness over polish. A working end-to-end pipeline with 3 models beats a half-finished one with 10 models."
