import json

def get_config():
    with open('./src/config.json', 'r') as file:
        config = json.load(file)
        print(config)
    return config

