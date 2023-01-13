import multiprocessing
import os

SERVER_PORT = os.getenv("FLASK_RUN_PORT", 5012)


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


bind = f"0.0.0.0:{SERVER_PORT}"
workers = number_of_workers()
