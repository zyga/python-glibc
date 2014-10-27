#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import

import argparse
import signal
import logging


def on_SIGINT(loop):
    print("Got SIGINT, stoping the loop")
    loop.stop()


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.set_defaults(use_asyncio=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--pyglibc', help='Use python-glibc',
        action='store_false', dest='use_asyncio')
    group.add_argument(
        '--asyncio', help='Use asyncio (python 3.4 only)',
        action='store_true', dest='use_asyncio')
    ns = parser.parse_args()
    if ns.use_asyncio:
        import asyncio
    else:
        from pyglibc import asyncio
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, on_SIGINT, loop)
    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    raise SystemExit(main())
