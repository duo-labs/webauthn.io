import multiprocessing
import os

from homepage.logging import logger

bind = ":8000"
errorlog = "gunicorn_webauthnio.log"

DEBUG = os.getenv("DEBUG", False)

if DEBUG == "true":
    workers = 1
else:
    workers = multiprocessing.cpu_count() * 2 + 1

logger.info(f"Gunicorn will use {workers} worker(s)")
