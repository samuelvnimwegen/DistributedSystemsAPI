"""
This module is the entry point of the application.
It sets up the Flask app with the given configuration
from the environment variables (in .env file or in the system).

Disclaimer: This is based on our bachelor eindwerk project setup, which I also largely contributed to.
"""
from confz import EnvSource
import argparse
from src.config import APIConfig
from src.app import create_app


def parse_args():
    """
    This function is used to parse the input variables
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", dest="API_KEY", help="API key to use in the app")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    config = APIConfig(config_sources=EnvSource(allow_all=True, nested_separator="__", file=".env"))
    app = create_app(config)
    app.run(host=config.host, port=config.port)
