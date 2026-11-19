---
title: API 限流与配额
type: guide
area: ops
status: active
importance: 0.75
confidence: 0.9
created: 2026-06-09T02:00:00+00:00
tags: [api, rate-limit, quota, gateway]
pinned: false
archived: false
access_count: 0
---

# API 限流与配额

## 默认限制

- 每租户默认 **100 QPS**，允许突发到 200 QPS，令牌桶容量 200。
- 单 IP 额外限制 300 QPS，防止单点打爆。
- 批量接口（如批量创建）单独配额：每分钟 60 次，不计入 QPS。

## 超限行为

返回 `429 Too Many Requests`，响应头带 `Retry-After`（秒）。
连续 5 分钟超限会触发告警给客户成功，连续 30 分钟超限可能被降级到 20 QPS。

## 提额

提交工单说明业务场景、峰值 QPS、调用来源。超过 500 QPS 需附压测报告，
由平台组评估后再调整。提额不改变 SLA 承诺。

## 排查

客户反馈「偶发 429」时，先看是否集中在整点（定时任务撞车），
再看是否单 IP 高频（未做连接池复用），最后看是否批量接口与普通接口混用。
