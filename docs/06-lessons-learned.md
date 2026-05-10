# 经验教训合集

> 所有踩过的坑，按类别整理。每个教训都有真实事件背景。

## 自治操作安全

### [LRN-001] 默认 Draft，确认后才 Publish

**事件：** 2026-03-31，自治 Agent 的文章解析失败，fallback 到 publish 状态，导致无关内容被公开发布。

**规则：**
- 自治 Agent 的所有写操作默认应为 draft 状态
- 只有明确确认后才改为 publish
- 解析失败时 fallback 到 draft，不是 publish

**实现：**
```python
# publish_wp.py 中
status = "draft"  # 默认 draft
if args.publish:
    status = "publish"
```

### [LRN-002] API 操作必须幂等

**事件：** 2026-03-31，Agent 因网络超时重试发布，导致同一篇文章被创建两次。

**规则：**
- 创建前先检查是否存在（用 slug/title 查询）
- 用 pid/lock 文件防并发
- 记录返回的 ID，后续操作用 ID 而不是名称

**实现：**
```python
# 先检查
existing = wp_client.get_posts(slug="my-post")
if existing:
    wp_client.update_post(existing[0].id, data)
else:
    wp_client.create_post(data)
```

### [LRN-003] 解析用健壮方式

**事件：** 2026-03-31，用正则解析 Markdown frontmatter，遇到多行值时解析失败。

**规则：**
- 不要用脆弱的正则解析结构化数据
- 用 YAML 解析器处理 frontmatter
- 支持多种 Markdown 结构变体（H2、粗体、列表等）

**实现：**
```python
import yaml

def parse_frontmatter(content):
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return fm, body
    return {}, content
```

## 内容质量

### [LRN-004] 发布前必须核实数据

**事件：** 2026-03-29，博客文章 "GLM-5 vs Gemini 3.1 Pro" 包含重大数据错误——参数量和 benchmark 分数都是错的。

**规则：**
- 写任何涉及具体数字的内容，先搜后写
- 模型参数量、benchmark 分数、发布日期、性能数据——全部需要实时验证
- 不依赖记忆或旧草稿

**检查清单：**
- [ ] 模型参数量
- [ ] Benchmark 分数
- [ ] 发布日期
- [ ] 性能数据
- [ ] 融资金额
- [ ] 硬件规格

### [LRN-005] 内容防重复

**事件：** 2026-04-01，Agent 发布了一篇与已发布文章高度重复的机器人技术文章（Post #462）。

**规则：**
- 开工前必须跑 wp_draft_guard.py
- 比对 slug 和标题相似度
- 最近 3 篇中有 2+ 篇同领域 → 必须换线

**实现：**
```bash
# 每次写作前
python3 scripts/wp_draft_guard.py
```

### [LRN-006] Humanizer QC

**事件：** Agent 生成的文章有明显的 AI 腔——"Executive Summary"、"In this article"、过度使用粗体。

**规则：**
- Humanizer 分数 < 30/100
- 禁止 AI 腔短语
- Sentence case 标题
- 减少粗体，用代码块替代
- 段落长度不均匀

## 基础设施

### [LRN-007] Tailscale 优于公网 SSH

**事件：** 2026-05，Oracle Cloud 公网 SSH 偶发不稳定，导致操作中断。

**规则：**
- 服务器间通信优先走 Tailscale 内网
- SSH 配置 ServerAliveInterval 30
- 备份通道：公网 SSH 作为 fallback

### [LRN-008] 对象存储备份

**事件：** 2026-02-26，尝试用 123pan WebDAV 备份，速度只有 20-30 KiB/s，完全不可用。

**规则：**
- 全量备份到 Cloudflare R2 私有桶
- 备份包含所有 key 和凭据
- 保留恢复命令（预签名 URL）

### [LRN-009] Docker 容器 IP 不可靠

**事件：** PostgreSQL Docker 容器重启后 IP 变化，导致连接失败。

**规则：**
- 用端口映射（127.0.0.1:5432）而不是容器内部 IP
- 用 docker-compose 固定网络配置
- 连接字符串用 localhost:port

### [LRN-010] Skill 依赖必须显式安装

**事件：** 2026-05-05，迁移后 6 个 Office 工具 skill 无法使用，因为缺少系统依赖。

**规则：**
- 迁移后第一件事：运行 skill 审计
- 依赖清单：apt、pip、npm、dotnet
- 测试每个 skill 的基本功能

**完整依赖清单：**
```bash
# apt
apt install -y jq pandoc gh libreoffice-writer libreoffice-calc libpango

# pip
pip install python-pptx arxiv weasyprint marker-pdf reportlab pypdf tavily-python requests beautifulsoup4

# npm
npm install -g pptxgenjs @anthropic-ai/claude-code

# dotnet
# 通过 install script 安装 SDK 8.0
```

## Agent 行为

### [LRN-011] Agent 不是代言人

**事件：** 2026-02，Agent 在群聊中过度参与，回复了每条消息，引起其他参与者不适。

**规则：**
- 群聊中保持克制，质量 > 数量
- 只在被 @、能提供价值、纠正错误时发言
- 不回复纯闲聊、已回答的问题、"对/不错"类回复

### [LRN-012] Mental Notes 不存在

**事件：** Agent 多次说"我记住了"但没有写文件，下次启动完全忘记。

**规则：**
- "Mental notes" 不会跨 session 存活
- 想记住的东西必须写到文件
- 用户说"记住这个" → 更新 memory/ 文件
- 学到教训 → 更新 TOOLS.md 或 workflows/

### [LRN-013] 静默时段

**事件：** 2026-03，Agent 在凌晨 2 点发送非紧急通知。

**规则：**
- 静默时段：23:00-08:00（除非紧急）
- 紧急定义：保证金余额 < $2,000、服务器宕机、安全事件
- 非紧急信息队列到早上发送

## Skill 管理

### [LRN-014] 少即是多

**事件：** 2026-05-05，审计发现 70 个 skill 中只有 16 个真正有用，其余 50 个从未使用。

**规则：**
- 定期审计 skill，删除从未使用的
- 16 个精挑细选的 skill > 70 个杂乱的 skill
- 归档 > 删除（可以找回）

**审计流程：**
1. 逐个检查 skill 的使用频率
2. 分类：核心 / 可能有用 / 用不上
3. 核心 skill 保留，用不上的归档
4. 测试每个核心 skill 的基本功能
5. 安装缺失的依赖

### [LRN-015] Skill 依赖管理

**事件：** 2026-05-05，安装了 dotnet SDK 后 minimax-docx 才能使用，但之前一直以为它不工作。

**规则：**
- 每个 skill 的 SKILL.md 应该列出依赖
- 迁移或重装后，先检查依赖
- 维护一个全局依赖清单

## 数据管理

### [LRN-016] 凭据分离

**事件：** 凭据被意外写入 MEMORY.md，差点在群聊中暴露。

**规则：**
- 凭据存 .env 文件
- MEMORY.md 只记录"凭据在哪里"
- 群聊不加载 MEMORY.md

### [LRN-017] 记忆蒸馏

**事件：** 2026-05-06，从旧实例迁移 82 个记忆文件，大部分是无用的会话记录和空轮询日志。

**规则：**
- 记忆迁移不是复制粘贴，是蒸馏
- 通读 → 分类 → 去重 → 蒸馏 → 归档
- 82 个文件 → 28 个有价值 → 3 个新文件

### [LRN-018] 配置快照

**事件：** 2026-04，修改了 DN42 配置但没有记录，后来忘记改了什么。

**规则：**
- 配置变更时写入 config/ 目录
- 包含变更原因和日期
- 保留旧配置的备份

## 沟通

### [LRN-019] 直接沟通

**事件：** 用户多次表示不喜欢 AI 的客套话。

**规则：**
- 不用 "Great question!"、"I'd be happy to help!"
- 直接给答案，不铺垫
- 有观点，允许不同意
- 用用户的语言风格

### [LRN-020] 知道什么时候问

**事件：** Agent 自作主张删除了一个文件，用户事后才知道。

**规则：**
- 内部操作（读、组织、搜索）→ 自由做
- 外部操作（邮件、推特、删除）→ 先问
- 不确定 → 先问
