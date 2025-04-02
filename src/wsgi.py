"""
WSGI config for src project.
"""
from confz import EnvSource
from src.app import create_app
from src.config import APIConfig

config = APIConfig(config_sources=EnvSource(allow_all=True, nested_separator="__", file=".env"))
app = create_app(config)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)
