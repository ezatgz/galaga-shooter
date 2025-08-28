import json
import os

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
        if os.path.exists("assets/data/config.json"):
            with open("assets/data/config.json", 'r') as f:
                config_data = json.load(f)
                for key in config_data:
                    if config_data[key] not in [2, 3]:
                        config_data[key] = 2
                return config_data
        else:
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    except:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open("assets/data/config.json", 'w') as f:
            json.dump(config, f, indent=4)
    except:
        pass  # Silently fail for Pyodide

def load_highscores():
    try:
        if os.path.exists("assets/data/highscores.json"):
            with open("assets/data/highscores.json", 'r') as f:
                return json.load(f)
        else:
            return HIGHSCORE_DEFAULT.copy()
    except:
        return HIGHSCORE_DEFAULT.copy()

def save_highscores(highscores):
    try:
        with open("assets/data/highscores.json", 'w') as f:
            json.dump(highscores, f, indent=4)
    except:
        pass  # Silently fail for Pyodide