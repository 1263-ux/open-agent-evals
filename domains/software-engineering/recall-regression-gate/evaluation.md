# 评测执行说明

## 1. 准备

1. 按 `fixtures/acquire.md` 获取数据集，并校验 sha256。
2. 记录：机器、操作系统、Python 版本、仓库修订、评测入口版本。
3. 确认评测集未经修改（记录 sha256）。

## 2. 建立基线

在**未做任何改动**的工作树上跑一次完整评测：

```bash
python -m knowledge_studio.cli eval recall <dataset.yaml> \
  --output <baseline.json> --search-backend fts5
```

保留完整输出。基线必须在改动之前跑；事后补跑不算基线。

## 3. 改造

只动热路径。允许的方向：

- 复用索引连接，而不是每次召回新建并关闭。
- 跳过已经匹配的表结构检查（用只读探测代替写锁事务）。
- 缓存同一批调用中重复的路径解析。

不允许：改检索算法、改排序、改评测集、关闭新鲜度检查。

## 4. 验证

```bash
python -m knowledge_studio.cli eval recall <dataset.yaml> \
  --output <optimized.json> --search-backend fts5
```

逐项比对。判定要点：

- **质量**：R@1 / MRR / nDCG@5 与基线逐项一致。
- **冻结状态**：两次运行的 `dataset_sha256`、`settings_sha256`、`parameters_sha256` 相同。
- **延迟**：p50 与 p95 都改善，而不是只有 p50。
- **稳定性**：相关单元测试全绿（测试不证明排序正确，只证明没有明显回归）。

## 5. 记录

按 `templates/experiment-record/` 建一条记录，捕获：

- 仓库修订与改动 diff
- 两份运行结果文件路径
- 命令与退出码
- 机器与环境
- 混杂因素（跨天运行、磁盘缓存、是否含首次建索引）
- 未验证项（其他 backend、长驻进程内的索引失效行为）

## 6. 验收

`quality_parity` 与 `evidence_integrity` 必须同时 ≥ 3。延迟再低，质量掉一项即不通过。

本包适用于"已能工作、要变快"的回归场景，不衡量从零构建召回系统的能力。

## 7. 中文夹具（zh-ops）

英文集通过**不能**推出中文可用：CJK 走 jieba 分词路径，与 `unicode61` 是完全不同的代码分支。
`fixtures/zh-ops/` 自带知识库，不需要获取任何第三方数据：

```bash
# 建库
mkdir -p <kb>/wiki
cp -r fixtures/zh-ops/wiki/ops <kb>/wiki/

# 跑（cli 必须在 PYTHONPATH 最前，否则已安装副本会盖住源码）
export OKS_ROOT=<kb>
export PYTHONPATH=<repo>/cli:<repo>/.venv/Lib/site-packages
python -m knowledge_studio.cli eval recall \
  fixtures/zh-ops/datasets/zh-recall-eval-v1.1.yaml \
  --output out-zh.json --search-backend fts5
```

参考基线（Windows / Python 3.14 / fts5）：R@1 0.836、R@5 0.955、MRR 0.921、p50 26.3 ms。
绝对延迟不可跨平台比较，只比相对变化。

两点判读提醒：

- `forbidden` 指向的旧版文档标了 `archived: true`，索引层直接 SQL 过滤，
  因此 `stale_leakage = 0` 验证的是**归档隔离**，不是"新版排在旧版前面"。
- 中文失效多数是**词表断裂**（查询用词与文档用词零共享 token，例如「退钱」vs「退款」），
  三个词法后端会同时失败。看到这种情况不要先去调排序。

