import argparse
import logging

from anyio import create_tcp_listener, run
import config

from src.milter import handle
from src.remailer import Remailer
from src.validator import Validator
from src.challenge import init_handlers as init_challenge_handlers

from src import services

async def main():
    parser = argparse.ArgumentParser(
        prog="postconfirm",
        description="Milter handler for confirming that emails come from valid email addresses"
    )
    parser.add_argument("-c", "--config-file", default="/app/etc/postconfirm.cfg", type=argparse.FileType())
    parser.add_argument("-p", "--port")

    args = parser.parse_args()

    # Load the configuration
    app_config = config.Config(args.config_file)

    # og
    # Set up the root logger
    #logger = logging.getLogger()

    #logging.basicConfig(
    #    level=app_config.get('log.level', logging.INFO),
    #    style="{",
    #    datefmt="%b %d %H:%M:%S",
    #    format="{asctime} postconfirm/postconfirm[{process}]: {message} [{filename}:{lineno}]"
    #)

    # new
    logging.basicConfig(
        level=app_config.get('log.level', logging.INFO),
        style="{",
        datefmt="%b %d %H:%M:%S",
        format="{asctime} postconfirm/postconfirm[{process}]: {message} [{filename}:{lineno}]"
    )

    logger = logging.getLogger()
    logger.setLevel(log_level)
    file_handler = TimedRotatingFileHandler(
        '/var/log/postconfirm.log', when=logging_rotate_period, interval=1, backupCount=5
    )

    file_formatter = logging.Formatter(
        style="{",
        datefmt="%b %d %H:%M:%S",
        fmt="{asctime} postconfirm/postconfirm[{process}]: {message} [{filename}:{lineno}]"
    )

    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
    logging = logging.LoggerAdapter(logger)

    # Set up a services registry
    services["app_config"] = app_config
    services["remailer"] = Remailer(app_config)
    services["validator"] = Validator(app_config)

    init_challenge_handlers(services)

    # Start the listener
    listen_port = args.port or app_config.get("milter_port", 1999)
    listener = await create_tcp_listener(local_port=listen_port)
    await listener.serve(handle)

if __name__ == "__main__":
    run(main)
