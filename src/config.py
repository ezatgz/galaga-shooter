import json
import os
from .constants import resource_path

DEFAULT_CONFIG = {
    "movement_speed": 2,
    "shooting_speed": 2,
    "bullet_speed": 2
}

HIGHSCORE_DEFAULT = [{"name": "Anonymous", "score": 0} for _ in range(5)]

def load_config():
    # Note: For Pyodide, file I/O is not supported, so return default config
    # For local execution, load from file if available
    try:
        config_path = "assets/data/config.json"
        # 1. Try local file
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        # 2. Try bundled file
        elif os.path.exists(resource_path(config_path)):
            with open(resource_path(config_path), 'r') as f:
                config_data = json.load(f)
        else:
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        for key in config_data:
            if config_data[key] not in [2, 3]:
                config_data[key] = 2
        return config_data
    except:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        config_path = "assets/data/config.json"
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    except:
        pass  # Silently fail for Pyodide

def load_highscores():
    try:
        path = "assets/data/highscores.json"
        # 1. Try local file
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        # 2. Try bundled file
        elif os.path.exists(resource_path(path)):
            with open(resource_path(path), 'r') as f:
                return json.load(f)
        else:
            return HIGHSCORE_DEFAULT.copy()
    except:
        return HIGHSCORE_DEFAULT.copy()

def save_highscores(highscores):
    try:
        path = "assets/data/highscores.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(highscores, f, indent=4)
    except:
        pass  # Silently fail for Pyodide