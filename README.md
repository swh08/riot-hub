<div align="center">

<img src="frontend/src/assets/brand/riot-hub-logo.png" alt="Riot Hub" width="300" />

### A self-hosted content hub for Riot Games titles

Manage Teamfight Tactics seasons and team compositions today —<br/>
League of Legends and VALORANT modules are on the roadmap.

<p>
  <img alt="Vue 3" src="https://img.shields.io/badge/Vue-3-42b883?logo=vuedotjs&logoColor=white" />
  <img alt="Vuetify 3" src="https://img.shields.io/badge/Vuetify-3-1867c0?logo=vuetify&logoColor=white" />
  <img alt="Vite 7" src="https://img.shields.io/badge/Vite-7-646cff?logo=vite&logoColor=white" />
  <img alt="Django 5" src="https://img.shields.io/badge/Django-5-092e20?logo=django&logoColor=white" />
  <img alt="PostgreSQL 16" src="https://img.shields.io/badge/PostgreSQL-16-4169e1?logo=postgresql&logoColor=white" />
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ed?logo=docker&logoColor=white" />
</p>

**English** | [简体中文](docs/README.zh-CN.md)

</div>

---

## Overview

Riot Hub opens on a game selection page and routes each title into its own module. Teamfight Tactics is fully supported: season management, composition upload and editing, S/A/B tier organization, one-click composition codes, per-season background images, and a responsive image viewer. League of Legends and VALORANT appear as planned cards.

## Highlights

- **Hub landing page** with game cards — swipeable stacked cards with smooth gestures on mobile, a grid on desktop.
- **Season-aware browsing** with a global season selector in the toolbar.
- **Searchable navigation** across composition names and custom keywords.
- **Tier board** (S / A / B) powered by drag-and-drop; changes persist through the backend API.
- **Composition management** — upload, edit metadata, delete, refresh, one-click code copy.
- **Season management** — create seasons, switch the viewed season, set the active season, and upload a custom background image per season (stored on the backend, shared across devices).
- **Responsive layout** that adapts the drawer, toolbar, and management views from desktop to mobile.

## Architecture

Riot Hub is a **modular monolith**: one frontend image, one backend image, one database, deployed with a single `docker-compose.yml`. Games are isolated by directory and namespace instead of by service:

- Every game uses a three-letter id (`tft`, `lol`, `val`) across frontend routes (`/tft`), API prefixes (`/api/tft/`), Django apps, and database table prefixes (`tft_*`).
- Game modules never import each other, and models never reference another game's models. Shared code, if ever needed, goes into a dedicated `common` layer that games depend on one-way.
- Adding a game means creating a Django app mounted at `/api/<game>/`, a `pages/<game>/` route tree with its own layout, store, and components, and enabling its card in `src/constants/games.js`. No compose, nginx, or CI changes are required.

See [docs/hub-refactor-architecture.md](docs/hub-refactor-architecture.md) for the full design document.

### Project Structure

```text
riot-hub/
  frontend/
    src/
      api/                 HTTP clients for backend resources
      components/
        hub/               Hub game cards and the mobile card stack
        tft/               TFT viewer, cards, dialogs, tier board, and settings UI
      constants/           Shared frontend constants (game cards, settings sections)
      layouts/             default.vue (hub shell) and tft.vue (TFT navigation layout)
      pages/
        index.vue          Hub game selection page
        tft/               TFT routes (/tft, /tft/settings)
      plugins/             Vuetify, router, Pinia, and app plugin registration
      stores/              Pinia stores
      styles/              Vuetify and global style settings
  backend/
    config/                Django project settings and root URLs
    tft/                   TFT app: seasons and team composition APIs
  docs/                    Architecture and translated documentation
```

## Quick Start

### Docker Compose (production-like)

```bash
cp .env.production.example .env   # then edit secrets and hosts
docker compose up -d
```

The frontend is served on port `8080`, the backend API on port `8000`, and PostgreSQL data persists under `./data/`.

### Local Development

Requirements: Node.js 20+, Python 3.10+, and a reachable PostgreSQL instance.

Backend:

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # or source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:3000` and proxies `/api` to `http://localhost:8000`.

### Frontend Scripts

Run from `frontend/`:

| Command           | Description                                      |
| ----------------- | ------------------------------------------------ |
| `npm run dev`     | Start the Vite dev server with HMR               |
| `npm run build`   | Build the production bundle into `frontend/dist` |
| `npm run preview` | Serve the production build locally               |
| `npm run lint`    | Run ESLint with auto-fix                         |

## API Reference

The frontend uses Axios with `baseURL: '/api'`. All TFT endpoints live under the `/api/tft/` namespace.

### Compositions

- `GET /api/tft/images/?season=<version>` — list composition images for a season.
- `POST /api/tft/images/` — upload a composition image (multipart form data).
- `PATCH /api/tft/images/:uid/` — update composition metadata such as code, keywords, or tier.
- `DELETE /api/tft/images/:uid/` — delete a composition image.

### Seasons

- `GET /api/tft/seasons/` — list seasons, each including its `background` image URL (or `null`).
- `POST /api/tft/seasons/` — create a season.
- `GET /api/tft/seasons/current/` — fetch the active season.
- `POST /api/tft/seasons/:uid/set_active/` — mark a season as active.
- `POST /api/tft/seasons/:uid/background/` — upload or replace the season background image (multipart field `background`, max 10 MB).
- `DELETE /api/tft/seasons/:uid/background/` — remove the season background image and its stored file.
- `POST /api/tft/seasons/:uid/import-compositions/` — sync the season folder and its `metadata.json` into the database.
- `GET /api/tft/seasons/:uid/composition-metadata/` — download the selected season metadata as a JSON backup.
- `POST /api/tft/seasons/:uid/composition-metadata/` — upload a metadata JSON backup and restore its composition state.

The first composition sync creates `media/season/<version>/metadata.json`. Each entry
contains the image filename, composition code, tier, and keywords:

```json
{
  "schema_version": 1,
  "season": 17,
  "compositions": [
    {
      "filename": "duelist.png",
      "comp_code": "SET17-DUELIST",
      "tier_level": 0,
      "tier_display": "S",
      "keywords": ["fast 8", "reroll"]
    }
  ]
}
```

Edit the file and run the sync again to update database records matched by filename.
Image files referenced by metadata must exist in the season folder; records omitted
from metadata are not deleted automatically. Uploading, editing, or deleting a
composition through the API rewrites the season metadata immediately from the latest
database state. Database-generated composition IDs are intentionally not stored. The
integer `season` must match the selected season or the restore is rejected before any
database changes are made.

The composition settings toolbar exposes the same workflow as **Export Backup** and
**Import Restore**. Import validates the JSON, season number, and referenced image
files before syncing. If database synchronization fails, the server restores the
previous metadata file. Restore is non-destructive: database records omitted from the
backup are not automatically deleted.

### Frontend Data Mapping

The frontend maps backend composition records into this internal shape:

- `uid` — unique composition identifier.
- `filename` — display name source.
- `comp_code` — composition code copied by users.
- `tier_level` — numeric tier level, where `0` is S, `1` is A, and `2` is B.
- `tier_display` — display label for the tier.
- `keywords` — searchable tags.
- `image_url` or `image` — image URL used by the viewer.

## User Flow

1. Open the Hub landing page and select TFT to enter the composition manager at `/tft`.
2. Select a season from the toolbar.
3. Browse compositions from the side drawer, search by name or keyword, and click an item to preview its image.
4. Copy a composition code from the drawer when needed.
5. Open Settings > Composition Management to upload images, edit metadata, delete entries, refresh data, or drag cards between tiers.
6. Open Settings > Season Management to create seasons, switch the viewed season, activate a season, or upload a season background image.
7. Use the toolbar menu's "Back to Hub" entry to return to the game selection page.

## Frontend Notes

- Routes are generated from `src/pages/**/*.vue` through `unplugin-vue-router`.
- Layouts are applied through `vite-plugin-vue-layouts-next`: the Hub page uses the minimal `default` layout, TFT pages declare `layout: tft` in their route blocks.
- Page titles come from `meta.title` in each page's route block; the router falls back to "Riot Hub".
- Vuetify components are auto-imported by `vite-plugin-vuetify` and `unplugin-vue-components`.
- Shared TFT state lives in `src/stores/tft.js`.
- The development proxy target is configured in `frontend/vite.config.mjs`.

## Roadmap

The Hub landing page and per-game namespacing are in place. Planned expansion areas:

- **League of Legends** — champion builds, matchup notes, rune pages, item sets, and strategy references.
- **VALORANT** — agent lineups, map notes, utility setups, team compositions, and tactical resources.
- Reusable upload, search, tagging, and organization tools shared across game modules.

## Troubleshooting

- If the UI loads but no compositions appear, confirm that the backend is running on `http://localhost:8000` and that `/api/tft/seasons/` returns at least one season.
- If uploads fail, check that the selected season is valid and that the backend accepts multipart form fields named `image`, `comp_code`, `tier_level`, `tier_display`, and `keywords`.
- If drag-and-drop tier changes roll back, inspect the `PATCH /api/tft/images/:uid/` response and backend validation errors.
- If a season background does not show up, check the `background` field returned by `/api/tft/seasons/` and confirm the media file is reachable under `/media/`.

## Deployment

Build the frontend with `npm run build` and deploy `frontend/dist` behind a web server, or use the provided Docker images. In production, make sure `/api` is routed to the backend service.

### Docker Publishing (CI)

The GitHub workflow expects the following repository configuration:

- `DOCKERHUB_USERNAME` secret — Docker Hub login username.
- `DOCKERHUB_TOKEN` secret — Docker Hub access token.
- Optional `DOCKERHUB_NAMESPACE` repository variable — namespace or organization for published images.

Published images: `${DOCKERHUB_NAMESPACE}/riot-hub-backend` and `${DOCKERHUB_NAMESPACE}/riot-hub-frontend`.

Publishing behavior:

- Pull requests only build-check the images and do not push them.
- Documentation-only changes (`*.md`, `*.mdx`, `docs/*`, `LICENSE`, `LICENSE.*`) skip Docker builds and publishing.
- Pushes to `main` automatically create the next patch version tag, starting at `v0.1.0` when no prior `v*` tag exists.
- Each release publishes `latest` plus the new version tag for each image.

## License

No license file is currently included in this repository. Add one before publishing or distributing the project.
