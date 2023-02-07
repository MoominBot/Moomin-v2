import os

from dotenv import load_dotenv

load_dotenv()


class ConfigMeta(type):
    def __getattr__(cls, key):
        return os.environ.get(key, None)


class Config(metaclass=ConfigMeta):
    pass
