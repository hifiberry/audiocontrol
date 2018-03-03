import sys
import argparse
import logging
import audiocontrol.audiocontrol as ac

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='verbose, log to console')
    parser.add_argument('-vv', '--debug',
                        action='store_true',
                        help='very verbose, debug to console')
    args = parser.parse_args()

    root = logging.getLogger()

    if args.debug:
        root.setLevel(logging.DEBUG)

    elif args.verbose:
        root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    ac.run()