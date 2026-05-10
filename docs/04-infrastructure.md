# 基础设施与部署

> 在自建服务器上运行 AI Agent 的实战经验。

## 服务器架构

```
┌─────────────────────────────────────────────────┐
│  Oracle Cloud ARM (Ampere A1)                    │
│  Tailscale: 100.75.60.122                       │
│                                                  │
│  ┌───────────┐  ┌───────────┐  ┌──────────────┐ │
│  │ OpenClaw  │  │ SillyTavern│  │  Caddy       │ │
│  │ Gateway   │  │ (Docker)   │  │  (反代+HTTPS)│ │
│  │ :18789    │  │ :8080      │  │              │ │
│  └───────────┘  └───────────┘  └──────────────┘ │
│                                                  │
│  ┌───────────┐  ┌───────────┐                    │
│  │ Telegram  │  │ Codex     │                    │
│  │ Bot       │  │ Proxy     │                    │
│  │           │  │ :8080     │                    │
│  └───────────┘  └───────────┘                    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  prod.mubibai.com (Debian 13 arm64)             │
│  Tailscale: 100.120.121.118, SSH: 4747          │
│                                                  │
│  ┌───────────┐  ┌───────────┐  ┌──────────────┐ │
│  │ Paperclip │  │ WordPress │  │  PostgreSQL   │ │
│  │ :3100     │  │ (1Panel)  │  │  (Docker)    │ │
│  └───────────┘  └───────────┘  └──────────────┘ │
└─────────────────────────────────────────────────┘
```

## Tailscale 组网

两台服务器通过 Tailscale 内网互联，SSH 走内网，不暴露公网端口。

```bash
# SSH 配置 (~/.ssh/config)
Host prod-mubibai
    HostName 100.120.121.118
    Port 4747
    User paperclip
    IdentityFile ~/.ssh/id_ed25519

Host dev
    HostName 100.75.60.122
    User root
```

**教训：** 公网 SSH 不稳定时（Oracle Cloud 偶发），Tailscale 是可靠的备用通道。

## Cloudflare R2 对象存储

### 双桶架构

| 桶 | 用途 | 访问 |
|---|---|---|
| pic | 博客图片 | 公开（p.mubibai.com） |
| openclaw | 备份/机密 | 私有 |

### 快捷命令

```bash
# ~/.bashrc
alias r2pub='aws --endpoint-url https://<account>.r2.cloudflarestorage.com s3 cp - s3://pic/'
alias r2sec='aws --endpoint-url https://<account>.r2.cloudflarestorage.com s3 cp - s3://openclaw/'
```

### 全量备份

```bash
# 备份到 R2 私有桶
tar czf - /root/.openclaw /root/.ssh /root/.config | r2sec secure/backups/openclaw-full-backup-$(date +%Y%m%d).tar.gz

# 一句话恢复（预签名 URL，7 天有效）
aws --endpoint-url https://<account>.r2.cloudflarestorage.com s3 presign s3://openclaw/secure/backups/openclaw-full-backup-20260505.tar.gz --expires-in 604800
```

## Caddy 反向代理

```caddyfile
# /etc/caddy/Caddyfile
st.mubibai.com {
    reverse_proxy localhost:8080
    basicauth * {
        kai $2a$14$...  # pitt1992
    }
}
```

**优势：** Caddy 自动签 Let's Encrypt 证书，零配置 HTTPS。

## DN42 网络

DN42 是一个去中心化的 VPN 网络，用于学习 BGP、WireGuard 等网络技术。

### 配置要点

```bash
# WireGuard 隧道
[Interface]
PrivateKey = <key>
Address = 172.20.2.192/32, fd85:df93:4ab4::1/128
ListenPort = 21172

[Peer]
PublicKey = <peer-key>
Endpoint = <peer-ip>:21172
AllowedIPs = 172.20.0.0/16, fd00::/8
```

### BIRD2 BGP

```bird
protocol bgp dn42_6700_v6 from dn42_base {
    neighbor fd42:6700:6700::1 as 4242423088;
    source address fd85:df93:4ab4::1;
}
```

### 踩过的坑

| 问题 | 原因 | 解决 |
|------|------|------|
| WG 握手成功但不通 | 缺少 point-to-point 地址 | `ip addr add A peer B` |
| 多 peer 端口冲突 | 同一 ListenPort | 每个 peer 用不同端口 |
| BGP 会话不起来 | MP-BGP/Extended Next Hop 配置错误 | 检查 address family 匹配 |
| UFW 放行无效 | 旧 iptables REJECT 规则短路 | 清理旧规则 |

### 状态页

```nginx
# /etc/nginx/sites-available/dn42-status
server {
    listen 443 ssl;
    server_name dn42.mubibai.com;
    
    location / {
        root /var/www/dn42-status;
        autoindex on;
    }
}
```

60 秒自动刷新，展示 BGP 状态和 WireGuard 聚合信息，不暴露敏感细节。

## systemd 服务管理

### OpenClaw Gateway (用户级服务)

```bash
# ~/.config/systemd/user/openclaw-gateway.service
[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
Type=simple
ExecStart=/root/.nvm/versions/node/v22.22.2/bin/openclaw gateway start
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

```bash
systemctl --user enable openclaw-gateway
systemctl --user start openclaw-gateway
```

### 生产服务器 Paperclip

```bash
# /etc/systemd/system/paperclip.service
[Unit]
Description=Paperclip Blog Engine
After=network.target

[Service]
Type=simple
User=paperclip
WorkingDirectory=/home/paperclip
ExecStart=/home/paperclip/paperclip
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 常见问题

### 1. OpenClaw 模型配置错误

**症状：** Agent 响应截断或报错  
**原因：** maxTokens 默认值太小（4096），reasoning 标记错误  
**解决：** 手动修正模型配置

```bash
openclaw config set models.mimo-v2.5-pro.maxTokens 131072
openclaw config set models.mimo-v2.5-pro.reasoning true
```

### 2. SSH 连接不稳定

**症状：** SSH 断连，操作中断  
**原因：** 公网 SSH 被 Oracle Cloud 安全组限制  
**解决：** 走 Tailscale 内网，配置 ServerAliveInterval

```
# ~/.ssh/config
ServerAliveInterval 30
ServerAliveCountMax 3
```

### 3. Docker 容器重启后 IP 变化

**症状：** PostgreSQL 连接失败  
**原因：** Docker 重启后容器 IP 变化  
**解决：** 用 127.0.0.1:5432 端口映射，不用容器内部 IP

### 4. Let's Encrypt 证书续期

**症状：** HTTPS 证书过期  
**原因：** Caddy 自动续期失败（端口 80 被占）  
**解决：** 确保端口 80 未被其他服务占用
