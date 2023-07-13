import logging

class Env:
    def __init__(self):
        pass
        
        
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add the console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)
    # add handler
    logger.addHandler(consoleHandler)
    return logger

env = Env()