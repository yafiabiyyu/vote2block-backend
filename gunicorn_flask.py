import multiprocessing

bind = '0.0.0.0:5000'

workers = multiprocessing.cpu_count() * 2 + 1
backlog = 2048
worker_connections = 1000
daemon = False
debug = True
proc_name = 'app'
pdfile = 'logs/gunicorn.pid'
errorlog = 'logs/gunicorn.log'
