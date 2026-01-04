import json
import logging

with open('src/game_conf.json') as f:
    conf = json.load(f)

def setup_logging(level):
    if level == 0:
        level = logging.WARNING
        print("logging set to WARNING")
    elif level == 1:
        level = logging.INFO
        print("logging set to INFO")
    else:
        level = logging.DEBUG
        print("logging set to DEBUG")
    logging.basicConfig(
        level=level,
        force=True
    )
