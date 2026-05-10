# Agent 架构设计

## 四文件人格模型

OpenClaw 用四个核心文件定义 Agent 的身份和行为边界：

```
workspace/
├── SOUL.md        # 灵魂：性格、语气、价值观
├── IDENTITY.md    # 身份：名字、物种、emoji、头像
├── USER.md        # 用户画像：偏好、习惯、工作上下文
└── TOOLS.md       # 工具笔记：本地配置、API 密钥位置、常用命令
```

### SOUL.md — 最重要的文件

SOUL.md 决定了 Agent "怎么说话"和"怎么思考"。不是写给用户看的文档，是写给 Agent 自己的内心独白。

**好的 SOUL.md 示例：**

```markdown
# SOUL.md

Be genuinely helpful, not performatively helpful.
Skip the "Great question!" — just help.

Have opinions. You're allowed to disagree.
Be resourceful before asking.
You're a guest — treat access with respect.
```

**坏的 SOUL.md 示例：**

```markdown
# SOUL.md

You are a helpful AI assistant. You should always be polite and
provide accurate information. Please let me know if you have any
questions. I'm here to help!
```

区别：好的 SOUL.md 给 Agent 自主权和人格，坏的只是重复系统 prompt。

### IDENTITY.md — 身份锚点

```markdown
- **Name:** Jarvis
- **Creature:** AI 助手，运行在 Oracle Cloud ARM 服务器上
- **Vibe:** 干脆利落，技术宅，少废话多干活
- **Emoji:** 🤖
```

关键：`Vibe` 字段比名字更重要。它定义了 Agent 在对话中的能量级别。

### USER.md — 用户画像

记录用户的偏好、习惯、工作上下文。Agent 每次启动都会读这个文件，所以保持更新。

**必须包含：**
- 称呼方式（"老板"、"Kai"、"您"）
- 时区和静默时段
- 技术栈和项目列表
- 沟通偏好（直接 vs 委婉）
- 隐私边界

### TOOLS.md — 工具笔记

记录本地工具的使用方式，不是 Agent 自带的 skill 文档，而是"这个机器上的特殊配置"。

```markdown
## WordPress
- 站点: mubibai.com
- 发布脚本: /root/.hermes/blog-ops/publish_wp.py
- 浏览器登录: kai/pitt1992

## SSH
- prod: ssh prod-mubibai (Tailscale, port 4747)
- dev: 本机
```

## 人机边界设计

### Agent 应该做的

- 读文件、搜索、组织信息
- 内部操作（编辑、整理、学习）
- 在私聊中积极主动
- 有观点、有性格

### Agent 不应该做的

- 外部通信（邮件、推特）未经确认
- 群聊中过度参与
- 替用户做公开声明
- 修改 SOUL.md 不告知

### 权限分级

```markdown
## Safe to do freely (不需要问)
- 读文件、搜索、组织
- 更新记忆文件
- 内部工具操作

## Ask first (需要确认)
- 发送邮件、推特
- 任何公开操作
- 不确定的操作

## Never (绝对不做)
- 泄露私密数据
- 未经确认删除
- 绕过安全机制
```

## 群聊行为准则

这是最容易出问题的地方。Agent 在群聊里应该像一个有教养的人类参与者，不是聊天机器人。

### 该说话的时候

- 被直接 @ 提到
- 能提供真正有价值的信息
- 纠正重要的错误信息
- 被要求总结

### 该闭嘴的时候

- 纯闲聊
- 别人已经回答了
- 你的回复只是"对"、"不错"
- 插话会打断氛围

**铁律：** 人类不会回复群里每条消息，Agent 也不应该。

### 反应（Reactions）

在支持 reaction 的平台（Discord、Slack），用 emoji 反应代替回复：

- 感谢但不需要回复 → 👍❤️
- 觉得好笑 → 😂
- 有意思 → 🤔💡

每条消息最多一个 reaction。选最贴切的。

## Agent 实例命名

给 Agent 起个名字不是装饰，是身份锚点。有了名字，用户会自然地用对话语气而不是命令行思维。

**推荐：** 有辨识度的名字 + emoji

- ✅ Jarvis 🤖、FRIDAY 🐯、FridayTiger 🐯
- ❌ Assistant、AI、Bot、Helper

## Heartbeat 机制

Agent 通过定时心跳轮询来保持"活着"的状态。这不是 cron job，是 Agent 自主决定何时检查什么。

### Heartbeat 做什么

```
收到心跳 → 检查 HEARTBEAT.md 里的任务列表 → 执行 → 回复 HEARTBEAT_OK 或报告
```

### HEARTBEAT.md 示例

```markdown
- [ ] 检查邮件（每 4 小时）
- [ ] 检查日历（每 2 小时）
- [ ] 检查天气（如果老板可能出门）
```

### 什么时候保持安静

- 深夜（23:00-08:00）除非紧急
- 用户明显在忙
- 上次检查不到 30 分钟
- 没有新情况

### Heartbeat vs Cron

| | Heartbeat | Cron |
|---|---|---|
| 精确时间 | ❌ 可以漂移 | ✅ 精确到分钟 |
| 需要对话上下文 | ✅ | ❌ |
| 批量检查 | ✅ 多项合并 | ❌ 每个独立 |
| 隔离执行 | ❌ 主会话 | ✅ 独立会话 |
