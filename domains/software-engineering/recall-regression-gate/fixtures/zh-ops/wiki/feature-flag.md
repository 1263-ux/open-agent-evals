---
title: 特性开关（Feature Flag）规范
type: guide
area: ops
status: active
importance: 0.7
confidence: 0.9
created: 2026-03-05T02:00:00+00:00
tags: [feature-flag, release, experiment]
pinned: false
archived: false
access_count: 0
---

# 特性开关规范

## 命名

`<domain>.<feature>.<variant>`，全小写，如 `billing.invoice_v2.treatment`。
禁止 `test1`、`temp`、`xxx_new` 这类无法追溯的名字。

## 默认值

**上线时必须默认关闭**。代码合并到主干不等于功能开启，
默认开启的开关等于没有开关。

## 灰度方式

- 按 `user_id` 哈希分桶，保证同一用户稳定命中同一档。
- 分桶比例只能单调递增，不允许从 50% 降回 10%（会造成体验抖动）。
- 面向企业客户的开关键控到租户维度，不能把同一租户的用户劈成两半。

## 生命周期

开关从创建起 **不超过 90 天**。到期前必须二选一：全量开启并删除开关代码，
或彻底下线。长期存在的开关是技术债，也是事故来源（旧分支逻辑不会被测试覆盖）。

清理责任人写在开关描述里，到期由平台组统一扫描并提醒。
