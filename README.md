# Chunithm 到 MuNET JSON 转换工具

## 简介

将 Chunithm 成绩数据转换为 MuNET 可导入的 JSON 文件。

提供三种使用方式：

| 方式 | 说明 |
|------|------|
| **在线前端** | 打开网页即用，支持 API 获取 / CSV 上传 / 成绩可视化 |
| **本地服务器** | 运行 `web.py` 启动基于 Flask 的后端，无跨域限制 |
| **命令行** | `python main.py <子命令> [参数]` |

**在线版地址**: https://munet-oss.github.io/chunithm-data-converter/

---

## 在线版 (Web)

无需安装任何依赖，浏览器打开即可使用。

### 功能

- **在线转换** — 输入落雪/水鱼令牌直接获取成绩并转换，或上传 CSV 文件转换
- **成绩可视化** — 上传 MuNET JSON 查看玩家信息、成绩统计图表、曲目详情

### 编译前端

使用 `npx` 编译前端产物：

```bash
cd web
npm install
npx vite build
```

构建产物输出到 `web/dist/`，推送到 `master` 分支后 GitHub Actions 会自动部署到 GitHub Pages。

---

## 本地服务器端 (web.py)

如果您不想处理浏览器复杂的 CORS 跨域限制，或者想自己提供无代理的后端服务，可以直接运行内置的 Flask 服务。

该方案基于 **Flask** 搭建，直接在内存层级导入底层转换核心模块，**性能极高，没有额外的磁盘 I/O**。配合前端打包，它默认会自动托管前端的静态资源。

```bash
# 1. 编译前端页面
cd web
npm install
npx vite build
cd ..

# 2. 安装 Python 依赖
pip install flask requests

# 3. 启动服务 (默认端口 5000)
python web.py
```

访问 `http://localhost:5000` 即可使用。

---

## 命令行版 (CLI)

### 环境配置

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

### 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 查看帮助
python main.py --help

# API - 落雪个人模式
python main.py api -m lxns --lxns-token YOUR_TOKEN

# API - 水鱼开发者模式
python main.py api -m shuiyu-dev --shuiyu-username "用户名"

# CSV - 自动检测格式
python main.py csv -i scores.csv
```

---

## API 子命令模式说明

| 模式 | 数据源 | 认证方式 | 说明 |
|------|--------|----------|------|
| `lxns` | 落雪 | `--lxns-token` | 获取自己的全部成绩 |
| `lxns-dev` | 落雪 | `.env` + `--lxns-friend-code` | 通过好友码获取他人数据 |
| `shuiyu` | 水鱼 | `--shuiyu-import-token` | 获取自己的全部成绩 |
| `shuiyu-dev` | 水鱼 | `.env` + `--shuiyu-username` | 获取指定用户成绩 |

### 水鱼 API 注意

- 缺少 `over_power`、`full_chain`、`play_time` 字段，默认以占位值填补
- 不生成 `userPlaylogList`

## 依赖

- Python 3.8+
- `requests`
- `flask` (仅运行 Web 服务时需要)