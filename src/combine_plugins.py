#!/usr/bin/env python
"""Combines source into a single file for each plugin
"""

import argparse

def parse_to_single_file(file_name, out_file_name, import_root="./"):
    file_in = open(file_name, mode = "r", encoding = "utf-8-sig")
    file_out = open(out_file_name, "w")
    for line in file_in.readlines():
        file_out.write(line)

    file_in.close()
    file_out.close()

def main():
    parser = argparse.ArgumentParser(description=
        "Take a python source file and copy local imports so there is a single output file.")
    parser.add_argument("--input", type=str, required=True,
        help="Path to the file to parse")
    parser.add_argument("--output", type=str, required=True,
        help="Output file to write to")
    parser.add_argument("--import-dir", type=str, required=False, default="./",
        help="Path to search for imported modulees")
    args = parser.parse_args()

    print(args.input)
    print(args.output)
    print(args.import_dir)
    #parse_to_single_file(args.input, args.output, args.import_dir)

if __name__ == "__main__":
    main()