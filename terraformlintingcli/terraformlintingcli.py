#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: terraformlintingcli.py
#
# Copyright 2018 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for terraformlintingcli

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
import logging.config
import json
import argparse
import os

from terraformtestinglib import Stack, InvalidPositioning, InvalidNaming
from colored import fore, style

__author__ = '''Costas Tyfoxylos <ctyfoxylos@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''2018-05-24'''
__copyright__ = '''Copyright 2018, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<ctyfoxylos@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''terraformlintingcli'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class ReadableDirectory(argparse.Action):  # pylint: disable=too-few-public-methods
    """Argparse action for a directory that is readable"""

    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            raise argparse.ArgumentTypeError("{} is not a valid path.".format(values))
        if os.access(values, os.R_OK):
            setattr(namespace, self.dest, values)
        else:
            raise argparse.ArgumentTypeError("No read access to {}.".format(values))


class ReadableFile(argparse.Action):  # pylint: disable=too-few-public-methods
    """Argparse action for a file that is readable"""

    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.exists(values):
            raise argparse.ArgumentTypeError("{} is not a valid file.".format(values))
        if os.access(values, os.R_OK):
            setattr(namespace, self.dest, values)
        else:
            raise argparse.ArgumentTypeError("No read access to {}.".format(values))


def get_arguments():
    """
    Gets us the cli arguments.

    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description=('Cli to lint naming conventions of terraform plans based on a'
                                                  ' provided rule set'))
    parser.add_argument('--log-config',
                        '-l',
                        action='store',
                        dest='logger_config',
                        help='The location of the logging config json file',
                        default='')
    parser.add_argument('--log-level',
                        '-L',
                        help='Provide the log level. Defaults to INFO.',
                        dest='log_level',
                        action='store',
                        default='info',
                        choices=['debug',
                                 'info',
                                 'warning',
                                 'error',
                                 'critical'])
    parser.add_argument('-n',
                        '--naming',
                        metavar='naming.yaml',
                        dest='naming',
                        action=ReadableFile,
                        required=True)
    parser.add_argument('-p',
                        '--positioning',
                        metavar='positioning.yaml',
                        dest='positioning',
                        action=ReadableFile,
                        required=True)
    parser.add_argument('-s',
                        '--stack',
                        dest='stack',
                        metavar='tf_plans_dir',
                        action=ReadableDirectory,
                        required=True)
    args = parser.parse_args()
    return args


def setup_logging(args):
    """
    Sets up the logging.

    Needs the args to get the log level supplied

    Args:
        args: The arguments returned gathered from argparse
    """
    # This will configure the logging, if the user has set a config file.
    # If there's no config file, logging will default to stdout.
    if args.logger_config:
        # Get the config for the logger. Of course this needs exception
        # catching in case the file is not there and everything. Proper IO
        # handling is not shown here.
        configuration = json.loads(open(args.logger_config).read())
        # Configure the logger
        logging.config.dictConfig(configuration)
    else:
        handler = logging.StreamHandler()
        handler.setLevel(args.log_level.upper())
        formatter = logging.Formatter(('%(asctime)s - '
                                       '%(name)s - '
                                       '%(levelname)s - '
                                       '%(message)s'))
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)
        LOGGER.setLevel(args.log_level.upper())


def main():
    """
    Main method.

    This method holds what you want to execute when
    the script is run on command line.
    """
    try:
        args = get_arguments()
    except argparse.ArgumentTypeError as exc:
        raise SystemExit(exc.message)
    setup_logging(args)
    try:
        stack = Stack(args.stack, args.naming, args.positioning)
    except (InvalidNaming, InvalidPositioning):
        print(fore.RED + style.BOLD + 'Invalid file provided as argument' + style.RESET)  # pylint: disable=superfluous-parens,no-member
        raise SystemExit(1)
    stack.validate()
    if stack.errors:
        for error in stack.errors:
            print(error)  # pylint: disable=superfluous-parens
        raise SystemExit(1)
    else:
        message = 'No naming convention or file positioning errors found!'
        print(fore.GREEN_3A + style.BOLD + message + style.RESET)  # pylint: disable=superfluous-parens,no-member
        raise SystemExit(0)


if __name__ == '__main__':
    main()
