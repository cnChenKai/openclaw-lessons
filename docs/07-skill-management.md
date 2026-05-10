# Skill 管理

> 从 70 个 skill 精简到 16 个的经验。

## Skill 审计

### 为什么需要审计

AI Agent 的 skill 库会自然膨胀——装了新的不删旧的，试了不用的不清理。结果：

- 70 个 skill，实际只用 16 个
- 很多 skill 从未被触发
- 有些 skill 缺少依赖，根本不能用
- Skill 之间有重叠

### 审计流程

```
1. 列出所有 skill
2. 按使用频率分类
3. 检查依赖
4. 测试核心 skill
5. 归档无用 skill
6. 更新依赖清单
```

### 分类标准

| 分类 | 标准 | 处理 |
|------|------|------|
| 核心 | 每周使用 2+ 次 | 保留，确保依赖完整 |
| 可能有用 | 每月使用 1+ 次 | 保留，标记为备用 |
| 用不上 | 从未使用或已被替代 | 归档到 .archived/ |

## 审计结果 (2026-05-05)

### 核心 Skill (16 个)

#### 博客运营 (6 个)

| Skill | 用途 | 依赖 |
|-------|------|------|
| blog-ops-autonomous | 博客流水线核心 | tavily-python, requests |
| blog-ops-morning-evolution | 晨间调研+起草 | tavily-python |
| blog-ops-midday-deep-dive | 午间深度扩展 | tavily-python |
| blog-ops-evening-evolution | 晚间发布 | tavily-python |
| tavily-blog-research | Tavily 调研层 | tavily-python |
| humanizer | 去 AI 腔 | 无 |

#### 办公文档 (4 个)

| Skill | 用途 | 依赖 |
|-------|------|------|
| pptx-generator | PPT 生成 | pptxgenjs (npm) |
| minimax-docx | DOCX 生成 | dotnet 8.0, LibreOffice |
| minimax-xlsx | XLSX 读写 | openpyxl (pip) |
| minimax-pdf | PDF 生成 | weasyprint, reportlab, playwright |

#### 股票/金融 (1 个)

| Skill | 用途 | 依赖 |
|-------|------|------|
| stock-market-quotes | 美股行情监控 | 无 (curl) |

#### 工具/辅助 (3 个)

| Skill | 用途 | 依赖 |
|-------|------|------|
| self-improving-agent | 自动记录经验教训 | 无 |
| obsidian | Obsidian 笔记管理 | 无 |
| getnote | GetNote 笔记服务 | API key |

#### 搜索 (2 个)

| Skill | 用途 | 依赖 |
|-------|------|------|
| tavily-blog-research | Tavily 搜索 | tavily-python |
| brave-search-api | Brave 搜索 | API key |

### 归档 Skill (50 个)

位于 `skills/.archived/hermes-skills/`，需要时可找回。

**类别：**
- 画图类：architecture-diagram, ascii-art, excalidraw
- SaaS 集成：notion, linear, airtable, google-workspace
- AI 编码工具：claude-code, codex, opencode, gemini-api-dev
- 开发方法论：plan, TDD, debugging
- Agent World 生态：agent-relay, exam-system
- 其他：youtube, gif, travel, web-design

## 依赖管理

### 完整依赖清单

```bash
# 系统包 (apt)
apt install -y \
    jq \
    pandoc \
    gh \
    libreoffice-writer \
    libreoffice-calc \
    libpango1.0-dev \
    libcairo2-dev

# Python 包 (pip)
pip install \
    python-pptx \
    arxiv \
    weasyprint \
    marker-pdf \
    reportlab \
    pypdf \
    tavily-python \
    requests \
    beautifulsoup4 \
    pre-commit \
    openpyxl

# Node.js 包 (npm)
npm install -g \
    pptxgenjs \
    @anthropic-ai/claude-code

# .NET SDK (通过 install script)
# SDK 8.0.420

# Playwright (headless chromium)
npx playwright install chromium
```

### 依赖检查脚本

```bash
#!/bin/bash
# check-deps.sh

echo "=== System Packages ==="
for pkg in jq pandoc gh libreoffice-writer; do
    if dpkg -l | grep -q "^ii  $pkg"; then
        echo "✅ $pkg"
    else
        echo "❌ $pkg (missing)"
    fi
done

echo ""
echo "=== Python Packages ==="
for pkg in python-pptx weasyprint reportlab tavily-python openpyxl; do
    if pip show $pkg > /dev/null 2>&1; then
        echo "✅ $pkg"
    else
        echo "❌ $pkg (missing)"
    fi
done

echo ""
echo "=== Node.js Packages ==="
for pkg in pptxgenjs; do
    if npm list -g $pkg > /dev/null 2>&1; then
        echo "✅ $pkg"
    else
        echo "❌ $pkg (missing)"
    fi
done

echo ""
echo "=== .NET SDK ==="
if dotnet --version > /dev/null 2>&1; then
    echo "✅ dotnet $(dotnet --version)"
else
    echo "❌ dotnet (missing)"
fi
```

## Skill 创建规范

### 目录结构

```
skills/my-skill/
├── SKILL.md           # 必须：skill 文档
├── scripts/           # 可选：辅助脚本
├── templates/         # 可选：模板文件
└── examples/          # 可选：示例
```

### SKILL.md 模板

```markdown
# Skill Name

## Description
一句话描述这个 skill 做什么。

## When to Use
- 触发条件 1
- 触发条件 2

## Prerequisites
- 依赖 1
- 依赖 2

## Usage
### 基本用法
\`\`\`bash
# 示例命令
\`\`\`

### 高级用法
\`\`\`bash
# 高级示例
\`\`\`

## Examples
### Example 1: 场景描述
\`\`\`
输入: ...
输出: ...
\`\`\`

## Troubleshooting
### 问题 1
解决方案

## Related Skills
- 相关 skill 1
- 相关 skill 2
```

### 最佳实践

1. **一个 skill 做一件事** — 不要什么都塞进去
2. **描述要具体** — "生成 PPT" 比 "文档处理" 好
3. **示例要真实** — 用实际场景，不是虚构的
4. **依赖要列出** — 不要让用户猜
5. **故障排除要详细** — 列出常见错误和解决方案

## Skill 演进

### 模型迭代对 Skill 的影响

2026 年 2 月到 5 月，模型从 Gemini → GLM-5 → Qwen → Gemini Flash → mimo-v2.5-pro 迭代了 5 次。

每次模型切换都会影响：
- Skill 的触发准确率
- 输出质量
- 响应时间
- Token 成本

**教训：** 不要过度依赖特定模型的行为。Skill 应该是模型无关的。

### Skill 的生命周期

```
创建 → 使用 → 维护 → 归档 → 可能复活
```

- **创建：** 解决具体问题
- **使用：** 日常调用
- **维护：** 修复 bug、更新依赖
- **归档：** 不再使用但保留
- **复活：** 需求变化后重新启用

### 何时删除 vs 归档

- **归档：** 功能被替代、暂时不用、可能以后用
- **删除：** 功能完全过时、安全风险、维护成本太高

**推荐：** 默认归档，除非有明确理由删除。
