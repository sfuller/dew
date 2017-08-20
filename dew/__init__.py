import argparse


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmake-generator', dest='cmake_generator')
    parser.add_argument('-v', help='Be verbose', action='store_true')
    return parser
