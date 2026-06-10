---
globs:
  - "frontend/**/*.js"
  - "frontend/**/*.html"
---

- No external JS libraries except Chart.js (already loaded via CDN in index.html)
- All API calls go through `api.js` — never use fetch() directly in app.js
- All pages are sections inside index.html — do not create separate HTML files
- CSS variables are defined in :root in style.css — use them, do not hardcode colors
- The dark theme palette: --bg #0f0f13, --surface #1a1a22, --accent #f97316
- heatmap.js handles all SVG rendering — do not manipulate SVG paths elsewhere
