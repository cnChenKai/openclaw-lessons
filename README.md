# OpenClaw Lessons Learned

> 从两个月的生产实践中提炼的经验教训——关于 AI Agent 运维、自动化博客流水线、记忆系统设计和基础设施管理。

## 背景

这个仓库记录了 2026 年 2 月至 5 月间，运行 OpenClaw AI Agent 服务个人生产力的完整经验。经历了两个 Agent 实例（Hermes → Jarvis），处理了 80+ 篇博客文章、8 个 cron 任务、16 个 skill、DN42 网络搭建、美股监控等场景。

**不是教程，是踩坑记录。**

## 文档目录

| 文档 | 内容 |
|------|------|
| [Agent 架构设计](docs/01-agent-architecture.md) | SOUL/IDENTITY/USER/TOOLS 四文件模型，人机边界，权限设计 |
| [博客自动化流水线](docs/02-blog-automation.md) | 三段式生产、防重复机制、Humanizer QC、WordPress 发布链路 |
| [记忆系统与连续性](docs/03-memory-and-continuity.md) | 分层记忆架构、daily vs long-term、迁移策略 |
| [基础设施与部署](docs/04-infrastructure.md) | Oracle Cloud ARM、Tailscale、R2 图床、DN42、反代 |
| [实例迁移手册](docs/05-migration-playbook.md) | 从旧 Agent 到新 Agent 的完整迁移流程 |
| [经验教训合集](docs/06-lessons-learned.md) | 所有踩过的坑，按类别整理 |
| [Skill 管理](docs/07-skill-management.md) | Skill 审计、精简策略、依赖管理 |
| [鸿蒙编译踩坑](docs/08-harmonyos-compilation.md) | 30 次 GitHub Actions 失败全记录——CLI Tools、hvigor、ArkTS 限制、API 类型系统 |

## 核心教训（速览）

1. **默认 draft，确认后才 publish** — 自治 Agent 的写操作绝不能默认公开
2. **API 操作必须幂等** — 创建前先检查存在性，用 lock 防并发
3. **不信任记忆，先搜后写** — 涉及具体数字的内容必须实时验证
4. **解析用健壮方式** — 不要用脆弱的正则解析 Markdown
5. **Skill 少即是多** — 70 个 skill 精简到 16 个，效率反而提升
6. **记忆分层** — daily 是日志，MEMORY.md 是精华，不能混
7. **备份到对象存储** — 本地备份不够，R2 私有桶是最后防线
8. **Agent 不是你的代言人** — 群聊里保持克制，私聊里积极有用
9. **HarmonyOS CLI Tools 不支持 ARM Linux** — 只能用 GitHub Actions
10. **ArkTS 不是 TypeScript** — `in`/`any`/`spread`/`Object.assign` 全禁
11. **hvigor 版本和 plugin 必须匹配** — 5.x 配 5.x，6.x 配 6.x
12. **HarmonyOS API 文档不可信** — 以 `.d.ts` 类型定义为准

## 适用场景

- 用 OpenClaw 或类似框架运行个人 AI Agent
- 自动化内容生产（博客、文档）
- 多 Agent 实例管理和迁移
- 自建基础设施上的 AI 工作负载
- HarmonyOS NEXT 原生应用开发与 CI 构建

## License

MIT — 随便用，踩坑了别怪我。
