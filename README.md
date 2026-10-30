# Find a Mass

A web app for finding Catholic parishes and Mass times in Karnataka. People can search by town, pincode, parish name or their current location, then filter by day, time of day and Mass language.

It is a static site with no server or database, so it can be hosted for free on GitHub Pages.

## What's in this repository

| Path | What it is |
|---|---|
| `site/index.html` | The app (HTML, CSS and JavaScript in one file) |
| `site/data/parishes.json` | Parish data the app reads. Generated from the workbook; don't edit by hand |
| `site/config.js` | Settings, including the street-map key |
| `site/vendor/maplibre-gl/` | MapLibre GL JS 4.7.1, the open-source map library (BSD licence) |
| `data-source/parish_data.xlsx` | The master data. Edit this one |
| `scripts/build_json.py` | Turns the workbook into `parishes.json` and checks it for mistakes |
| `scripts/geocode.py` | Improves map pins using Google or OpenStreetMap |
| `.github/workflows/deploy.yml` | Rebuilds the data and publishes the site on every push to `main` |

## Put it online with GitHub Pages

1. Create a new repository on GitHub (it can be public or private, though Pages on a private repo needs a paid plan).
2. Upload the contents of this folder, either by dragging the files into the GitHub web page or with:
   ```bash
   git init
   git add .
   git commit -m "Find a Mass"
   git branch -M main
   git remote add origin https://github.com/YOUR-ORG/find-a-mass.git
   git push -u origin main
   ```
3. On GitHub, open **Settings → Pages**, and under **Build and deployment** set **Source** to **GitHub Actions**.
4. Open the **Actions** tab. The "Build data and deploy site" run will finish in about a minute, and the site appears at `https://YOUR-ORG.github.io/find-a-mass/`.

### The street map

The map uses [OpenFreeMap](https://openfreemap.org), a free street-map service built on OpenStreetMap data. It needs no account, no API key and has no limits on map views, so it works as soon as the site is deployed.

To change the look, edit `mapStyleUrl` in `site/config.js`. OpenFreeMap offers `liberty` (the default, detailed and colourful), `bright` (classic road-map colours) and `positron` (pale and minimal, so the parish pins stand out most). Any other MapLibre-compatible style URL also works.

OpenFreeMap's public service is offered as-is, without an uptime guarantee. If its map can't load, the app switches to OpenStreetMap's standard map automatically, so search, filters and parish details keep working. If the map becomes critical to ParishConnect, you can self-host OpenFreeMap or move to a paid provider by changing that one URL.

To use your own domain (for example `mass.parishconnect.in`), add it under **Settings → Pages → Custom domain** and create the DNS record GitHub shows you.

## Update parish data or Mass times

1. Edit `data-source/parish_data.xlsx`. The README sheet inside it explains each column.
2. Commit and push the workbook (or upload it through the GitHub web page).
3. The Action rebuilds `parishes.json` and redeploys. If the workbook has a mistake, such as a wrong day name or a Mass linked to an unknown parish, the run fails and its log lists exactly what to fix. The live site keeps the previous version until it's fixed.

To check your changes before pushing:

```bash
pip install -r requirements.txt
python scripts/build_json.py data-source/parish_data.xlsx site/data/parishes.json
```

## Improve the map pins

Most pins are approximate (the nearest post office). For exact church locations:

```bash
python scripts/geocode.py data-source/parish_data.xlsx --google YOUR_GOOGLE_API_KEY
```

You need a Google Cloud project with the Geocoding API enabled. Never commit the API key to the repository. The script only needs it on your own computer.

## Run it on your computer

The app loads its data with `fetch`, so it must be served by a web server rather than opened by double-clicking the file:

```bash
cd site
python -m http.server 8000
```

Then open http://localhost:8000.

## Hosting elsewhere

The `site` folder is the whole website. It also works on Netlify, Cloudflare Pages, Vercel or any ordinary web host: upload the folder, or point the host at this repository with `site` as the publish directory. Run `scripts/build_json.py` before uploading if you edited the workbook.

## Data notes

- Parish details come from diocesan directories (Bangalore, Mangalore, Mysore, Belgaum, Karwar, Bellary, Chikmagalur).
- Map pins come from the India Post office directory (open data from data.gov.in). Each pin's precision is stored with it, and the app tells visitors when a pin is approximate.
- Street maps: OpenFreeMap, © OpenMapTiles, © OpenStreetMap contributors. The map shows this credit automatically; please don't hide it.
