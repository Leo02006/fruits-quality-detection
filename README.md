# Fruit Ripeness Detector - Streamlit

## Run locally

1. Open this folder in VS Code.
2. Create/activate a Python virtual environment (recommended).
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run:

   ```bash
   streamlit run app.py
   ```

5. Upload `best.pt` in the sidebar.

## EDA
- Upload existing evaluation plots from your notebook's `runs/detect/val/` folder.
- Or upload `data.yaml` and run validation, provided the dataset paths in the YAML are accessible locally.

The class names are read directly from the uploaded model. The notebook used the labels:
`overripe`, `ripe`, `rotten`, `unripe`.
