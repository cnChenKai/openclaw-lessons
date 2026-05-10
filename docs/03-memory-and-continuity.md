# 记忆系统与连续性

> AI Agent 每次启动都是白纸。记忆系统是它唯一的连续性。

## 分层记忆架构

```
workspace/
├── MEMORY.md              # 长期记忆（精华，手动维护）
├── HEARTBEAT.md           # 心跳任务清单
│
└── memory/
    ├── daily/             # 每日日志（原始记录）
    │   ├── 2026-05-05.md
    │   └── 2026-05-06.md
    │
    ├── workflows/         # 工作流文档
    │   ├── blog-pipeline.md
    │   ├── stock-monitor.md
    │   ├── lessons-learned.md
    │   └── skill-audit.md
    │
    ├── config/            # 配置变更历史
    │   ├── dn42-config.md
    │   └── hermes-credentials-backup.md
    │
    ├── people/            # 人物笔记
    │
    ├── projects/          # 项目相关
    │
    └── archive/           # 归档
        └── hermes-memories/
```

## 各层职责

### MEMORY.md — 长期记忆

**定位：** 人类的"长期记忆"，经过筛选和蒸馏的精华。

**规则：**
- 只在主会话（私聊）中加载
- 不在群聊、共享上下文中暴露（安全考虑）
- 定期从 daily 文件中提炼更新
- 删除过时信息

**内容：**
- 关键基础设施信息
- 项目状态概览
- 重要决策和原因
- 经验教训摘要

**反模式：**
- ❌ 把 daily 日志全量复制进来
- ❌ 记录临时性信息
- ❌ 保留已过时的配置

### daily/ — 每日日志

**定位：** 原始操作记录，像实验室笔记本。

**格式：**
```markdown
# 2026-05-05 日志

## 19:07 - 模型配置修正
- 修正 mimo-v2.5-pro 的 maxTokens (4096→131072)

## 20:50 - 完整迁移
- SSH 连接 prod.mubibai.com:4747 建立
- Skills: 70 个 SKILL.md 导入
```

**关键：** daily 文件不需要完美，但必须及时。想到什么记什么。

### workflows/ — 工作流文档

**定位：** 持久的操作手册，不随时间过时。

**示例：**
- 博客发布流程
- 股票监控规则
- Skill 审计结果
- 经验教训合集

### config/ — 配置变更

**定位：** 基础设施配置的快照，用于恢复和参考。

## 记忆维护周期

### 每天

1. 写入 `daily/YYYY-MM-DD.md`（自动或手动）
2. 重要事件同步更新 MEMORY.md

### 每周

1. 回顾本周 daily 文件
2. 提炼有价值的信息到 MEMORY.md
3. 删除 MEMORY.md 中过时的内容

### 每月

1. 归档旧的 daily 文件
2. 更新 workflows/ 文档
3. 检查 config/ 是否需要更新

## 从 daily 到 MEMORY.md 的蒸馏

```markdown
# daily/2026-05-05.md (原始)
## 22:00 - Skill 审计 + 依赖安装
- 66 个 skill 逐个过了一遍
- 安装的依赖: apt: jq, pandoc, gh, libpango...
- 最终精简: 16 个 active，50 个 archived

# MEMORY.md (蒸馏后)
### Skill 管理
- 16 个 active skill，50 个 archived
- 依赖: jq, pandoc, gh, dotnet 8.0, playwright
- 审计报告: memory/workflows/skill-audit.md
```

蒸馏的原则：保留结论，省略过程。

## 安全考量

### MEMORY.md 的访问控制

```
主会话（私聊） → ✅ 加载 MEMORY.md
群聊           → ❌ 不加载
共享上下文     → ❌ 不加载
子 Agent       → ⚠️ 按需加载，脱敏
```

### 凭据管理

凭据不存 MEMORY.md，存 `.env` 文件。MEMORY.md 只记录"凭据在哪里"。

```markdown
# ✅ 正确
- WordPress 凭据: blog-ops/.env

# ❌ 错误
- WordPress 密码: pitt1992
```

## 实例迁移时的记忆处理

迁移不是简单复制文件，需要：

1. **通读所有文件** — 理解上下文
2. **分类** — 有价值 / 已过时 / 重复
3. **去重** — 与目标实例已有信息比对
4. **蒸馏** — 只导入精华
5. **归档** — 原始文件保留但不导入

**数据：** 82 个 Hermes 记忆文件 → 28 个有价值提取 → 3 个新文件 + 1 个更新

详见 [实例迁移手册](05-migration-playbook.md)。

## Agent 自主记忆管理

### 什么时候写

- 用户说"记住这个"
- 学到了新教训
- 做了重要决策
- 发现了新信息

### 什么时候不写

- 临时性对话
- 不确定的信息
- 对方要求保密的内容

### 记忆回顾

Agent 在心跳期间可以自主回顾和整理记忆：

```markdown
## Heartbeat 记忆维护
1. 读最近的 daily 文件
2. 识别值得长期保留的信息
3. 更新 MEMORY.md
4. 删除过时内容
```

这就像人类回顾日记并更新心智模型的过程。

## 反模式

### 1. 记忆过载

```markdown
# ❌ MEMORY.md 里塞了 500 行
# 大部分是过时的配置和临时笔记
```

**解决：** 定期清理，MEMORY.md 应该在 100 行以内。

### 2. 只写不读

```markdown
# ❌ 每天写 daily 文件，但从不回顾
# 结果同样的错误反复犯
```

**解决：** 设定每周回顾周期。

### 3. 记忆泄露

```markdown
# ❌ 在群聊中引用 MEMORY.md 的私密内容
```

**解决：** 严格遵守加载规则，群聊不加载 MEMORY.md。

### 4. Mental Notes

```
# ❌ Agent 说"我记住了"但没写文件
# 下次启动完全忘记
```

**解决：** AGENTS.md 里明确写了——"Mental notes don't survive session restarts. Files do."
