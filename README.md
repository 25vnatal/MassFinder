# Find a Mass

A web app for finding Catholic parishes and Mass times in Karnataka. People can search by town, pincode, parish name or their current location, then filter by day, time of day and Mass language.

It is a static site with no server or database, so it can be hosted for free on GitHub Pages.

## What's in this repository

| Path | What it is |
|---|---|
| `site/index.html` | The app (HTML, CSS and JavaScript in one file) |
| `site/data/parishes.json` | Parish data the app reads. Generated from the workbook; don't edit by hand |
| `site/config.js` | Settings, including the street-map key |
| `site/data/karnataka.geojson` | District outlines, used when no street-map key is set |
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

### Turn on the street map

The site works straight away with a plain district map. For streets, landmarks and parish clusters on a real map, add a free MapTiler key:

1. Create a free account at https://cloud.maptiler.com and copy the default key from **Account → API keys**.
2. On that key, add your site's address under **Allowed HTTP origins** (for example `your-org.github.io` and your own domain). Browser map keys are always visible in the page, so this is what stops other sites from using yours.
3. In your GitHub repository, open **Settings → Secrets and variables → Actions → Variables**, and add a variable named `MAPTILER_KEY` with the key as its value.
4. Push any change, or run the workflow from the **Actions** tab. The deploy step writes the key into `config.js`.

You can also paste the key directly into `site/config.js` instead. If the key is wrong or blocked, the app falls back to the district map and logs a note in the browser console.

`config.js` also sets the map style (`streets-v2`, with `streets-v2-dark` in dark mode). Any MapTiler style name works there, such as `basic-v2` or `bright-v2`.

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
- District outlines are from the 2011 Census boundaries.
- Street maps are © MapTiler and © OpenStreetMap contributors. The map shows this credit automatically.
