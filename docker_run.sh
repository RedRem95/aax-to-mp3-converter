gunicorn -w ${WORKER_THREADS:-$(expr $(nproc --all) - 1)} -b 0.0.0.0:${BIND_ADDRESS:-8000} app:app
