# -*- coding: utf-8 -*-

import sys
import logging
import argparse
import os
import threading
from history_dumper.history_dumper import*
from history_dumper.settings import*
from history_dumper.db_work import*

__version__ = "0.0.1.dev0"
logger = logging.getLogger("LOG")
DEFAULT_CONFIG_NAME = "config"

def parse_arguments():
    parser = argparse.ArgumentParser(
        description = 'vk history dumper',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-V', '--verbose', action = 'store_const',
                        const = logging.DEBUG, dest = 'verbosity',
                        help = 'Make a lot of noise')

    parser.add_argument('-v', '--version', action = 'version',
                        version = __version__,
                        help = 'Print version number and exit')

    parser.add_argument('-c', '--config', dest = 'config',
                        help = 'Load configuration file.',
                        default = DEFAULT_CONFIG_NAME)

    return parser.parse_args()

def main():
    args = parse_arguments()

    logger.addHandler(logging.StreamHandler())

    if (args.verbosity):
        logger.setLevel(args.verbosity)
    else:
        logger.setLevel(logging.INFO)

    logger.debug('vk_history_dumper version: %s', __version__)

    settings = {}

    if args.config is not None and os.path.isfile(args.config):
        settings.update(read_settings(args.config))
        logger.debug("Current settings: %s", settings)

    vk_history_dumper = VKHistoryDumper(settings)
    vk_history_dumper.start()
