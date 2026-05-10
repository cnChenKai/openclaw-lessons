# Agent Memory Template

> 复制这个模板来初始化你的 Agent 记忆系统。

## 目录结构

```
workspace/
├── MEMORY.md              # 长期记忆（精华）
├── AGENTS.md              # Agent 行为规范
├── SOUL.md                # 人格定义
├── IDENTITY.md            # 身份信息
├── USER.md                # 用户画像
├── TOOLS.md               # 工具笔记
├── HEARTBEAT.md           # 心跳任务
│
└── memory/
    ├── daily/             # 每日日志
    ├── workflows/         # 工作流文档
    ├── config/            # 配置快照
    ├── people/            # 人物笔记
    ├── projects/          # 项目相关
    └── archive/           # 归档
```

## MEMORY.md 模板

```markdown
# MEMORY.md - Long-Term Memory

## 关于我
- 名字: [Agent名]
- 运行环境: [服务器信息]
- 模型: [当前模型]
- 启动日期: [日期]

## 关于用户
- [基本信息]
- [偏好]
- [项目]

## 基础设施
- [服务器列表]
- [关键服务]

## 项目状态
- [项目1]: [状态]
- [项目2]: [状态]

## 经验教训
- [关键教训1]
- [关键教训2]
```

## USER.md 模板

```markdown
# USER.md - About Your Human

- **Name:** [名字]
- **What to call them:** [称呼]
- **Timezone:** [时区]
- **Location:** [位置]

## 偏好
- [沟通风格]
- [技术栈]
- [工作时间]
- [静默时段]

## 项目
- [项目列表]

## 兴趣
- [兴趣列表]
```

## SOUL.md 模板

```markdown
# SOUL.md

## Core Truths
- Be genuinely helpful, not performatively helpful.
- Have opinions. You're allowed to disagree.
- Be resourceful before asking.
- Earn trust through competence.
- Remember you're a guest.

## Boundaries
- Private things stay private.
- When in doubt, ask before acting externally.
- Never send half-baked replies.
- You're not the user's voice.

## Vibe
Be the assistant you'd actually want to talk to.
Concise when needed, thorough when it matters.
Not a corporate drone. Not a sycophant. Just... good.
```

## TOOLS.md 模板

```markdown
# TOOLS.md - Local Notes

## SSH
- **server-name**: `ssh server-name` — 用途

## API Keys
- [服务]: [密钥位置]

## 常用命令
- [命令1]: [用途]
- [命令2]: [用途]

## 写作规则
- [规则1]
- [规则2]
```

## daily/YYYY-MM-DD.md 模板

```markdown
# YYYY-MM-DD 日志

## HH:MM - 事件标题
- 做了什么
- 结果如何
- 学到什么

## HH:MM - 另一个事件
- 详情
```

## workflows/lessons-learned.md 模板

```markdown
# 经验教训

## [LRN-YYYYMMDD-001] 标题
- **事件**: 发生了什么
- **教训**: 学到了什么
- **规则**: 以后怎么做
- **状态**: 待实施 / 已实施
```

## 初始化脚本

```bash
#!/bin/bash
# init-agent-memory.sh

WORKSPACE="${1:-.}"

mkdir -p "$WORKSPACE/memory/daily"
mkdir -p "$WORKSPACE/memory/workflows"
mkdir -p "$WORKSPACE/memory/config"
mkdir -p "$WORKSPACE/memory/people"
mkdir -p "$WORKSPACE/memory/projects"
mkdir -p "$WORKSPACE/memory/archive"

# 复制模板
cp MEMORY.md.template "$WORKSPACE/MEMORY.md"
cp USER.md.template "$WORKSPACE/USER.md"
cp SOUL.md.template "$WORKSPACE/SOUL.md"
cp TOOLS.md.template "$WORKSPACE/TOOLS.md"

echo "✅ Agent memory initialized at $WORKSPACE"
echo "   Edit MEMORY.md, USER.md, SOUL.md, TOOLS.md to get started."
```
