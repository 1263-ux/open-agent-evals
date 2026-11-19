# 中文集未命中分析（v1.1.0 / fts5）

55 条中 3 条 `recall_at_5 < 1.0`。以下 `retrieved` 只列前 3 条。

## 1. `zh-011` —— 中文同义词零共享词元（严重）

```
query : 客户想退钱有什么条件
gold  : refund-policy-current
got   : customer-success-playbook, cdn-cache-policy, incident-postmortem
mrr   : 0.00    recall_at_5: 0.00
```

分词证据（`knowledge_studio.recall._tokenize`）：

```
客户想退钱有什么条件 -> ['什么', '客户', '条件', '退钱']
退款政策             -> ['政策', '退款']
```

`退钱` 与 `退款` 是两个独立 token，交集为空。查询里剩下的 `客户`/`条件` 是泛词，
于是「客户成功手册」以「客户」得分最高被排到第一。

三个后端同 rank、同缺失：

| backend | top1 | mrr |
| --- | --- | --- |
| fts5 | customer-success-playbook | 0.00 |
| native | customer-success-playbook | 0.00 |
| fusion | customer-success-playbook | 0.00 |

结论：这不是排序缺陷，是**词表缺陷**。系统没有同义扩展，也没有向量兜底
（`settings/recall.yaml: embedding_fallback: false`）。

同类高风险对：报销/报帐、开票/发票、加班/值班、退款/退钱、客户/租户。

## 2. `zh-016` —— 文档词表缺口（非引擎缺陷）

```
query : 改了代码怎么逐步放量
gold  : release-train
got   : feature-flag, security-baseline
mrr   : 0.00    recall_at_5: 0.00
```

`release-train` 全文用的是「灰度档位 1% → 10% → 50% → 100%」，
从未出现「放量」二字。查询语义正确，文档没写用户会说的那个词。

这类失败不能靠改引擎修，属于**文档写作规范**问题：面向检索的文档，
应当把用户可能使用的口语说法写进正文或 `tags`。

## 3. `zh-034` —— 多跳标签偏严（保留，不改）

```
query : 发布冻结期能不能走 hotfix
gold  : release-train, oncall-escalation
got   : release-train, cdn-cache-policy, feature-flag
mrr   : 1.00    recall_at_5: 0.50
```

`release-train` 写明「hotfix 需值班经理批准」，`oncall-escalation` 定义值班经理的
权限与升级路径。要求同时召回两者是合理的，但需要读者自己把「值班经理」对上，
对纯词法检索偏严。

**保留此标签**：改成单文档会让 R@5 好看，却掩盖真实的多跳弱点。

## 附：v1.0.0 → v1.1.0 的两条标签修正

跑完 v1.0.0 后自审发现，两条黄金标签指向 `archived: true` 的文档。
`cli/knowledge_studio/search/fts5.py:543` 对归档文档有 SQL 过滤：

```sql
AND COALESCE(p.archived, 0) = 0
```

因此这些标签在物理上不可达，属于夹具错误而非引擎失败：

| case | v1.0.0 | 问题 | v1.1.0 |
| --- | --- | --- | --- |
| `zh-038` 2023 白屏原因 | `cdn-cache-legacy` | 归档，不进索引 | `cdn-cache-policy`（该文写明 2023 旧方案导致 ChunkLoadError） |
| `zh-039` v2 何时废止 | `-v2-archive` + `current` | 归档项不可达，R@5 上限 0.5 | `refund-policy-current`（正文写明 2026-09-01 废止） |

修正只改这两条，其余 53 条逐字未动；v1.0.0 原样保留。
