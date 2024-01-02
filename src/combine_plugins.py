#!/usr/bin/env python
"""Combines source into a single file for each plugin
"""
import argparse
import re

def _get_import_path(line, import_root=".\\"):
    import_path_re = re.compile(
        "^\s*from\s*(common\.[\._a-z]*)\s*import\s*\*.*$", re.MULTILINE)
    result = re.search(import_path_re, line)
    if result:
        module = result.group(1)
        local_path = module.replace(".", "\\")
        if import_root[-1] == "\\":
            import_root = import_root[:-1]
        return "{0}\\{1}.py".format(import_root, local_path)
    return None

def _parse_to_single_file(file_name, out_file_name, import_root=".\\"):

    file_in = open(file_name, mode = "r")
    file_out = open(out_file_name, "w")
    for line in file_in.readlines():
        import_path = _get_import_path(line, import_root)
        if not import_path:
            file_out.write(line)
        else:
            file_out.write("TODO copy contents of {}".format(import_path))

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

    _parse_to_single_file(args.input, args.output, args.import_dir)

if __name__ == "__main__":
    main()