export PYTHONIOENCODING=UTF-8
export LANG=C.UTF-8
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/base
export PYTHONPATH=${PYTHONPATH}:/base

celery -A celery_worker flower --address=0.0.0.0 --port=4020 --pool=solo &
celery -A celery_worker worker --loglevel=INFO &

uvicorn api:app --port 80 --host 0.0.0.0 --workers 1
