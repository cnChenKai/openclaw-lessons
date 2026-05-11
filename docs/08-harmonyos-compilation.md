# HarmonyOS 编译踩坑全记录

> ArkVault 项目，2026-05-10，30 次 GitHub Actions 失败，0 次成功。从下午 1 点搞到晚上 6 点。

## 项目背景

ArkVault 是一个 HarmonyOS NEXT 原生密码管理器，用 ArkTS 开发。由于 HarmonyOS CLI Tools 不支持 ARM Linux（我们的服务器是 Oracle Cloud ARM），只能用 GitHub Actions 做 CI 构建。

## 时间线总览

```
13:38 ── 15:31 ── 16:16 ── 17:00 ── 17:40 ── 18:20
  │        │        │        │        │        │
  ▼        ▼        ▼        ▼        ▼        ▼
 阶段1    阶段2    阶段3    阶段4    阶段5    阶段6
 CLI工具  环境配置  构建系统  签名配置  ArkTS    类型系统
 下载     权限     hvigor   签名     语法限制  AssetMap
```

30 次失败，每个阶段 5-6 次迭代。

---

## 阶段 1: CLI Tools 下载 (5 次失败)

### 问题

HarmonyOS CLI Tools 是一个 ~900MB 的 zip 包，GitHub Actions 的 `ubuntu-latest` runner 下载后需要解压和配置。

### 踩过的坑

**1.1 嵌套目录结构**

CLI Tools 的 zip 包解压后有一层嵌套目录：
```
commandline-tools.zip
└── command-line-tools/          # 这一层
    ├── hvigor/
    ├── ohpm/
    └── sdk/
```

直接 `unzip -d /opt/command-line-tools` 会得到 `/opt/command-line-tools/command-line-tools/...`，路径多了一层。

**解决：**
```bash
unzip -q commandline-tools.zip -d /tmp/cli-extract
cp -r /tmp/cli-extract/command-line-tools/. /opt/command-line-tools/
```

**1.2 文件权限**

解压后的文件权限不一致，有些脚本没有执行权限。

**解决：**
```bash
sudo chmod -R 755 /opt/command-line-tools
```

**1.3 大文件分片**

GitHub Releases 对单文件有大小限制，900MB 的 zip 超过了某些限制。

**解决：** 分成 3 个 part 文件上传，下载后合并：
```bash
wget .../commandline-tools.zip.part_aa
wget .../commandline-tools.zip.part_ab
wget .../commandline-tools.zip.part_ac
cat commandline-tools.zip.part_* > commandline-tools.zip
```

**1.4 R2 预签名 URL 限制**

尝试用 Cloudflare R2 的预签名 URL 下载，但有 1GB 限制。

**解决：** 放弃 R2，直接用 GitHub Releases 存储分片文件。

**1.5 清理权限**

删除临时文件时 `rm -rf` 权限不足（因为用了 sudo 解压）。

**解决：** `sudo rm -rf`

### 教训

> HarmonyOS CLI Tools 的安装过程没有官方文档说明如何在 CI 中配置。每一个路径、权限、环境变量都需要自己摸索。

---

## 阶段 2: 环境配置 (4 次失败)

### 问题

hvigor（HarmonyOS 的构建工具）需要特定的环境变量和 npm 注册表配置。

### 踩过的坑

**2.1 ohpm 路径**

ohpm（HarmonyOS 的包管理器）不在 PATH 中，hvigor 找不到它。

**解决：**
```bash
echo "/opt/command-line-tools/ohpm/bin" >> $GITHUB_PATH
echo "/opt/command-line-tools/hvigor/bin" >> $GITHUB_PATH
```

**2.2 DEVECO_SDK_HOME 环境变量**

环境变量名搞错了——用了 `HOS_SDK_HOME` 但 hvigor 实际要的是 `DEVECO_SDK_HOME`。

**解决：**
```bash
echo "DEVECO_SDK_HOME=/opt/command-line-tools/sdk" >> $GITHUB_ENV
```

**2.3 npmrc 文件缺失**

hvigor 依赖 `.npmrc` 文件来配置 npm 注册表，但 GitHub Actions runner 没有这个文件。

错误信息：
```
The hvigor depends on the npmrc file. No npmrc file is matched in the current user folder.
```

**解决：**
```bash
cat > ~/.npmrc << 'EOF'
registry=https://registry.npmjs.org/
@ohos:registry=https://repo.huaweicloud.com/repository/npm/
EOF
```

**2.4 ohpm 注册表**

ohpm 需要单独配置华为的包注册表。

**解决：**
```bash
ohpm config set registry https://repo.harmonyos.com/ohpm/
```

### 教训

> HarmonyOS 的构建工具链（hvigor + ohpm + SDK）需要三套不同的注册表/路径配置，而且文档几乎没有。必须靠试错。

---

## 阶段 3: 构建系统 hvigor (6 次失败)

### 问题

hvigor 是华为自研的构建工具，基于 Gradle 的理念但完全不兼容。配置文件是 JSON5 格式，行为和 Node.js 生态差异巨大。

### 踩过的坑

**3.1 hvigor-config.json5 格式**

初始的 `hvigor-config.json5` 放的是 JavaScript 代码（从 DevEco Studio 导出的模板），应该是 JSON5 配置。

**解决：** 重写为纯 JSON5 配置格式。

**3.2 hvigor-ohos-plugin 版本**

`hvigor-ohos-plugin@5.0.0` 不存在。华为的版本号不是标准 semver，需要查实际可用版本。

错误信息：
```
npm ERR! not found: @ohos/hvigor-ohos-plugin@5.0.0
```

**解决：** 用 `5.19.8` 或 `6.23.5`（取决于 hvigor 版本）。

**3.3 hvigor 版本与 plugin 版本不匹配**

hvigor `5.x` 只能用 `5.x` 的 plugin，hvigor `6.x` 只能用 `6.x` 的 plugin。混用会报 JSON 解析错误。

错误信息：
```
Not a correct JSON/JSON5 format, at file: .../error/error.json
```

**解决：** 保持 hvigor 和 plugin 版本一致。

**3.4 build-profile.json5 缺少 modules 数组**

CI 构建需要在 `build-profile.json5` 中显式声明 modules，DevEco Studio 会自动处理但 CLI 不会。

**解决：**
```json5
{
  "modules": [
    {
      "name": "entry",
      "srcPath": "./entry",
      "targets": [
        { "name": "default", "applyToProducts": ["default"] }
      ]
    }
  ]
}
```

**3.5 entry/oh-package.json5 缺失**

hvigor 要求每个模块都有自己的 `oh-package.json5`，但项目模板只生成了根目录的。

**解决：** 手动创建 `entry/oh-package.json5`。

**3.6 hapTasks vs homavuTasks**

entry 模块应该用 `hapTasks`（HarmonyOS Ability Package），不是 `homavuTasks`（HarmonyOS Ability Module）。

**解决：**
```typescript
// entry/hvigorfile.ts
export { hapTasks } from '@ohos/hvigor-ohos-plugin';
```

### 教训

> hvigor 的配置极其脆弱，版本兼容性差，错误信息晦涩。DevEco Studio 自动处理的事情在 CLI 模式下全部需要手动配置。

---

## 阶段 4: 签名配置 (4 次失败)

### 问题

HarmonyOS 应用签名和 Android 完全不同。需要 p12 证书、cer 证书、AGC Provision Profile 材料。

### 踩过的坑

**4.1 签名配置字段不完整**

`build-profile.json5` 中的 `signingConfigs` 需要多个字段，缺一个就报错。

**解决：**
```json5
"signingConfigs": [
  {
    "name": "default",
    "type": "HarmonyOS",
    "material": {
      "certpath": "signing/arkvault.cer",
      "storePassword": "$P12_PASSWORD",
      "keyAlias": "debugKey",
      "keyPassword": "$P12_PASSWORD",
      "profile": "signing/material/profile.p7b",
      "signAlg": "SHA256withECDSA",
      "storeFile": "signing/arkvault.p12"
    }
  }
]
```

**4.2 storePassword 长度要求**

HarmonyOS 要求 `storePassword` 和 `keyPassword` 长度 >= 32 字符。

错误信息：
```
The length of the storePassword or keyPassword field in the signature configuration is less than 32.
```

**解决：** 用 32+ 字符的密码，或者在 CI 中用环境变量覆盖。

**4.3 p12 私钥泄露**

签名用的 p12 文件包含私钥，最初被提交到了公开仓库。

**解决：**
1. 从仓库移除 p12
2. 用 BFG 清理 git 历史
3. p12 只存在 GitHub Secrets 中（base64 编码）

**4.4 material 文件结构**

AGC Provision Profile 的 material 文件需要按特定目录结构组织：
```
signing/material/
├── ac/<hash>      # Application Certificate
├── ce/<hash>      # Certificate Extension
└── fd/<hash>/     # Feature Description
    ├── 0
    ├── 1
    └── 2
```

文件名是 hash 值，不是人类可读的名字。搞错一个就签名失败。

### 教训

> HarmonyOS 签名系统比 Android 复杂得多，文档示例不完整，错误信息不告诉你具体哪个字段有问题。

---

## 阶段 5: ArkTS 语法限制 (5 次失败)

### 问题

ArkTS 不是 TypeScript。它是 TypeScript 的严格子集，禁用了大量 JavaScript/TypeScript 的动态特性。

### 踩过的坑

**5.1 `in` 操作符禁用**

```typescript
// ❌ ArkTS 禁止
if ('key' in obj) { ... }

// ✅ 替代方案
if (obj.key !== undefined) { ... }
```

错误码：`arkts-no-in`

**5.2 `any`/`unknown` 类型禁用**

```typescript
// ❌ ArkTS 禁止
function process(data: any) { ... }

// ✅ 必须用具体类型
function process(data: MyType) { ... }
```

错误码：`arkts-no-any-unknown`

**5.3 展开运算符限制**

```typescript
// ❌ ArkTS 只允许数组展开
const merged = { ...obj1, ...obj2 };  // 对象展开禁止
const arr = [...otherArr];            // 数组展开 OK

// ✅ 替代方案
const merged = Object.assign({}, obj1, obj2);
// 或者手动赋值
```

错误码：`arkts-no-spread`

**5.4 `Object.assign` 禁用**

```typescript
// ❌ ArkTS 禁止
const obj = Object.assign({}, defaults, overrides);

// ✅ 用属性字面量
const obj: MyType = {
  prop1: defaults.prop1,
  prop2: overrides.prop2,
};
```

错误码：`arkts-limited-stdlib`

**5.5 `TextEncoder`/`TextDecoder` 不可用**

```typescript
// ❌ ArkTS 没有 Web API 的 TextEncoder
const encoder = new TextEncoder();
const bytes = encoder.encode(str);

// ✅ 用 HarmonyOS 的 util 工具
import { util } from '@kit.ArkTS';
const encoder = new util.TextEncoder();
```

### 教训

> ArkTS 的限制远超预期。不能把 TypeScript 代码直接搬过来，几乎每一行涉及动态特性的代码都需要重写。建议在开发前通读 [ArkTS 限制文档](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-limitations-V5)。

---

## 阶段 6: HarmonyOS API 类型系统 (6 次失败)

### 问题

HarmonyOS API 的类型定义和文档示例经常不一致。AssetStoreKit 的 `AssetMap` 类型是最大的坑。

### 踩过的坑

**6.1 AssetMap 类型困惑**

文档示例用数组语法：
```typescript
const query: asset.AssetMap = [
  { tag: asset.Tag.SECRET, value: new Uint8Array(...) }
];
```

但类型定义是 `Map<Tag, Value>`。试了 5 种不同的写法才搞对：

1. 数组 → `Type 'AssetMap[]' is missing the following properties from type 'Map<Tag, Value>'`
2. Map → `Property 'tag' does not exist on type '[Tag, Value]'`
3. 数组语法 + 类型断言 → 还是不行
4. Map + 类型断言 → 还是不行
5. 最终：用 `Map` 构造函数 + 正确的泛型

**最终解决：**
```typescript
const query = new Map<asset.Tag, asset.ValueType>();
query.set(asset.Tag.SECRET, new Uint8Array(...));
const results = await asset.query(query);
```

**6.2 asset.query 返回值**

`asset.query()` 返回的是 `AssetMap[]`（数组），不是单个 `AssetMap`。文档没说清楚。

**6.3 cryptoFramework API**

```typescript
// ❌ 文档示例（过时）
const cipher = cryptoFramework.createCipher('AES128/GCM/NoPadding');

// ✅ 实际 API
const cipher = cryptoFramework.createCipher('AES_GCM_128');
```

**6.4 RdbStore.close() 方法**

```typescript
// ❌ 文档示例
db.close();

// ✅ 实际 API
await db.close();  // 是异步的
```

**6.5 GCM 参数**

GCM 加密的 `GcmParams` 类型字段名和文档不完全一致，需要查类型定义而不是文档。

### 教训

> HarmonyOS API 文档和实际类型定义严重不一致。**以类型定义为准，文档仅供参考。** 遇到类型错误时，直接去 `@ohos` 的 `.d.ts` 文件里查真实签名。

---

## 签名问题（30+ 次失败的根本原因）

### Material 和 p12 密码不匹配

AGC 导出的签名包有一个隐藏陷阱：

- `material` 文件里加密的是 AGC 内部生成的**二进制随机密码**（16字节）
- `p12` 文件的密码是你在下载时设的**文本密码**（如 "pitt1992..."）
- 两者不一致！hvigor 用 material 解密出的密码打不开 p12

### hvigor 密码加密机制（源码分析）

```
build-profile.json5 中的 storePassword = 加密后的 hex
↓
hvigor decipher-util.js 解密流程:
1. 读取 material/fd/0,1,2 → 3个16字节缓冲区
2. XOR(fd[0], fd[1], fd[2], component) → 16字节
3. Buffer.from(xorResult).toString('utf-8') → 密钥字符串
4. PBKDF2(密钥字符串, material/ac, 10000, 16, sha256) → AES密钥
5. AES-128-GCM 解密(material/ce) → 明文密码
6. 用明文密码打开 p12
```

**关键发现：** `Buffer.from(int8array).toString('utf-8')` 会把无效 UTF-8 字节替换为 U+FFFD（替换字符），这导致密钥派生结果和预期不同。在 Node.js v22 和 v24 上行为一致。

### 解决方案

在 DevEco Studio 中使用「自动签名」功能，它会生成一套密码匹配的 material + p12。

### 30 次失败分布（最终版）

| 阶段 | 次数 | 核心问题 |
|------|------|----------|
| CLI Tools 下载 | 5 | 900MB zip 嵌套目录、权限、分片 |
| 环境配置 | 4 | npmrc、DEVECO_SDK_HOME、ohpm registry |
| hvigor 构建 | 6 | plugin 版本匹配、JSON5 配置 |
| 签名 - 密码格式 | 4 | 明文 vs hex vs 二进制 |
| 签名 - Material 缓存 | 3 | 旧 material 文件残留 |
| 签名 - 密码不匹配 | 8+ | material 加密的密码 ≠ p12 密码 |

## 总结：30 次失败的分布

| 阶段 | 失败次数 | 耗时 | 核心问题 |
|------|----------|------|----------|
| CLI Tools 下载 | 5 | ~2h | 文件大、路径嵌套、权限 |
| 环境配置 | 4 | ~1h | npmrc、环境变量、注册表 |
| 构建系统 hvigor | 6 | ~1h | 版本兼容、配置格式、模块声明 |
| 签名配置 | 4 | ~30min | 字段缺失、密码长度、material 结构 |
| ArkTS 语法 | 5 | ~30min | in/any/spread/Object.assign 禁用 |
| API 类型系统 | 6 | ~30min | AssetMap 类型、API 不匹配文档 |

## 可复用的 GitHub Actions 配置

最终可用的 workflow 要点：

```yaml
env:
  COMMANDLINE_TOOLS_VERSION: "6.1.0.830"

steps:
  # 1. 缓存 CLI Tools（避免每次下载 900MB）
  - uses: actions/cache@v4
    with:
      path: /opt/command-line-tools
      key: harmonyos-cli-${{ env.COMMANDLINE_TOOLS_VERSION }}

  # 2. 下载 + 解压 + 权限
  - run: |
      cd /tmp
      wget -nv "${{ env.CLI_TOOLS_RELEASE }}/commandline-tools.zip.part_aa"
      wget -nv "${{ env.CLI_TOOLS_RELEASE }}/commandline-tools.zip.part_ab"
      wget -nv "${{ env.CLI_TOOLS_RELEASE }}/commandline-tools.zip.part_ac"
      cat commandline-tools.zip.part_* > commandline-tools.zip
      sudo mkdir -p /opt/command-line-tools
      sudo unzip -q commandline-tools.zip -d /tmp/cli-extract
      sudo cp -r /tmp/cli-extract/command-line-tools/. /opt/command-line-tools/
      sudo chmod -R 755 /opt/command-line-tools

  # 3. 环境变量
  - run: |
      echo "COMMANDLINE_TOOL_DIR=/opt/command-line-tools" >> $GITHUB_ENV
      echo "DEVECO_SDK_HOME=/opt/command-line-tools/sdk" >> $GITHUB_ENV
      echo "/opt/command-line-tools/ohpm/bin" >> $GITHUB_PATH
      echo "/opt/command-line-tools/hvigor/bin" >> $GITHUB_PATH

  # 4. npmrc（必须！）
  - run: |
      cat > ~/.npmrc << 'EOF'
      registry=https://registry.npmjs.org/
      @ohos:registry=https://repo.huaweicloud.com/repository/npm/
      EOF

  # 5. 签名文件（从 Secrets 解码）
  - run: |
      echo "$P12_BASE64" | base64 -d > signing/arkvault.p12
      echo "$CER_BASE64" | base64 -d > signing/arkvault.cer
      # ... material 文件

  # 6. 构建
  - run: hvigorw assembleHap --mode module -p product=default
```

## 给后来者的建议

1. **先装 DevEco Studio，导出一个能跑的项目**——然后对比 CI 环境缺什么
2. **hvigor 版本和 plugin 版本必须匹配**——5.x 配 5.x，6.x 配 6.x
3. **ArkTS 不是 TypeScript**——开发前通读限制文档
4. **API 以类型定义为准**——文档可能是旧的
5. **CLI Tools 缓存**——每次下载 900MB 太慢
6. **签名密码 32+ 字符**——华为的安全要求
7. **p12 绝对不能提交到 git**——用 Secrets + base64

## 最终解决方案：hap-sign-tool.jar

### 为什么 hvigor 内置签名不行

hvigor 的内置签名需要 material 文件加密密码，但 AGC 导出的 material 和 p12 密码不匹配（material 加密的是二进制随机密码，p12 用的是用户设的文本密码）。

### 正确方案

用 `hap-sign-tool.jar`（命令行签名工具）替代 hvigor 内置签名：

1. **构建**：`hvigorw assembleHap` 生成 unsigned HAP
2. **签名**：`java -jar hap-sign-tool.jar sign-app` 签名

```bash
java -jar hap-sign-tool.jar sign-app \
  -mode localSign \
  -keyAlias arkvault \
  -keyPwd "密码" \
  -appCertFile cert.cer \
  -profileFile profile.p7b \
  -inFile unsigned.hap \
  -signAlg SHA256withECDSA \
  -keystoreFile keystore.p12 \
  -keystorePwd "密码" \
  -outFile signed.hap \
  -compatibleVersion 12 \
  -signCode 1
```

### 关键发现

- `hap-sign-tool` 从 p7b Profile 中自动提取开发者证书，不需要单独的 cer 文件
- `-appCertFile` 可以用 CA 根证书（用于验证证书链）
- p12 密码是明文，不需要 material 加密
- 不依赖 hvigor 的 decipher-util 解密链路

### CI 流程

```
push → hvigorw assembleHap → unsigned.hap → hap-sign-tool sign-app → signed.hap → upload artifact
```

### 需要的 GitHub Secrets

| Secret | 内容 |
|--------|------|
| `SIGNING_P12` | p12 文件 (base64) |
| `P12_PASSWORD` | p12 密码 (明文) |
| `SIGNING_CER` | CA 根证书 (base64) |
| `SIGNING_PROFILE` | Profile p7b 文件 (base64) |
