import json

class ConfigController:
    _config = None

    @classmethod
    def load(cls):
        try:
            with open('config.json', 'r', encoding='utf-8') as file:
                cls._config = json.load(file)
        except FileNotFoundError:
            print("Can't find config file")
        except json.JSONDecodeError as e:
            print("Json syntax error")

    @classmethod
    def get(cls, key, default=None):
        if cls._config is None:
            ConfigController.load()
            raise Exception("Config not loaded! Need to call ConfigLoader.load() first")
        return cls._config.get(key, default)

    @classmethod
    def edit(cls, key, value):
        if cls._config is None:
            raise Exception("Config not loaded! Need to call ConfigLoader.load() first")
        try:
            cls._config[key] = value

            with open('config.json', 'w', encoding='utf-8') as file:
                json.dump(cls._config, file, ensure_ascii=False, indent=4)
                print("edit success")
            return True
        except Exception as e:
            print(f"Error editing config: {e}")
            return False
