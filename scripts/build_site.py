"""Build the in-browser demo (GitHub Pages) with stlite: Streamlit running on Pyodide.

    python scripts/build_site.py  ->  _site/

The page downloads stlite and Pyodide from jsDelivr, then mounts the app files that sit
next to it. Nothing runs on a server.
"""
from __future__ import annotations

import json
import shutil
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / '_site'
STLITE = 'https://cdn.jsdelivr.net/npm/@stlite/browser@1.9.2/build'

FILES = ['app.py', *map(str, sorted(Path('backend').glob('*.py'))), *map(str, sorted(Path('pages').glob('*.py'))),
         'data/kepler.csv', 'data/kepler_ai.csv', 'data/tess.csv', 'data/k2.csv',
         'models/kepler_lgbm.json', 'models/kepler_metrics.json', 'assets/logo.png']

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Exoplanet Explorer · NASA Space Apps 2025</title>
  <meta name="description" content="Browse Kepler, TESS and K2 exoplanets and classify transit signals with a LightGBM model, in your browser.">
  <link rel="icon" href="assets/logo.png">
  <link rel="stylesheet" href="{stlite}/stlite.css">
  <style>
    body {{ margin: 0; background: #d6e4ff; }}
    #boot {{ position: fixed; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;
            gap: 14px; font: 15px/1.5 system-ui, sans-serif; color: #0b2e61; text-align: center; padding: 0 16px; }}
    #boot img {{ width: 84px; height: 84px; animation: spin 6s linear infinite; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  </style>
</head>
<body>
  <div id="boot"><img src="assets/logo.png" alt=""><b>Exoplanet Explorer</b>
    <span>Starting Python in your browser… the first visit takes about 20 seconds.</span></div>
  <div id="root"></div>
  <script type="module">
    import {{ mount }} from "{stlite}/stlite.js";
    const files = {files};
    const app = mount({{
      entrypoint: "app.py",
      requirements: ["pandas", "plotly"],
      files: Object.fromEntries(files.map(f => [f, {{ url: "./" + f }}])),
      streamlitConfig: {config},
    }}, document.getElementById("root"));
    new MutationObserver((_, obs) => {{
      if (document.querySelector('[data-testid="stAppViewContainer"]')) {{ document.getElementById("boot").remove(); obs.disconnect(); }}
    }}).observe(document.body, {{ childList: true, subtree: true }});
  </script>
</body>
</html>
"""


def main() -> None:
    import os
    os.chdir(ROOT)
    if SITE.exists():
        shutil.rmtree(SITE)
    for f in FILES:
        dst = SITE / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / f, dst)
    cfg = tomllib.loads((ROOT / '.streamlit' / 'config.toml').read_text())
    flat = {f'{sec}.{k}': v for sec, kv in cfg.items() for k, v in kv.items()}
    (SITE / 'index.html').write_text(PAGE.format(stlite=STLITE, files=json.dumps(FILES), config=json.dumps(flat)))
    (SITE / '.nojekyll').write_text('')
    size = sum(p.stat().st_size for p in SITE.rglob('*') if p.is_file())
    print(f'_site: {len(FILES)} app files, {size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
