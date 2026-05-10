# Cron Jobs 配置示例

> 博客自动化流水线的 cron job 配置。

## 晨间选题 (08:10)

```json
{
  "name": "blog-morning-evolution",
  "schedule": {
    "kind": "cron",
    "expr": "10 8 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行晨间博客选题：1) 读 NEXT_HOOK.md 获取昨日钩子 2) 用 Tavily 扫描技术社区热点 3) 从 CONTENT_CALENDAR.md 选择主题 4) 起草 1500-2500 词初稿 5) 保存到 drafts/ 目录",
    "timeoutSeconds": 1800
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce"
  },
  "enabled": true
}
```

## 午间深挖 (13:30)

```json
{
  "name": "blog-midday-deep-dive",
  "schedule": {
    "kind": "cron",
    "expr": "30 13 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行午间深度扩展：1) 扩展晨间草稿到 2000-3000 词 2) 添加代码示例和 benchmark 数据 3) 用 web_search 核实所有数字 4) 扫描新技术趋势更新 CONTENT_CALENDAR.md",
    "timeoutSeconds": 3600
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce"
  },
  "enabled": true
}
```

## 晚间发布 (21:30)

```json
{
  "name": "blog-evening-publish",
  "schedule": {
    "kind": "cron",
    "expr": "30 21 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行晚间发布流程：1) Humanizer QC (目标 < 30/100) 2) SEO 检查 3) R2 配图 4) 发布到 WordPress (默认 draft) 5) 写入 NEXT_HOOK.md 明日钩子 6) 更新 CONTENT_CALENDAR.md",
    "timeoutSeconds": 3600
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce"
  },
  "enabled": true
}
```

## QA 审计 (10:30)

```json
{
  "name": "blog-qa-audit",
  "schedule": {
    "kind": "cron",
    "expr": "30 10 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行每日 QA 审计：1) 检查昨天发布的文章 2) 查找重复内容 3) 检查幻觉/错误 4) 检查误发布的草稿 5) 汇报结果",
    "timeoutSeconds": 1800
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce"
  },
  "enabled": true
}
```

## 股票监控 (每日收盘后)

```json
{
  "name": "stock-daily-review",
  "schedule": {
    "kind": "cron",
    "expr": "0 5 * * 2-6",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行每日股票复盘：1) 用 Yahoo Finance API 获取持仓行情 2) 计算当日盈亏 3) 检查保证金余额 4) 生成每日收益摘要 5) 如果保证金 < $2000 发送紧急通知",
    "timeoutSeconds": 900
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce"
  },
  "enabled": true
}
```

## 注意事项

1. **时区**：所有 cron 表达式都用 `Asia/Shanghai` 时区
2. **隔离执行**：所有任务都用 `isolated` session，不污染主会话
3. **超时**：复杂任务设 3600 秒，简单任务设 900-1800 秒
4. **交付**：`announce` 模式会把结果发送到聊天频道
5. **禁用**：临时不需要的任务设 `enabled: false`，不要删除
