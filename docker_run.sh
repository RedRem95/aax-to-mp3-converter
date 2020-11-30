gunicorn -w ${WORKER_THREADS:-$(expr $(nproc --all) - 1)} -t ${GUNICORN_TIMEOUT:-180} -b 0.0.0.0:${BIND_ADDRESS:-8000} webapp:app
