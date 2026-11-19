---
title: CDN 缓存策略（当前）
type: guide
area: ops
status: active
importance: 0.8
confidence: 0.9
created: 2026-05-14T02:00:00+00:00
tags: [cdn, cache, performance, frontend]
pinned: false
archived: false
access_count: 0
---

# CDN 缓存策略

## 按资源类型的缓存头

| 资源 | Cache-Control | 说明 |
| --- | --- | --- |
| 带 hash 的 JS/CSS | `public, max-age=31536000, immutable` | 文件名变则内容变，可永久缓存 |
| 图片、字体 | `public, max-age=604800` | 7 天，靠刷新兜底 |
| HTML 入口 | `no-cache` | 必须回源校验，否则发布后用户看到旧版本 |
| API 响应 | `no-store` | 一律不缓存 |

## 为什么 HTML 不能缓存

2023 年旧方案给 HTML 设了 10 分钟缓存，导致每次发布后最长 10 分钟内
用户仍在加载旧的 JS 引用，前端报 `ChunkLoadError`。改为 `no-cache` 后问题消失。
旧方案见「CDN 缓存旧方案（已下线）」，不要照抄。

## 刷新与预热

- 刷新 API 单次最多 **100 个 URL**，超过需分批。
- 目录刷新按前缀，一天限 20 次，慎用。
- 大促或发布会提前 1 小时预热核心静态资源，预热失败不阻塞发布但要记录。

## 常见问题

用户反馈「改了没生效」：先确认资源是否带 hash、HTML 是否被浏览器强缓存，
再查 CDN 边缘节点命中率。不要第一反应就全站刷新。
