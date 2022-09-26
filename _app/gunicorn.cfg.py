import multiprocessing

bind = ":8000"
workers = multiprocessing.cpu_count() * 2 + 1
errorlog = "gunicorn_webauthnio.log"
