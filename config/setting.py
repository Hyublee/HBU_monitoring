import configparser

def load_settings(path='./config/main.ini'):
    config = configparser.ConfigParser()
    config.read(path)
    return config
