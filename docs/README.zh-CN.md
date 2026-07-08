<div align="center">

<img src="../frontend/src/assets/brand/riot-hub-logo.png" alt="Riot Hub" width="300" />

### 自托管的 Riot Games 多游戏内容中心

现已支持云顶之弈的赛季与阵容管理——<br/>
英雄联盟和无畏契约模块在规划中。

<p>
  <img alt="Vue 3" src="https://img.shields.io/badge/Vue-3-42b883?logo=vuedotjs&logoColor=white" />
  <img alt="Vuetify 3" src="https://img.shields.io/badge/Vuetify-3-1867c0?logo=vuetify&logoColor=white" />
  <img alt="Vite 7" src="https://img.shields.io/badge/Vite-7-646cff?logo=vite&logoColor=white" />
  <img alt="Django 5" src="https://img.shields.io/badge/Django-5-092e20?logo=django&logoColor=white" />
  <img alt="PostgreSQL 16" src="https://img.shields.io/badge/PostgreSQL-16-4169e1?logo=postgresql&logoColor=white" />
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ed?logo=docker&logoColor=white" />
</p>

[English](../README.md) | **简体中文**

</div>

---

## 项目简介

Riot Hub 打开后首先是游戏选择页，每个游戏进入各自独立的模块。云顶之弈已完整支持：赛季管理、阵容上传与编辑、S/A/B 强度分级、一键复制阵容码、每赛季独立背景图，以及响应式大图预览。英雄联盟和无畏契约以规划中卡片展示。

## 功能亮点

- **Hub 游戏选择首页**——手机上是可滑动切换的堆叠卡片（丝滑手势动效），桌面端为网格布局。
- **按赛季浏览**，顶部工具栏提供全局赛季选择器。
- **搜索导航**，支持按阵容名称和自定义关键词过滤。
- **强度看板**（S / A / B），拖拽调整并通过后端 API 持久化。
- **阵容管理**——上传、编辑元数据、删除、刷新、一键复制阵容码。
- **赛季管理**——创建赛季、切换查看赛季、设置激活赛季，并为每个赛季上传自定义背景图（保存在后端，跨设备共享）。
- **响应式布局**，侧边栏、工具栏和管理页面自适应桌面与移动端。

## 架构说明

Riot Hub 采用**模块化单体**架构：单前端镜像 + 单后端镜像 + 单数据库，一个 `docker-compose.yml` 一条命令部署。游戏之间靠目录和命名空间隔离，而不是拆分服务：

- 每个游戏使用三字母标识（`tft`、`lol`、`val`），贯穿前端路由（`/tft`）、API 前缀（`/api/tft/`）、Django app 和数据库表前缀（`tft_*`）。
- 游戏模块之间禁止互相 import，model 之间禁止跨游戏外键。若确有共享需求，建立单向依赖的 `common` 层。
- 新增游戏的标准动作：创建挂在 `/api/<game>/` 下的 Django app，建立 `pages/<game>/` 路由树及配套布局、store、组件，并在 `src/constants/games.js` 中启用对应卡片。无需修改 compose、nginx 或 CI。

完整设计文档见 [hub-refactor-architecture.md](hub-refactor-architecture.md)。

### 项目结构

```text
riot-hub/
  frontend/
    src/
      api/                 后端接口封装
      components/
        hub/               Hub 游戏卡片与移动端堆叠卡片
        tft/               TFT 查看、卡片、弹窗、强度看板和设置组件
      constants/           前端共享常量（游戏卡片、设置分区）
      layouts/             default.vue（Hub 极简壳）与 tft.vue（TFT 导航布局）
      pages/
        index.vue          Hub 游戏选择页
        tft/               TFT 路由（/tft、/tft/settings）
      plugins/             Vuetify、Router、Pinia 等插件注册
      stores/              Pinia 状态管理
      styles/              Vuetify 与全局样式配置
  backend/
    config/                Django 项目配置与根路由
    tft/                   TFT app：赛季与阵容 API
  docs/                    架构文档与翻译文档
```

## 快速开始

### Docker Compose（类生产环境）

```bash
cp .env.production.example .env   # 编辑其中的密钥和域名
docker compose up -d
```

前端服务在 `8080` 端口，后端 API 在 `8000` 端口，PostgreSQL 数据持久化在 `./data/` 目录。

### 本地开发

环境要求：Node.js 20+、Python 3.10+、可访问的 PostgreSQL 实例。

后端：

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # Linux/macOS 用 source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

Vite 开发服务器运行在 `http://localhost:3000`，并将 `/api` 代理到 `http://localhost:8000`。

### 前端脚本

以下命令在 `frontend/` 目录执行：

| 命令              | 说明                               |
| ----------------- | ---------------------------------- |
| `npm run dev`     | 启动 Vite 开发服务器（支持热更新） |
| `npm run build`   | 构建生产版本到 `frontend/dist`     |
| `npm run preview` | 本地预览生产构建结果               |
| `npm run lint`    | 运行 ESLint 并自动修复             |

## API 参考

前端 Axios 使用 `baseURL: '/api'`，所有 TFT 接口位于 `/api/tft/` 命名空间下。

### 阵容接口

- `GET /api/tft/images/?season=<version>`——获取指定赛季的阵容图片列表。
- `POST /api/tft/images/`——使用 multipart form data 上传阵容图片。
- `PATCH /api/tft/images/:uid/`——更新阵容码、关键词或强度等元数据。
- `DELETE /api/tft/images/:uid/`——删除阵容图片。

### 赛季接口

- `GET /api/tft/seasons/`——获取赛季列表，每条记录包含 `background` 背景图 URL（无背景时为 `null`）。
- `POST /api/tft/seasons/`——创建赛季。
- `GET /api/tft/seasons/current/`——获取当前激活赛季。
- `POST /api/tft/seasons/:uid/set_active/`——设置激活赛季。
- `POST /api/tft/seasons/:uid/background/`——上传或替换赛季背景图（multipart 字段 `background`，最大 10 MB）。
- `DELETE /api/tft/seasons/:uid/background/`——删除赛季背景图及其存储文件。

### 前端数据映射

前端会将后端阵容记录映射为以下内部字段：

- `uid`——阵容唯一标识。
- `filename`——显示名称来源。
- `comp_code`——用户复制的阵容码。
- `tier_level`——数字强度等级，`0` 为 S，`1` 为 A，`2` 为 B。
- `tier_display`——强度展示名称。
- `keywords`——可搜索关键词。
- `image_url` 或 `image`——用于展示的图片地址。

## 主要使用流程

1. 打开 Hub 游戏选择页，点击 TFT 卡片进入 `/tft` 阵容管理。
2. 在顶部栏选择需要查看的赛季。
3. 在侧边栏浏览阵容，按名称或关键词搜索，并点击阵容查看大图。
4. 需要时在侧边栏一键复制阵容码。
5. 进入设置中心的阵容管理，上传图片、编辑信息、删除阵容、刷新数据，或将卡片拖拽到不同强度栏。
6. 进入设置中心的赛季管理，创建赛季、切换查看赛季、设置激活赛季，或上传赛季背景图。
7. 通过顶部菜单的「返回 Hub」回到游戏选择页。

## 前端说明

- 路由由 `src/pages/**/*.vue` 通过 `unplugin-vue-router` 自动生成。
- 布局由 `vite-plugin-vue-layouts-next` 处理：Hub 页使用极简的 `default` 布局，TFT 页面在 route block 中声明 `layout: tft`。
- 页面标题来自各页面 route block 中的 `meta.title`，未声明时回落到「Riot Hub」。
- Vuetify 组件通过 `vite-plugin-vuetify` 和 `unplugin-vue-components` 自动导入。
- TFT 相关共享状态集中在 `src/stores/tft.js`。
- 开发环境代理配置位于 `frontend/vite.config.mjs`。

## 路线图

Hub 游戏选择页和按游戏划分的命名空间已经就绪。计划扩展方向：

- **英雄联盟**——英雄出装、对位笔记、符文页、装备方案和策略资料。
- **无畏契约**——特工点位、地图笔记、技能道具布置、阵容搭配和战术资料。
- 将上传、搜索、标签和内容整理能力复用于各游戏模块。

## 常见问题

- 如果页面能打开但没有阵容，请确认后端运行在 `http://localhost:8000`，并且 `/api/tft/seasons/` 至少返回一个赛季。
- 如果上传失败，请确认当前已选择有效赛季，且后端支持 `image`、`comp_code`、`tier_level`、`tier_display`、`keywords` 这些 multipart 字段。
- 如果拖拽调整强度后回滚，请检查 `PATCH /api/tft/images/:uid/` 的响应和后端校验错误。
- 如果赛季背景没有显示，请检查 `/api/tft/seasons/` 返回的 `background` 字段，并确认对应媒体文件可以通过 `/media/` 访问。

## 部署

使用 `npm run build` 构建前端并将 `frontend/dist` 部署到 Web 服务器，或直接使用提供的 Docker 镜像。生产环境需要确保 `/api` 能正确转发到后端服务。

### Docker 发布（CI）

GitHub workflow 需要以下仓库配置：

- `DOCKERHUB_USERNAME` secret——Docker Hub 登录用户名。
- `DOCKERHUB_TOKEN` secret——Docker Hub access token。
- 可选 `DOCKERHUB_NAMESPACE` repository variable——发布镜像使用的命名空间或组织名。

发布的镜像：`${DOCKERHUB_NAMESPACE}/riot-hub-backend` 和 `${DOCKERHUB_NAMESPACE}/riot-hub-frontend`。

发布行为：

- Pull request 只构建检查镜像，不推送。
- 纯文档改动（`*.md`、`*.mdx`、`docs/*`、`LICENSE`、`LICENSE.*`）会跳过 Docker 构建与发布。
- 推送到 `main` 会自动创建下一个 patch 版本标签；仓库没有历史 `v*` 标签时从 `v0.1.0` 开始。
- 每次发布会为每个镜像推送 `latest` 和新的版本标签。

## 许可证

当前仓库暂未包含许可证文件。公开发布或分发前建议补充许可证。
