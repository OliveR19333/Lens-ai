# TNC Tool Stack — Vetted Libraries & Repos

The fixed toolbox for every TNC build. All open source unless noted.

## Core (every site)

| Tool | Repo | Role |
|---|---|---|
| React 19 + Vite | — | App framework |
| Tailwind CSS | — | Styling |
| **React Bits** | [DavidHDev/react-bits](https://github.com/DavidHDev/react-bits) | 110+ animated components (text effects, backgrounds, cards, grids). Copy-paste ownership model — components live in our repo and get customized per brand. ~35k stars. |
| **Anime.js v4** | [juliangarnier/anime](https://github.com/juliangarnier/anime) | Animation engine for DOM, SVG, and (v4.5+) three.js objects via the built-in adapter. Modular imports keep bundles small. |

## Motion tier additions

| Tool | Repo | Role |
|---|---|---|
| GSAP + ScrollTrigger | [greensock/GSAP](https://github.com/greensock/GSAP) | Scroll choreography, pinning, scrubbing (free for standard use since 2025) |
| Lenis | [darkroomengineering/lenis](https://github.com/darkroomengineering/lenis) | Smooth scrolling that plays well with ScrollTrigger |

## 3D Premium tier additions

| Tool | Repo | Role |
|---|---|---|
| three.js | [mrdoob/three.js](https://github.com/mrdoob/three.js) | 3D engine |
| React Three Fiber | [pmndrs/react-three-fiber](https://github.com/pmndrs/react-three-fiber) | React renderer for three.js |
| drei | [pmndrs/drei](https://github.com/pmndrs/drei) | R3F helpers: cameras, controls, loaders, environment, text |
| Structural reference | [adrianhajdin/3d-portfolio](https://github.com/adrianhajdin/3d-portfolio), [adrianhajdin/project_3D_developer_portfolio](https://github.com/adrianhajdin/project_3D_developer_portfolio) | Proven R3F + GSAP site structures to adapt (never ship as-is) |

## Visual editor (optional, for client self-service later)

Evaluated open-source builders — none replaces the custom pipeline, but if TNC
later offers a "client edits their own content" add-on:

| Tool | Repo | Verdict |
|---|---|---|
| GrapesJS | [GrapesJS/grapesjs](https://github.com/GrapesJS/grapesjs) | Framework for embedding a drag-drop editor into our own product (~26k stars). Best if TNC productizes the builder. |
| Puck | [puckeditor/puck](https://github.com/puckeditor/puck) | Embeddable React visual editor — drops into Next.js/React sites; pairs naturally with our React Bits components. Best near-term fit. |
| Webstudio | [webstudio-is/webstudio](https://github.com/webstudio-is/webstudio) | Open-source Webflow alternative (AGPL). Full standalone platform — heavier than we need per-client. |
| Onlook | [onlook-dev/onlook](https://github.com/onlook-dev/onlook) | Visual editor for React apps, AI-assisted. Worth watching. |

**Decision:** custom code pipeline first; revisit Puck when a client asks for
self-serve editing.

## Asset generation & deploy — Higgsfield MCP

| Capability | Tool |
|---|---|
| Brand imagery, heroes, covers | `generate_image` → `upscale_image` |
| Hero motion loops, launch videos | `generate_video`, `upscale_video` |
| Image → 3D mesh (GLB) for R3F scenes | `generate_3d` |
| Cutouts, uncrops, aspect changes | `remove_background`, `outpaint_image`, `reframe` |
| Create + deploy client site (SSR Cloudflare Worker, own subdomain, zero Higgsfield branding) | `create_website` (`type: "website"`) → `deploy_website` |
| Site repo access, secrets, status | `website_repo_access`, `website_secrets`, `website_status` |

Rule from the Higgsfield flow: `type: "website"` builds must have a fully
independent brand and cannot include AI-generation features in the shipped
site itself (generation is a build-time tool for us, not a runtime feature
for site visitors). Sites that need runtime generation are `type: "app"`.
