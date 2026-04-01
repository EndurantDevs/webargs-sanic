import argparse
import logging.config
import os
from pathlib import Path

from dotenv import load_dotenv
from sanic import Sanic
import yaml

from extentions.exceptions import register_handlers
from extentions.middlewares import blueprint as ext_middlewares
from app import blueprint as app_blueprint


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='Setup host ip to listen up, default to 0.0.0.0', default='0.0.0.0')
    parser.add_argument('--port', help='Setup port to attach, default to 8080', type=int, default=8080)
    parser.add_argument('--workers', help='Setup workers to run, default to 1', type=int, default=1)
    parser.add_argument('--debug', help='Enable or disable debugging', action='store_true')
    parser.add_argument('--accesslog', help='Enable or disable access log', action='store_true')
    return parser.parse_args(argv)


def build_app(app_name="user_simple_storage", env_prefix=None):
    load_dotenv(dotenv_path=ENV_PATH)

    app = Sanic(app_name, env_prefix=env_prefix or os.environ.get("ENV_PREFIX", "SANIC_"))

    log_cfg = Path(app.config.get('LOG_CFG', 'logging.yaml'))
    if not log_cfg.is_absolute():
        log_cfg = BASE_DIR / log_cfg
    with log_cfg.open() as fobj:
        logging.config.dictConfig(yaml.safe_load(fobj))

    register_handlers(app)
    app.blueprint(ext_middlewares)
    app.blueprint(app_blueprint, url_prefix='/')

    return app


app = build_app()


def main(argv=None):
    args = parse_args(argv)
    app.run(
        host=args.host,
        port=args.port,
        workers=args.workers,
        debug=args.debug,
        access_log=args.accesslog,
    )


if __name__ == '__main__':
    main()
