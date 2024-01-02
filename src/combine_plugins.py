#!/usr/bin/env python
"""Combines source into a single file for each plugin
"""
import argparse
import re

def _get_local_import_path(line):
    import_path_re = re.compile(
        "^\s*from\s*(common\.[\._a-z]*)\s*import\s*\*.*$", re.MULTILINE)
    result = re.search(import_path_re, line)
    if result:
        module = result.group(1)
        return module.replace(".", "\\")
    return None

def _get_global_import_path(local_path, import_root=".\\"):
    if import_root[-1] == "\\":
        import_root = import_root[:-1]
    return "{0}\\{1}.py".format(import_root, local_path)

def _append_contents_to_file(
        file_name,
        file_out,
        import_root=".\\",
        imports_already_included=[]
    ):
    file_in = open(file_name, mode = "r")

    for line in file_in.readlines():
        local_path = _get_local_import_path(line)
        if not local_path:
            file_out.write(line)
        else:
            if any(local_path == old for old in imports_already_included):
                continue

            imports_already_included.append(local_path)
            global_path = _get_global_import_path(local_path, import_root)
            _append_contents_to_file(global_path, file_out, import_root, imports_already_included)

    file_in.close()

def _parse_to_single_file(file_name, out_file_name, import_root=".\\"):
    file_out = open(out_file_name, "w")
    _append_contents_to_file(file_name, file_out, import_root)
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