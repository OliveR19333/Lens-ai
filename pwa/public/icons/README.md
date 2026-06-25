# App icons

Drop PNG launcher icons here before building for production:

- `icon-192.png` — 192×192
- `icon-512.png` — 512×512 (also used as the maskable icon)

They are referenced by `vite.config.js` (`manifest.icons`) and `index.html`
(`apple-touch-icon`). Until real artwork exists, generate placeholders from
`public/favicon.svg`, e.g.:

```bash
npx @resvg/resvg-js-cli favicon.svg -w 512 -h 512 icons/icon-512.png
npx @resvg/resvg-js-cli favicon.svg -w 192 -h 192 icons/icon-192.png
```
