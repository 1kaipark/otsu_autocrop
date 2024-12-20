from datetime import datetime as dt 

def log(msg: str, fpath: str = 'log.txt') -> None:
    """writes to a log.txt file"""
    with open(fpath, 'a+') as h:
        h.write('[' + str(dt.now()) + '] ' + msg + '\n')
