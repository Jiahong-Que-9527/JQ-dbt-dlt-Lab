# Experiments

每个 notebook 对应 README 里一条 "What to try" 学习实验。

| Notebook | 实验内容 | 前提 |
|---|---|---|
| [01_merge_disposition.ipynb](01_merge_disposition.ipynb) | merge vs replace disposition，观察重复 ingest 的行为 | `make ingest` |
| [02_dbt_type_change.ipynb](02_dbt_type_change.ipynb) | 修改 stg 列类型，观察 view/table 的响应差异 | `make build` |
| [03_schema_evolution.ipynb](03_schema_evolution.ipynb) | 新增货币 AUD，观察 dlt schema 自动演化 | `make ingest` |
| [04_dbt_lineage_docs.ipynb](04_dbt_lineage_docs.ipynb) | 用代码读 manifest，理解模型依赖图 | `make build` |
| [05_break_a_test.ipynb](05_break_a_test.ipynb) | 故意破坏 accepted_values test，分析 dbt 失败输出 | `make build` |
| [06_incremental_model.ipynb](06_incremental_model.ipynb) | 把 table 改为 incremental，对比编译后的 SQL | `make build` |
| [07_dlt_metadata.ipynb](07_dlt_metadata.ipynb) | 深入 `_dlt_loads`、`_dlt_id` 等内部表 | `make ingest` |
| [08_dlt_pipeline_show.ipynb](08_dlt_pipeline_show.ipynb) | dlt CLI 查看 pipeline trace 和 state | `make ingest` |

## 启动 JupyterLab

```bash
make lab
```

然后打开 http://localhost:8888，进入 `experiments/` 目录。
