@echo off
python app_data.py
streamlit run app.py --server.port=8501
pause
