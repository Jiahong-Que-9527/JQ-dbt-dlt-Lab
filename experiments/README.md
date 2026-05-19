# Experiments

按编号顺序做完，你应该能在生产环境里熟练使用 dlt + dbt。

## 怎么开始 / 怎么收尾

环境拉起、JupyterLab 启动、DuckDB 文件锁、清理重置等流程都在项目根的 [../README.md](../README.md) 里：

- **拉起环境**：[../README.md#快速开始拉起环境](../README.md#快速开始拉起环境)
- **做实验的工作流**：[../README.md#做实验的工作流](../README.md#做实验的工作流)
- **关闭与清理环境**：[../README.md#关闭与清理环境](../README.md#关闭与清理环境)
- **故障排查**：[../README.md#常见故障排查](../README.md#常见故障排查)

最短路径：

```bash
make all      # 第一次拉起：装依赖 + ingest + dbt build
make lab      # 开 JupyterLab 在 http://localhost:8888
# ……做实验……
# 关 lab：跑 lab 的终端按 Ctrl-C 两次
make clean    # 清 dbt 产物（可选）
make reset    # 删 DuckDB 文件，回到出厂（可选）
```

## 跑实验前的检查

1. 已经跑过一次 `make all`（确保有基础数据）
2. 没有别的进程占着 `data/sandbox.duckdb`（避免 DuckDB 文件锁）
3. 当前目录在项目根（或 notebook 里用了 `cwd='..'` / `'../...'` 的相对路径）

## 实验之间的依赖

- 强烈建议 **01 → 26 顺序**做。
- 实验 16（snapshot）、17（seed）、19（custom test）会留下产物（`snapshots.snp_currencies`、`main.currency_regions`、audit 表等），是预期的。
- 实验 09（incremental cursor）、12（nested JSON）、14（filesystem）会建独立 schema，不污染 main。
- 实验 19/22/24/26 会**临时改文件再还原**。每个这种实验最后都有清理 cell——务必运行。忘了的话用 `git status` 和 `git checkout -- <file>` 复原。

## 学习路径

### 一、入门概念（01–08）

| Notebook | 主题 |
|---|---|
| [01_merge_disposition.ipynb](01_merge_disposition.ipynb) | dlt merge vs replace |
| [02_dbt_type_change.ipynb](02_dbt_type_change.ipynb) | dbt view vs table 物化 |
| [03_schema_evolution.ipynb](03_schema_evolution.ipynb) | dlt 自动 schema 演化 |
| [04_dbt_lineage_docs.ipynb](04_dbt_lineage_docs.ipynb) | dbt manifest 与 lineage |
| [05_break_a_test.ipynb](05_break_a_test.ipynb) | dbt test 失败诊断 |
| [06_incremental_model.ipynb](06_incremental_model.ipynb) | dbt incremental 入门 |
| [07_dlt_metadata.ipynb](07_dlt_metadata.ipynb) | dlt 内部 metadata 表 |
| [08_dlt_pipeline_show.ipynb](08_dlt_pipeline_show.ipynb) | dlt CLI / pipeline state |

### 二、dlt 生产能力（09–15）

| Notebook | 主题 | 解决什么生产问题 |
|---|---|---|
| [09_dlt_incremental_cursor.ipynb](09_dlt_incremental_cursor.ipynb) | `dlt.sources.incremental` 游标 | 不重拉全量、不被 API 限流 |
| [10_dlt_schema_contract.ipynb](10_dlt_schema_contract.ipynb) | schema contract + 列类型 hints | 上游 schema drift 治理 |
| [11_dlt_secrets_config.ipynb](11_dlt_secrets_config.ipynb) | secrets / config 三层管理 | 不把密钥写进代码、CI 注入凭证 |
| [12_dlt_nested_json.ipynb](12_dlt_nested_json.ipynb) | 嵌套 JSON 自动展开 | REST/event 数据落库 |
| [13_dlt_testing.ipynb](13_dlt_testing.ipynb) | pytest dlt pipeline | 让 ingestion 进 CI |
| [14_dlt_filesystem_parquet.ipynb](14_dlt_filesystem_parquet.ipynb) | filesystem destination | lakehouse staging |
| [15_dlt_dbt_integration.ipynb](15_dlt_dbt_integration.ipynb) | dlt + dbt 串成端到端 | 一个脚本跑完 EL+T |

### 三、dbt 生产能力（16–25）

| Notebook | 主题 | 解决什么生产问题 |
|---|---|---|
| [16_dbt_snapshot_scd2.ipynb](16_dbt_snapshot_scd2.ipynb) | snapshot / SCD2 | 维度历史不丢 |
| [17_dbt_seeds.ipynb](17_dbt_seeds.ipynb) | seed 参考数据 | 版本化的小映射表 |
| [18_dbt_jinja_macros.ipynb](18_dbt_jinja_macros.ipynb) | Jinja + 自定义 macro | 复用 SQL 片段、env-aware |
| [19_dbt_custom_tests.ipynb](19_dbt_custom_tests.ipynb) | singular + generic test | 业务不变量入测试 |
| [20_dbt_source_freshness.ipynb](20_dbt_source_freshness.ipynb) | source freshness | 上游停了能报警 |
| [21_dbt_hooks.ipynb](21_dbt_hooks.ipynb) | pre/post + on-run-end hooks | grants、audit 表、监控 |
| [22_dbt_selectors_defer.ipynb](22_dbt_selectors_defer.ipynb) | selector 语法 + `--defer --state` | slim CI 省钱省时间 |
| [23_dbt_incremental_strategies.ipynb](23_dbt_incremental_strategies.ipynb) | 4 种 incremental_strategy | 大表增量正确性 |
| [24_dbt_multi_target.ipynb](24_dbt_multi_target.ipynb) | 多 target + env-aware | dev / ci / prod 分隔 |
| [25_dbt_utils_in_practice.ipynb](25_dbt_utils_in_practice.ipynb) | dbt_utils 常用宏 | 代理键、date_spine、pivot |

### 四、整体工作流（26）

| Notebook | 主题 |
|---|---|
| [26_orchestration_ci.ipynb](26_orchestration_ci.ipynb) | 端到端 orchestration + slim CI 演练 |
