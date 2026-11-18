# 数据获取与校验

本包**不内置**数据集。LoCoMo 属第三方素材，仓库许可策略未定，因此只记录获取方式与校验值。

## LoCoMo

- 论文：Maharana et al., *Evaluating Very Long-Term Conversational Memory of LLM Agents*, ACL 2024
- 仓库：`snap-research/locomo`
- 本实验实际使用的文件：`locomo10.json`
- 大小：约 2.8 MB
- sha256：`553cd5a15e25f2ceccc6ed185221eba645080c93e5b91087560a91aa5961f365`

```bash
sha256sum locomo10.json   # Windows: certutil -hashfile locomo10.json SHA256
```

## 评测集

由 `locomo10.json` 转换生成（conversation → wiki 页面，qa → case）。本实验使用的评测集：

- 文件：`locomo-eval.yaml`（1540 case，已排除 adversarial 类型）
- sha256：`c00ce960f18ab778f7e4202ba90e75dae7ffc1e12f62e072a6216ea06ca757ff`

转换脚本由执行方提供，必须固定版本；转换后先校验上面的 sha256，再开始基线运行。

## 为什么没有 fixtures 目录

把转换产物直接放进本包，等于转发第三方数据的衍生内容。许可未清前，本包只保留"如何得到同一份输入"的说明。等许可策略确定后，再决定是否内置。

## 已知缺口

- 转换脚本未随包分发；不同实现可能生成不同 slug，导致指标不可比。
- 除 fts5 之外的 backend（native / fusion）未纳入本包阈值。
