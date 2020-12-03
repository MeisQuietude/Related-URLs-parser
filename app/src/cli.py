import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument("method", type=str, choices=["get", "load"],
                    help="Show parsed urls")
parser.add_argument("url", type=str)
parser.add_argument("-d", "--depth", type=int, default=2,
                    help="Limit depth to parse")
parser.add_argument("-n", "--limit", type=int, default=0,
                    help="Limit to show urls")

args = parser.parse_args(sys.argv[1:])
