@echo off

set PYTHON=C:\Proyectos\Suite\venv\Scripts\python.exe

start cmd /k "cd /d C:\Proyectos\Suite\launcher && %PYTHON% -m streamlit run app.py --server.port 8888"

start cmd /k "cd /d C:\Proyectos\Suite\carga_precios && %PYTHON% -m streamlit run app.py --server.port 8889"

start cmd /k "cd /d C:\Proyectos\Suite\reporte_ops && %PYTHON% -m streamlit run app.py --server.port 8890"