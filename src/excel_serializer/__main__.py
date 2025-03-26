import argparse
import json
import sys

from . import dump, load


def main():
    parser = argparse.ArgumentParser(description="Excel Serializer")
    parser.add_argument("-o", "--output", help="Output Excel file")
    parser.add_argument("-i", "--input", help="Input Excel file")
    args = parser.parse_args()

    if args.input:
        # Deserialize from Excel
        data = load(args.input)
    else:
        # Read JSON from stdin
        data = json.loads(sys.stdin.read())

    if args.output:
        # Serialize to Excel
        dump(data, args.output)
    else:
        # Print JSON to stdout
        print(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()
