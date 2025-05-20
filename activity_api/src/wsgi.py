"""
WSGI config for src project.
This is used as an entry-point for the application in gunicorn.

Disclaimer: This is based on our bachelor eindwerk project setup, which I also largely contributed to.
"""
from confz import EnvSource
from src.app import create_app
from src.config import APIConfig

config = APIConfig(config_sources=EnvSource(allow_all=True, nested_separator="__", file=".env"))
app = create_app(config)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)
