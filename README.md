# Riot Hub

Riot Hub is a Vue 3 + Vuetify web client for managing and browsing Teamfight Tactics composition screenshots. The current application focuses on TFT season management, composition upload and editing, tier organization, quick composition-code copying, and a responsive viewer for selected composition images.

## Features

- Season-aware TFT composition browsing with a global season selector.
- Searchable side navigation for composition names and custom keywords.
- Large image viewer for the currently selected composition.
- Composition management page with upload, refresh, edit, delete, and drag-and-drop tier updates.
- S / A / B tier board powered by `vuedraggable`, with tier changes persisted through the backend API.
- Season management page for creating seasons, switching the viewed season, setting the active season, and assigning local custom background images per season.
- One-click copy for composition codes.
- Responsive Vuetify layout that adapts the drawer, toolbar, and management views for desktop and mobile screens.

## Tech Stack

- Vue 3 with `<script setup>`
- Vite 7
- Vuetify 3
- Pinia
- Vue Router with file-based auto routes
- Axios
- Sass
- `vuedraggable` for tier-board drag and drop
- ESLint with Vuetify configuration

## Project Structure

```text
riot-hub/
  frontend/
    src/
      api/                 HTTP clients for backend resources
      components/tft/      TFT viewer, cards, dialogs, tier board, and settings UI
      constants/           Shared frontend constants
      layouts/             Application shell and navigation layout
      pages/               File-based routes
      plugins/             Vuetify, router, Pinia, and app plugin registration
      stores/              Pinia stores
      styles/              Vuetify and global style settings
    package.json
    vite.config.mjs
```

## Requirements

- Node.js 20 or newer is recommended for Vite 7.
- npm is the expected package manager because the project includes `package-lock.json`.
- A compatible backend API should be running locally when you need real data.

## Getting Started

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:3000`.

## Available Scripts

Run these commands from `frontend/`.

```bash
npm run dev
```

Starts the Vite development server with hot module replacement.

```bash
npm run build
```

Builds the production bundle into `frontend/dist`.

```bash
npm run preview
```

Serves the production build locally for verification.

```bash
npm run lint
```

Runs ESLint with auto-fix enabled.

## Backend API Expectations

The frontend uses Axios with `baseURL: '/api'`. During development, Vite proxies `/api` to `http://localhost:8000`.

Expected composition endpoints:

- `GET /api/images/?season=<version>`: list composition images for a season.
- `POST /api/images/`: upload a composition image with multipart form data.
- `PATCH /api/images/:uid/`: update composition metadata such as code, keywords, or tier.
- `DELETE /api/images/:uid/`: delete a composition image.

Expected season endpoints:

- `GET /api/seasons/`: list seasons.
- `POST /api/seasons/`: create a season.
- `GET /api/seasons/current/`: fetch the active season.
- `POST /api/seasons/:uid/set_active/`: mark a season as active.

The frontend maps backend composition records into this internal shape:

- `uid`: unique composition identifier.
- `filename`: display name source.
- `comp_code`: composition code copied by users.
- `tier_level`: numeric tier level, where `0` is S, `1` is A, and `2` is B.
- `tier_display`: display label for the tier.
- `keywords`: searchable tags.
- `image_url` or `image`: image URL used by the viewer.

## Main User Flows

1. Open the app and let it load available seasons and the active season.
2. Select a season from the toolbar.
3. Browse compositions from the side drawer, search by name or keyword, and click an item to preview its image.
4. Copy a composition code from the drawer when needed.
5. Open Settings > Composition Management to upload images, edit metadata, delete entries, refresh data, or drag cards between tiers.
6. Open Settings > Season Management to create seasons, switch the viewed season, activate a season, or set a local background image.

## Future Roadmap

Riot Hub currently focuses on Teamfight Tactics, but the long-term direction is to become a broader Riot Games companion hub. Planned expansion areas include:

- League of Legends support for champion builds, matchup notes, rune pages, item sets, and strategy references.
- VALORANT support for agent lineups, map notes, utility setups, team compositions, and tactical resources.
- A shared game selector and data model so each game can keep its own seasons, assets, tags, and management workflows.
- Reusable upload, search, tagging, and organization tools across TFT, League of Legends, and VALORANT content.

## Frontend Notes

- Routes are generated from `src/pages/*.vue` through `unplugin-vue-router`.
- Layouts are applied through `vite-plugin-vue-layouts-next`.
- Vuetify components are auto-imported by `vite-plugin-vuetify` and `unplugin-vue-components`.
- Shared TFT state lives in `src/stores/tft.js`.
- Custom season backgrounds are stored in browser `localStorage` under `riot-hub:season-backgrounds`; they are local to the browser and are not uploaded to the backend.
- The current development proxy target is configured in `frontend/vite.config.mjs`.

## Troubleshooting

- If the UI loads but no compositions appear, confirm that the backend is running on `http://localhost:8000` and that `/api/seasons/` returns at least one season.
- If uploads fail, check that the selected season is valid and that the backend accepts multipart form fields named `image`, `comp_code`, `tier_level`, `tier_display`, and `keywords`.
- If drag-and-drop tier changes roll back, inspect the `PATCH /api/images/:uid/` response and backend validation errors.
- If custom season backgrounds disappear in another browser or device, that is expected because backgrounds are stored locally.

## Deployment

Build the frontend with:

```bash
cd frontend
npm run build
```

Deploy the generated `frontend/dist` directory behind a web server. In production, make sure `/api` is routed to the backend service or replace the Axios base URL / proxy strategy to match your deployment environment.

### Docker Publishing

The GitHub workflow expects the following repository configuration for Docker image publishing:

- `DOCKERHUB_USERNAME` secret: Docker Hub login username.
- `DOCKERHUB_TOKEN` secret: Docker Hub access token.
- Optional `DOCKERHUB_NAMESPACE` repository variable: namespace or organization for published images.

Published image names:

- `${DOCKERHUB_NAMESPACE}/riot-hub-backend`
- `${DOCKERHUB_NAMESPACE}/riot-hub-frontend`

Publishing behavior:

- Pull requests only build-check the images and do not push them.
- Pushes to `main` automatically create the next patch version tag.
- Versioning starts at `v0.1.0` when the repository has no prior `v*` tags.
- If the latest git tag is `v1.2.3`, the next release becomes `v1.2.4`.
- Each release publishes `latest` and the new version tag, such as `v1.2.4`, for each image.

## License

No license file is currently included in this repository. Add one before publishing or distributing the project.

---

# Riot Hub 中文说明

Riot Hub 是一个基于 Vue 3 和 Vuetify 的 TFT 阵容管理前端。当前应用主要用于管理云顶之弈阵容截图，支持赛季管理、阵容上传与编辑、强度分级、阵容码复制，以及选中阵容的大图预览。

## 功能特性

- 按赛季浏览 TFT 阵容，顶部提供全局赛季选择器。
- 侧边栏支持按阵容名称和关键词搜索。
- 中央区域展示当前选中阵容的大图。
- 阵容管理页面支持上传、刷新、编辑、删除和拖拽调整强度。
- S / A / B 强度看板基于 `vuedraggable` 实现，拖拽后的强度变更会提交到后端。
- 赛季管理页面支持创建赛季、切换查看赛季、设置激活赛季，并为每个赛季设置本地背景图。
- 支持一键复制阵容码。
- Vuetify 响应式布局，适配桌面端和移动端。

## 技术栈

- Vue 3 与 `<script setup>`
- Vite 7
- Vuetify 3
- Pinia
- Vue Router 文件路由
- Axios
- Sass
- `vuedraggable`
- ESLint 与 Vuetify 配置

## 项目结构

```text
riot-hub/
  frontend/
    src/
      api/                 后端接口封装
      components/tft/      TFT 查看、卡片、弹窗、强度看板和设置组件
      constants/           前端共享常量
      layouts/             应用外壳、顶部栏和侧边栏布局
      pages/               文件路由页面
      plugins/             Vuetify、Router、Pinia 等插件注册
      stores/              Pinia 状态管理
      styles/              Vuetify 与全局样式配置
    package.json
    vite.config.mjs
```

## 环境要求

- 推荐使用 Node.js 20 或更新版本。
- 项目包含 `package-lock.json`，建议使用 npm。
- 如需加载真实数据，需要本地启动兼容的后端 API。

## 快速开始

从仓库根目录执行：

```bash
cd frontend
npm install
npm run dev
```

开发服务器地址为 `http://localhost:3000`。

## 可用脚本

以下命令均在 `frontend/` 目录执行。

```bash
npm run dev
```

启动 Vite 开发服务器，支持热更新。

```bash
npm run build
```

构建生产版本，输出到 `frontend/dist`。

```bash
npm run preview
```

本地预览生产构建结果。

```bash
npm run lint
```

运行 ESLint，并启用自动修复。

## 后端 API 约定

前端 Axios 使用 `baseURL: '/api'`。开发环境中，Vite 会将 `/api` 代理到 `http://localhost:8000`。

阵容相关接口：

- `GET /api/images/?season=<version>`：获取指定赛季的阵容图片列表。
- `POST /api/images/`：使用 multipart form data 上传阵容图片。
- `PATCH /api/images/:uid/`：更新阵容码、关键词或强度等元数据。
- `DELETE /api/images/:uid/`：删除阵容图片。

赛季相关接口：

- `GET /api/seasons/`：获取赛季列表。
- `POST /api/seasons/`：创建赛季。
- `GET /api/seasons/current/`：获取当前激活赛季。
- `POST /api/seasons/:uid/set_active/`：设置激活赛季。

前端会将后端阵容记录映射为以下内部字段：

- `uid`：阵容唯一标识。
- `filename`：显示名称来源。
- `comp_code`：用户复制的阵容码。
- `tier_level`：数字强度等级，`0` 为 S，`1` 为 A，`2` 为 B。
- `tier_display`：强度展示名称。
- `keywords`：可搜索关键词。
- `image_url` 或 `image`：用于展示的图片地址。

## 主要使用流程

1. 打开应用，等待赛季列表和激活赛季加载完成。
2. 在顶部栏选择需要查看的赛季。
3. 在侧边栏浏览阵容，按名称或关键词搜索，并点击阵容查看大图。
4. 需要时在侧边栏一键复制阵容码。
5. 进入设置中心的阵容管理，上传图片、编辑信息、删除阵容、刷新数据，或将卡片拖拽到不同强度栏。
6. 进入设置中心的赛季管理，创建赛季、切换查看赛季、设置激活赛季，或配置本地赛季背景图。

## 未来路线图

Riot Hub 当前聚焦 Teamfight Tactics，但长期方向是成为更完整的 Riot Games 内容管理中心。计划扩展方向包括：

- 支持 League of Legends，用于管理英雄出装、对位笔记、符文页、装备方案和策略资料。
- 支持 VALORANT，用于管理特工点位、地图笔记、技能道具布置、阵容搭配和战术资料。
- 增加统一的游戏选择器和数据模型，让每个游戏都能维护自己的赛季、素材、标签和管理流程。
- 将上传、搜索、标签和内容整理能力复用于 TFT、League of Legends 和 VALORANT。

## 前端说明

- 路由由 `src/pages/*.vue` 通过 `unplugin-vue-router` 自动生成。
- 布局由 `vite-plugin-vue-layouts-next` 处理。
- Vuetify 组件通过 `vite-plugin-vuetify` 和 `unplugin-vue-components` 自动导入。
- TFT 相关共享状态集中在 `src/stores/tft.js`。
- 自定义赛季背景保存在浏览器 `localStorage` 的 `riot-hub:season-backgrounds` 中，只在当前浏览器本地生效，不会上传到后端。
- 开发环境代理配置位于 `frontend/vite.config.mjs`。

## 常见问题

- 如果页面能打开但没有阵容，请确认后端运行在 `http://localhost:8000`，并且 `/api/seasons/` 至少返回一个赛季。
- 如果上传失败，请确认当前已选择有效赛季，且后端支持 `image`、`comp_code`、`tier_level`、`tier_display`、`keywords` 这些 multipart 字段。
- 如果拖拽调整强度后回滚，请检查 `PATCH /api/images/:uid/` 的响应和后端校验错误。
- 如果自定义赛季背景在其他浏览器或设备上不存在，这是预期行为，因为背景图只保存在本地浏览器。

## 部署

构建前端：

```bash
cd frontend
npm run build
```

将生成的 `frontend/dist` 部署到 Web 服务器。生产环境需要确保 `/api` 能正确转发到后端服务，或根据部署方式调整 Axios base URL / 代理策略。

### Docker 发布

GitHub workflow 发布 Docker 镜像时需要以下仓库配置：

- `DOCKERHUB_USERNAME` secret：Docker Hub 登录用户名。
- `DOCKERHUB_TOKEN` secret：Docker Hub access token。
- 可选 `DOCKERHUB_NAMESPACE` repository variable：发布镜像使用的命名空间或组织名。

发布的镜像名称：

- `${DOCKERHUB_NAMESPACE}/riot-hub-backend`
- `${DOCKERHUB_NAMESPACE}/riot-hub-frontend`

发布行为：

- Pull request 只构建检查镜像，不推送。
- 推送到 `main` 会自动创建下一个 patch 版本标签。
- 如果仓库没有历史 `v*` 标签，版本从 `v0.1.0` 开始。
- 如果最新 git 标签是 `v1.2.3`，下一次发布会变为 `v1.2.4`。
- 每次发布会为每个镜像推送 `latest` 和新的版本标签，例如 `v1.2.4`。

## 许可证

当前仓库暂未包含许可证文件。公开发布或分发前建议补充许可证。
