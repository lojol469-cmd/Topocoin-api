#!/bin/bash

# Démarrer l'API FastAPI en arrière-plan
python api.py &
API_PID=$!

# Attendre un peu que l'API démarre
sleep 2

# Démarrer Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Si Streamlit s'arrête, tuer l'API
kill $API_PID