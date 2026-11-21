---
title: CDN 缓存旧方案（已下线）
type: guide
area: ops
status: deprecated
importance: 0.2
confidence: 0.5
created: 2023-06-02T02:00:00+00:00
tags: [cdn, cache, legacy]
pinned: false
archived: true
access_count: 0
---

# CDN 缓存旧方案（2023，已下线）

> 已由 2026 年的新策略取代。本页保留用于解释历史故障，**不要按此配置**。

## 当时的配置

- 全部资源统一 `max-age=600`（10 分钟），包括 HTML。
- 刷新靠发布脚本调用刷新接口，一次最多 20 个 URL。
- 图片未单独设置，跟随全局 10 分钟。

## 导致的问题

1. 发布后 10 分钟内用户拿到旧 HTML，引用已删除的 chunk，白屏。
2. 刷新接口限额太低，每次发布要手工分 8 批。
3. 图片频繁回源，回源带宽成本高出 3 倍。

## 结论

缓存粒度必须按资源类型区分；入口 HTML 绝不能有强缓存。
