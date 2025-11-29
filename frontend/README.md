# Topocoin Frontend (Streamlit)

This is the Streamlit frontend for Topocoin wallet.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run app.py
   ```

## Docker

```bash
docker build -t topocoin-frontend .
docker run -p 8501:8501 --env-file .env topocoin-frontend
```

## Environment Variables

Create a `.env` file with:
- API_BASE_URL (URL of the backend API)
