#archivo autoejecutado por el app service en azure
#python3 -m venv CargueMasivoGomedisys
#source CargueMasivoGomedisys/bin/activate
#pip install -r requirements.txt
#gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
python3 -m venv entorno
source entorno/bin/activate
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
