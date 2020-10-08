from pathlib import Path
from os import path

root_path = Path(path.dirname(__file__)) / '..'

bind = '127.0.0.1:8050'
workers = 2
proc_name = 'cardlive'
timeout = 600
loglevel = 'debug'
accesslog = str(root_path / 'access.log')
errorlog = str(root_path / 'prod.log')
daemon = True
pidfile = str(root_path / 'cardlive.pid')
