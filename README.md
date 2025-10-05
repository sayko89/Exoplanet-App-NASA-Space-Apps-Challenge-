# Exoplanet Explorer

A clean, high-performance Streamlit app for browsing exoplanets with a dedicated details page and showcasing a project video on the homepage.

## Features
- **Multi-page UI**: Öte Gezegen Detayları
- **Interactive**: Uydu ve gezegen seçimi, metrikler ve grafikler
- **Fast & Lightweight**: Caching (`st.cache_data`) and minimal deps
- **Secure**: No hardcoded secrets
- **Predict Interface Only**: `backend/predict.py` with placeholder scoring

## Quick Start (Local)
1. **Create & activate venv**
   ```bash
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. **Install deps**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure env (optional)**
   ```bash
   cp .env.example .env
   # Edit `.env` if you add custom variables for your extensions
   ```
4. **Run app**
   ```bash
   streamlit run app.py
   ```

You should see the homepage titled **“Exoplanet Explorer”**. Use the sidebar to navigate.

## Pages
1. **Gezegen Detayları**: Seçtiğiniz uydu verisinden gezegen detayları, metrikler ve grafikler.

### Deep-linking
- You can open the details page directly via URL params:
  - `?sat=KEPLER&planet=Kepler-186f`
  - Supported satellites: `KEPLER`, `TESS`, `COROT`

## Environment Variables
Create a `.env` if you need custom configuration for your extensions.
> **Note:** This project never logs secrets and only reads environment variables via `os.getenv`.

## Data
This app uses processed satellite datasets:
- `kepler_processed_exoplanets.csv`
- `toi_processed_exoplanets.csv` (TESS)
- `k2_processed_exoplanets.csv` (COROT/K2)

Columns may vary per dataset; the details page gracefully handles missing fields.

## Prediction Interface
`backend/predict.py` contains a **placeholder** inference function:
- `predict_habitability_score(planet_name, csv_path)` returns a score and rationale.
- Replace the heuristic with your real model inference (e.g., load a `.pkl` or `.onnx`), and cache any heavy resources using `st.cache_resource` in your Streamlit page.

## Performance Tips
- Use `@st.cache_data` for dataset loading and computed tables.
- Use `@st.cache_resource` for model loading or long-lived connections.
- Prefer lazy-loading and paging for large datasets.
- Keep assets small and compress images/videos.

## Replace Assets
- Logo: `assets/logo.png` (PNG recommended).
- Video: `assets/demo.mp4`. If empty or < 1 KB, the homepage will embed YouTube instead.
- Update your own assets and re-run the app.

## Deployment Checklist (3–5 steps)
1. Ensure `requirements.txt` matches your environment.
2. Upload the `exoplanet-app/` folder.
3. Run `streamlit run app.py`.
4. Verify `verify_run.py` passes.

## verify_run.py
Use this script to validate imports and basic file presence:
```bash
python verify_run.py
```

## License
MIT
