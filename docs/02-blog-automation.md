# 博客自动化流水线

> 用 AI Agent 自动运营一个面向 Tier 1 AI/ML 工程师的英文技术博客。

## 架构概览

```
晨间 (08:10)          午间 (13:30)          晚间 (21:30)
┌──────────┐         ┌──────────┐         ┌──────────┐
│ 趋势扫描  │         │ 深度扩展  │         │ 终审发布  │
│ 选题起草  │   →     │ 代码/数据 │   →     │ Humanizer│
│ 1500词    │         │ 2500词    │         │ R2配图   │
└──────────┘         └──────────┘         └──────────┘
```

## 三段式生产

### 晨间 (08:10) — 选题与起草

1. 读 `NEXT_HOOK.md`（昨日留下的搜索钩子）
2. 用 Tavily 扫描技术社区热点
3. 从 `CONTENT_CALENDAR.md` 选择主题
4. 起草 1500-2500 词的初稿
5. 保存到 `drafts/` 目录

**关键教训：选题必须跑防重复检查。**

```bash
# 开工前先跑 guard
python3 scripts/wp_draft_guard.py
```

### 午间 (13:30) — 深度扩展

1. 扩展到 2000-3000 词
2. 添加代码示例、benchmark 数据、架构图
3. 用 web_search 核实所有数字
4. 扫描新的技术趋势，更新 `CONTENT_CALENDAR.md`

**关键教训：技术对比文章的数字必须实时搜索验证。**

### 晚间 (21:30) — 终审与发布

1. Humanizer QC（目标 < 30/100）
2. SEO 检查（标题、slug、excerpt、tags）
3. 本地图片上传到 R2 图床
4. 发布到 WordPress（默认 draft，确认后 publish）
5. 写入 `NEXT_HOOK.md`（明日钩子）

## 防重复机制

这是最重要的防线。AI Agent 天然倾向于重复生成类似内容。

### wp_draft_guard.py

```python
# 核心逻辑
1. 拉取 WordPress 已发布文章的 slug 列表
2. 扫描本地 drafts/ 目录的草稿
3. 比对 slug 和标题相似度
4. 输出重复警告
```

### 三层防重

| 层级 | 机制 | 作用 |
|------|------|------|
| L1 | NEXT_HOOK.md | 预设明日方向，避免随机选题撞车 |
| L2 | CONTENT_CALENDAR.md | 7 天排期，可视化主题分布 |
| L3 | wp_draft_guard.py | 最终防线，发布前硬检查 |

### 内容多样性规则

> 最近 3 篇文章中有 2+ 篇属于同一技术领域 → 必须换线

例如：连续写了 2 篇 LLM 推理优化 → 第 3 篇必须换到基础设施、MLOps、数据工程等其他领域。

## Humanizer QC

AI 生成内容的最大敌人不是错误，是"AI 腔"。

### 什么是 AI 腔

- "In this article, we will explore..."
- "Executive Summary"
- "If you're looking to..."
- 过度使用粗体
- 列表项超过 5 个
- 每段都以主题句开头

### Humanizer 评分标准

| 分数 | 含义 |
|------|------|
| 0-20 | 纯人类风格，优秀 |
| 20-30 | 可接受 |
| 30-50 | 需要修改 |
| 50+ | 重写 |

### 降分技巧

1. 删掉所有 "In this article"、"Executive Summary"
2. 用 Sentence case（不是 Title Case）
3. 减少粗体，用代码块替代
4. 段落长度不均匀（人类写作的自然节奏）
5. 加入个人观点（"I think"、"In my experience"）
6. 偶尔用口语化表达

## WordPress 发布链路

```bash
# 完整发布流程
python3 scripts/publish_wp.py drafts/my-post.md

# 自动执行：
# 1. 解析 frontmatter (title, slug, date, categories, tags, excerpt)
# 2. 提取 Markdown 中的本地图片
# 3. 上传图片到 Cloudflare R2 (p.mubibai.com)
# 4. 替换图片链接为 R2 URL
# 5. 转换 Markdown → HTML
# 6. 通过 WP REST API 创建/更新文章

# 预演模式（不实际发布）
python3 scripts/publish_wp.py drafts/my-post.md --dry-run

# 跳过 R2 图片上传
python3 scripts/publish_wp.py drafts/my-post.md --no-r2
```

### Frontmatter 格式

```yaml
---
title: "NVFP4 vs FP8: Memory Footprint is the New Throughput"
slug: nvfp4-vs-fp8-memory-footprint
date: 2026-04-02
categories: [AI Infrastructure, Quantization]
tags: [NVFP4, FP8, Blackwell, inference]
excerpt: "Why 1.8x memory reduction matters more than raw throughput for 700B+ model inference."
---
```

### R2 图床架构

```
Cloudflare R2
├── pic (公共桶)     → p.mubibai.com (自定义域)
│   └── blog/        → 博客图片
└── openclaw (私有桶) → 备份/机密共享
    └── secure/      → 加密备份
```

## 搜索与调研

### Tavily 配置

```bash
# 3 个 key 轮换防限速
TAVILY_KEY_1=tvly-dev-xxx
TAVILY_KEY_2=tvly-dev-yyy
TAVILY_KEY_3=tvly-dev-zzz
```

### 搜索策略

| 场景 | 方法 |
|------|------|
| 技术调研 | `tavily --topic general` |
| 新闻热点 | `tavily --topic news --days 7` |
| 页面提取 | `tavily extract <url>` |
| 交叉验证 | `web_search` (Brave) |

### 数据核实铁律

> 写任何涉及具体数字的内容，先搜后写。

- 模型参数量
- Benchmark 分数
- 发布日期
- 性能数据
- 融资金额

**血的教训：** 2026-03-29，一篇 GLM-5 vs Gemini 3.1 Pro 的文章包含重大数据错误（参数量和 benchmark 分数），因为依赖了记忆而非实时搜索。

## 目录结构

```
blog-ops/
├── .env                    # API 密钥（Tavily、WP、R2）
├── NEXT_HOOK.md            # 明日搜索钩子
├── CONTENT_CALENDAR.md     # 7 天排期
├── drafts/                 # 草稿
│   ├── my-post.md
│   └── archived/           # 已发布归档
├── scripts/
│   ├── publish_wp.py       # WordPress 发布
│   ├── wp_draft_guard.py   # 防重复检查
│   ├── r2_storage.py       # R2 双桶管理
│   └── delete_wp_post.py   # 删除重复帖
└── plans/                  # 运营计划（已归档）
```

## Cron Jobs

| 时间 | 任务 | 类型 |
|------|------|------|
| 08:10 | 晨间选题 | isolated agentTurn |
| 13:30 | 午间深挖 | isolated agentTurn |
| 21:30 | 晚间发布 | isolated agentTurn |
| 10:30 | QA 审计 | isolated agentTurn |

每个 cron job 运行在独立的 isolated session 中，不污染主会话上下文。
