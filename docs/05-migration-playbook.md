# 实例迁移手册

> 从旧 Agent 实例迁移到新实例的完整流程。

## 迁移场景

- Agent 框架升级（需要全新安装）
- 切换到新的服务器
- 从一个 Agent 实例换到另一个（Hermes → Jarvis）
- 灾难恢复

## 迁移清单

```
Phase 1: 准备
□ 完整备份旧实例
□ 列出所有待迁移内容
□ 确认新实例基础环境

Phase 2: 核心迁移
□ 四文件人格 (SOUL/IDENTITY/USER/TOOLS)
□ 工作流文档 (workflows/)
□ Cron jobs
□ Scripts
□ Skills

Phase 3: 凭据迁移
□ .env 文件
□ API keys
□ SSH keys
□ OAuth tokens

Phase 4: 记忆迁移
□ MEMORY.md (直接复制，后续精简)
□ daily/ (归档，不直接导入)
□ workflows/ (直接复制)
□ config/ (直接复制)

Phase 5: 验证
□ Agent 启动正常
□ Cron jobs 触发正常
□ 外部 API 连通
□ SSH 连接正常
□ 博客发布流程正常

Phase 6: 清理
□ 旧实例备份后停止
□ 更新文档中的引用
□ 通知相关方
```

## Phase 1: 完整备份

```bash
# 旧实例上执行
tar czf /tmp/agent-backup-$(date +%Y%m%d).tar.gz \
    ~/.openclaw/workspace/ \
    ~/.openclaw/config/ \
    ~/.hermes/ \
    ~/.ssh/ \
    ~/.config/gh/

# 上传到 R2 私有桶
aws --endpoint-url https://<account>.r2.cloudflarestorage.com \
    cp /tmp/agent-backup-*.tar.gz s3://openclaw/secure/backups/
```

## Phase 2: 核心迁移

### 四文件人格

```bash
# 直接复制，根据新 Agent 身份修改 IDENTITY.md
scp old-instance:~/.openclaw/workspace/SOUL.md ./
scp old-instance:~/.openclaw/workspace/IDENTITY.md ./
scp old-instance:~/.openclaw/workspace/USER.md ./
scp old-instance:~/.openclaw/workspace/TOOLS.md ./
```

**注意：** SOUL.md 和 USER.md 通常不需要改。IDENTITY.md 需要更新名字和身份。

### Cron Jobs

```bash
# 在新实例上重建 cron jobs
# OpenClaw cron 不支持直接导出，需要手动创建

# 列出旧实例的 cron
openclaw cron list

# 在新实例上逐个创建
openclaw cron add --schedule "0 8 * * *" --payload "晨间选题任务..."
```

### Skills

```bash
# 复制 skills 目录
scp -r old-instance:~/.openclaw/workspace/skills/ ./

# 或者只复制 active skills
scp -r old-instance:~/.openclaw/workspace/skills/{blog-ops-*,humanizer,stock-*} ./
```

## Phase 3: 凭据迁移

### .env 文件

```bash
# 复制所有 .env 文件
scp old-instance:~/.hermes/blog-ops/.env ./
scp old-instance:~/.hermes/blog-ops/.env.alpha_vantage ./
```

### SSH Keys

```bash
# 复制 SSH keys
scp old-instance:~/.ssh/id_ed25519 ./
scp old-instance:~/.ssh/id_friday_dn42 ./
scp old-instance:~/.ssh/config ./

# 设置权限
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/config
```

### GitHub CLI

```bash
# 复制 gh 配置
scp -r old-instance:~/.config/gh/ ./

# 验证
gh auth status
```

## Phase 4: 记忆迁移（关键步骤）

记忆迁移不是简单复制，需要蒸馏。

### 步骤

1. **通读所有记忆文件**
   ```bash
   # 列出所有文件
   find old-instance:~/.openclaw/workspace/memory/ -name "*.md" | wc -l
   
   # 逐个读取（可能需要几个小时）
   ```

2. **分类**
   - ✅ 有价值：需要导入
   - ⚠️ 已过时：只记录存在，不导入
   - ❌ 重复/无用：跳过

3. **去重**
   - 与新实例已有信息比对
   - 避免重复导入

4. **蒸馏**
   - 从 daily 文件中提取精华
   - 写入 MEMORY.md 或 workflows/

5. **归档**
   - 原始文件保留在 archive/ 目录
   - 不删除，只是不导入

### 实际数据

| 指标 | 数量 |
|------|------|
| 处理文件总数 | 82 |
| 有价值提取 | 28 |
| 跳过 (纯日志/重复/过时) | 54 |
| 写入新文件 | 3 |
| 更新文件 | 1 (MEMORY.md) |
| 归档文件 | 83 |

### 跳过的内容类型

| 类型 | 数量 | 原因 |
|------|------|------|
| 会话记录模板 | ~30 | 大量重复的格式模板 |
| HEARTBEAT_OK 循环 | ~10 | 无实质内容的空轮询 |
| 已停用功能 | ~8 | 数字孪生协作系统等 |
| 已迁移内容 | ~5 | 凭据、skills、cron 已迁移 |
| 模型配置 | ~5 | 频繁切换的临时记录 |

## Phase 5: 验证清单

```bash
# 1. Agent 启动
openclaw status

# 2. 人格文件加载
# 在 Telegram 中发送消息，检查 Agent 响应风格

# 3. Cron jobs
openclaw cron list
# 手动触发一个测试
openclaw cron run <job-id>

# 4. 外部 API
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d" -H "User-Agent: Mozilla/5.0"
# 检查 Tavily
curl -s "https://api.tavily.com/search" -H "Authorization: Bearer $TAVILY_KEY"

# 5. SSH
ssh prod-mubibai "echo ok"

# 6. 博客发布
cd ~/.hermes/blog-ops && python3 scripts/publish_wp.py --dry-run drafts/test.md

# 7. GitHub
gh auth status
gh repo list --limit 3
```

## Phase 6: 清理

```bash
# 旧实例
# 1. 最终备份
tar czf /tmp/hermes-final-backup.tar.gz ~/.hermes/

# 2. 停止服务
sudo systemctl stop hermes
sudo systemctl disable hermes

# 3. 清理 crontab
crontab -e  # 删除 hermes 相关条目

# 4. 保留备份，删除运行目录
rm -rf ~/.hermes/

# 新实例
# 1. 更新文档中的旧引用
grep -r "hermes\|Hermes" ~/.openclaw/workspace/ --include="*.md" -l

# 2. 更新 IDENTITY.md
# 3. 通知用户迁移完成
```

## 灾难恢复

如果旧实例完全不可用：

1. 从 R2 私有桶下载最新备份
2. 解压到新实例
3. 按 Phase 5 验证
4. 修复发现的问题

```bash
# 从 R2 恢复
aws --endpoint-url https://<account>.r2.cloudflarestorage.com \
    cp s3://openclaw/secure/backups/openclaw-full-backup-20260505.tar.gz /tmp/

tar xzf /tmp/openclaw-full-backup-*.tar.gz -C /
```

## 踩过的坑

### 1. 模型配置不一致

旧实例的模型配置（maxTokens、reasoning）在新实例上可能不同。迁移后第一件事检查模型配置。

### 2. Cron Job 时间漂移

时区设置可能不同，导致 cron job 在错误的时间触发。迁移后检查时区。

### 3. 凭据泄露

迁移过程中 .env 文件可能被意外提交到 git。始终用 .gitignore 排除。

### 4. 记忆冲突

新实例可能已经有自己的记忆，与旧记忆冲突。迁移前先备份新实例的记忆。

### 5. Skill 依赖缺失

旧实例安装的依赖（apt、pip、npm）在新实例上可能缺失。迁移后运行 skill 审计。
