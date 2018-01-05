import sys
import argparse
import re

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, 
                        help="Specify an input file.  If no file is given, assumes input over standard in.")

    args = parser.parse_args()
    return open(args.input) if args.input != None else sys.stdin

def main():
    test = re.compile("ERROR.*TOCID=(\d*)")
    with parse_args() as fs:
        for line in fs:
            m = re.match(test, line)
            if m != None:
                print m.group(1)


if __name__ == "__main__":
    main()
