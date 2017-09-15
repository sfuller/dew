import argparse


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmake-generator', dest='cmake_generator')
    parser.add_argument('-v', help='Be verbose', action='store_true')
    parser.add_argument('--skip-download', help='avoid downloading files', action='store_true')
    return parser
