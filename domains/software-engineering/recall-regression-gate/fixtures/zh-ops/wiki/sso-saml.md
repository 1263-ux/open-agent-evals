---
title: 单点登录（SSO / SAML / OIDC）接入
type: guide
area: ops
status: active
importance: 0.7
confidence: 0.9
created: 2026-07-21T02:00:00+00:00
tags: [sso, saml, oidc, scim, identity]
pinned: false
archived: false
access_count: 0
---

# 单点登录接入

## 支持协议

- **SAML 2.0**：主流企业 IdP（ADFS、Azure AD、Okta、飞书企业版）均支持。
- **OIDC**：适合自建 IdP，需提供 discovery 地址。

## 接入步骤

1. 客户提供 IdP 元数据（SAML）或 client_id / client_secret / issuer（OIDC）。
2. 我方生成 SP 元数据或回调地址，客户在 IdP 侧登记。
3. 配置属性映射：`email` 必填且唯一，`name`、`department` 可选。
4. 开启 SCIM 2.0 用户同步（可选但强烈建议），否则离职用户不会自动停用。
5. 用测试账号完成一次登录、一次登出、一次属性变更验证。

## 常见问题

- **登录后回到登录页**：多为时钟偏移超过 5 分钟，SAML 断言失效。
- **用户重复创建**：`email` 大小写不一致或带了空格，映射前需 lowercase + trim。
- **SCIM 同步不全**：IdP 侧只推送了已分配应用的用户，需在 IdP 检查 assignment。

## 安全要求

必须开启签名校验，禁止 `wantAssertionsSigned=false`。
生产环境不允许使用自签证书，证书到期前 30 天需更换并同步元数据。
