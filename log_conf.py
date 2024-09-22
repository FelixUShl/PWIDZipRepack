import logging
import os
import dotenv
from datetime import datetime


def configure_logging():
    dotenv.load_dotenv(".env")
    level = os.getenv("LOGING_LEVEL")
    mark = datetime.now()
    if not os.path.exists('log'):
        os.mkdir('log')
    if level == 'DEBUG':
        mark = f"_{mark.day}_{mark.month}_{mark.year}_{mark.hour}_{mark.minute}_{mark.second}"
        file_log = logging.FileHandler(f'log/app{mark}.log', "w", encoding="UTF-8")
    else:
        file_log = logging.FileHandler('log/app.log', "a", encoding="UTF-8")
    console_out = logging.StreamHandler()
    logging.basicConfig(
        handlers=(file_log, console_out),
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(levelname)-7s - %(message)s", # %(module)15s:%(lineno)-3d
        # filename="log/app.log",
        # filemode="w"
    )
