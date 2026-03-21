# Chunithm 到 MuNET JSON 转换工具

## 简介

将 Chunithm 成绩数据转换为 MuNET 可导入的 JSON 文件。

提供两种使用方式：

| 方式 | 说明 |
|------|------|
| **在线版** | 打开网页即用，支持 API 获取 / CSV 上传 / 成绩可视化 |
| **命令行** | `python main.py <子命令> [参数]` |

**在线版地址**: https://munet-oss.github.io/chunithm-data-converter/

---

## 在线版 (Web)

无需安装任何依赖，浏览器打开即可使用。

### 功能

- **在线转换** — 输入落雪/水鱼令牌直接获取成绩并转换，或上传 CSV 文件转换
- **成绩可视化** — 上传 MuNET JSON 查看玩家信息、成绩统计图表、曲目详情

### 本地开发

```bash
cd web
npm install
npm run dev
```

构建产物输出到 `web/dist/`，推送到 `master` 分支后 GitHub Actions 自动部署到 GitHub Pages。

---

## 命令行版 (CLI)

## 环境配置

在项目根目录创建 `.env` 文件（仅 API 开发者模式需要）：

```env
LXNS_DEVELOPER_TOKEN=           # 落雪开发者令牌
SHUIYU_DEVELOPER_TOKEN=         # 水鱼开发者令牌
```

### 令牌获取方式

| 令牌 | 获取方式 |
|------|----------|
| 落雪个人令牌 | 登录 [落雪](https://maimai.lxns.net/) → 账号详情 第三方应用 个人 API 密钥 → 通过 `--lxns-token` 传入 |
| `LXNS_DEVELOPER_TOKEN` | 在落雪平台申请开发者权限 |
| 水鱼 Import-Token | 登录 [水鱼查分器](https://www.diving-fish.com/maimaidx/prober/) → 编辑个人资料 → 生成 “成绩导入 Token” → 通过 `--lxns-token` 传入 |
| `SHUIYU_DEVELOPER_TOKEN` | 在水鱼查分器申请开发者权限 |

---

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 查看帮助
python main.py --help
python main.py api --help
python main.py csv --help

# API - 落雪个人模式
python main.py api -m lxns --lxns-token YOUR_TOKEN

# API - 落雪开发者模式
python main.py api -m lxns-dev --lxns-friend-code 1234567890

# API - 水鱼个人模式
python main.py api -m shuiyu --shuiyu-import-token YOUR_TOKEN

# API - 水鱼开发者模式
python main.py api -m shuiyu-dev --shuiyu-username "用户名"

# CSV - 自动检测格式
python main.py csv -i scores.csv

# CSV - 指定格式
python main.py csv -i scores.csv -f shuiyu -u "玩家名"

# 指定输出文件
python main.py api -m lxns --lxns-token YOUR_TOKEN -o my_export.json
```

---

## API 子命令

### 模式

| 模式 | 数据源 | 认证方式 | 说明 |
|------|--------|----------|------|
| `lxns` | 落雪 | `--lxns-token` | 获取自己的全部成绩 |
| `lxns-dev` | 落雪 | `.env` + `--lxns-friend-code` | 通过好友码获取他人数据 |
| `shuiyu` | 水鱼 | `--shuiyu-import-token` | 获取自己的全部成绩 |
| `shuiyu-dev` | 水鱼 | `.env` + `--shuiyu-username` | 获取指定用户成绩 |

### 参数

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--mode` | `-m` | **必填**，模式：`lxns` / `lxns-dev` / `shuiyu` / `shuiyu-dev` |
| `--output` | `-o` | 输出文件路径（默认: `chunithm_munet_export.json`） |
| `--test` | | 测试模式，只处理前 10 条 |
| `--lxns-token` | | 落雪个人令牌 |
| `--lxns-developer-token` | | 落雪开发者令牌 |
| `--lxns-friend-code` | | 好友码 |
| `--shuiyu-import-token` | | 水鱼 Import-Token |
| `--shuiyu-developer-token` | | 水鱼 Developer-Token |
| `--shuiyu-username` | | 水鱼用户名 |

### 水鱼 API 注意

- 缺少 `over_power`、`full_chain`、`play_time` 字段，使用默认值
- 不生成 `userPlaylogList`

---

## CSV 子命令

### 参数

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--input` | `-i` | 输入 CSV 文件路径（默认: `chunithm-scores.csv`） |
| `--output` | `-o` | 输出 JSON 文件路径（默认: 自动生成） |
| `--username` | `-u` | 用户名（默认: `Player`） |
| `--format` | `-f` | CSV 格式：`auto` / `lxns` / `shuiyu`（默认: `auto`） |

---

## 依赖

- Python 3.8+
- `requests`

## 故障排除

1. **API 认证失败**: 检查令牌是否正确
2. **水鱼 400**: Import-Token 有误或用户不存在
3. **CSV 格式错误**: 确保 UTF-8 编码
