# zh-ops —— 自带知识库的中文召回夹具

## 为什么有这个夹具

本 pack 的第一份实验用的是 LoCoMo 英文数据集：它是第三方素材，不能随包分发，
且**英文召回通过不能推出中文可用**（CJK 走 jieba 分词路径，与 unicode61 完全不同的代码分支）。

`zh-ops` 的作用是让中文召回**开箱可跑、可复核**：

- 文档与查询都是为本 pack 自撰，不含第三方内容，可随包分发。
- 19 篇文档 104 KB，一个 `cp` 就能建库，不需要网络、不需要授权。
- 中文语料里最容易出问题的结构都被刻意做进去了（见下）。

## 结构

```
wiki/            19 篇运营/支持类知识库文档（虚构 SaaS 公司）
datasets/
  zh-recall-eval-v1.0.yaml   55 case，审计前原样保留
  zh-recall-eval-v1.1.yaml   55 case，修正两条不可达标签（推荐用这个）
```

`wiki/` 比 `datasets/` 高一层的原因是：OKS 的 KB 根要求 `wiki/<area>/<slug>.md`，
评测时把 `wiki/` 整个拷到 KB 根即可，slug 即文件名主干。

## 三类刻意结构

| 结构 | 文档 | 用来测什么 |
| --- | --- | --- |
| 现行版 + 已废止旧版 | `refund-policy-current` / `-v2-archive`；`cdn-cache-policy` / `-legacy` | 旧版标 `archived: true`，作为 `forbidden` 目标；实际验证的是**归档隔离**，不是排序 |
| 同主题不同答案 | `data-export`（导出日志 180 天）vs `security-baseline`（审计日志 180 天） | 真实竞争文档，避免"一查就中" |
| 噪声文档 | `weekly-ops-sync-notes`（周会纪要） | 大量无关决议与高频套话，检验查询不被带跑 |

## 55 条查询的类别分布

| topic_id | 条数 | 说明 |
| --- | --- | --- |
| `zh-literal` | 10 | 与文档用词基本一致 |
| `zh-paraphrase` | 10 | 换说法，仍需词表有交集 |
| `zh-colloquial` | 8 | 口语、缩略（"用了半还能退吗"） |
| `zh-multihop` | 6 | 需要两篇文档 |
| `zh-temporal` | 5 | 版本与时间边界 |
| `zh-stale` | 5 | 带 `forbidden`（旧版） |
| `zh-mixed` | 6 | 中英混合（SAML / SCIM / Retry-After） |
| `zh-distractor` | 5 | 答案埋在噪声文档里 |

## 已知结果（OKS，Windows，Python 3.14，fts5）

55 case，v1.1.0：

| backend | R@1 | R@5 | MRR | nDCG@5 | p50 | p95 |
| --- | --- | --- | --- | --- | --- | --- |
| fts5 | 0.8364 | 0.9545 | 0.9212 | 0.9223 | 26.3ms | 37.7ms |
| native | 0.8000 | 0.9455 | 0.9000 | 0.9022 | 39.0ms | 55.5ms |
| fusion | 0.8364 | 0.9455 | 0.9212 | 0.9180 | 56.8ms | 82.9ms |

三条未命中及其成因见 `../../experiments/exp-20261119-oks-zh-recall/`。
绝对延迟不可跨平台比较。

## 校验值

改动任何文档都会让下列 sha256 变化，据此判断夹具是否被改过：

```
00442cbf2e9ca41a  datasets/zh-recall-eval-v1.1.yaml  8961
0feb0cffed41fbdd  datasets/zh-recall-eval-v1.0.yaml  8566
9670f01ac54b7afe  wiki/api-rate-limit.md  1064
e659718d0af34025  wiki/cdn-cache-legacy.md  909
2e41cd462e522f40  wiki/cdn-cache-policy.md  1399
01e18389cf588e64  wiki/customer-onboarding-checklist.md  1475
a8ed29b9a47d92c6  wiki/customer-success-playbook.md  1496
6dff956e816d4af3  wiki/customer-tier-sla.md  1166
ece43fe09507fba2  wiki/data-export.md  1275
c90290ed193f43d7  wiki/expense-reimbursement.md  1380
0c4932df238d62e7  wiki/feature-flag.md  1175
a5e38add6790a944  wiki/incident-postmortem.md  1614
5417940560905423  wiki/invoice-issuance.md  1377
8ecb76eb5a661dd4  wiki/oncall-escalation.md  1557
98fd6a35dbf43df6  wiki/refund-policy-current.md  1761
aa9b6dcd0380e4ad  wiki/refund-policy-v2-archive.md  836
e01b812476a53337  wiki/release-train.md  1240
48d2291ebb17657a  wiki/security-baseline.md  1207
547bf30d9d0b731a  wiki/sla-credit.md  1132
f6add4e87d693123  wiki/sso-saml.md  1383
64b3a2015e9f6a28  wiki/weekly-ops-sync-notes.md  1546
```

（截断为 16 位十六进制，用于发现意外改动；防篡改请用完整值。）

## 标注方法

标签在任何一次运行**之前**写定，没有按引擎输出回调。跑完后做过一轮标签自审，
发现两条黄金标签指向 `archived` 文档（不可能被索引），据此出 v1.1.0，
两条修正逐条记录在 `../../experiments/exp-20261119-oks-zh-recall/experiment.yaml`。
v1.0.0 保留不删，两版并存以便看到审计前后的差别。

## 许可

自撰内容，随本 pack 以 CC BY 4.0 提供。文中公司、人名、金额均为虚构。
