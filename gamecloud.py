#!/usr/bin/env python

import os
import sys

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas = os.listdir(schemas_dir)

commands = ["push", "pull"]
if len(sys.argv) == 3 and sys.argv[1] in commands and sys.argv[2] in schemas:
    command = sys.argv[1]
    schema_file = os.path.join(schemas_dir, sys.argv[2])
    if command == "push":
        with open(schema_file) as f:
            schema_lines = f.readlines()
        
        schema = [line.strip() for line in schema_lines]
        if sys.platform == "win32":
            save_dir = os.path.expandvars(schema[1])
        elif sys.platform == "darwin":
            save_dir = os.path.expandvars(schema[2])
        elif sys.platform == "linux":
            save_dir = os.path.expandvars(schema[3])
        
        save_file_paths = [os.path.join(save_dir, file_name) for file_name in schema[4:]]
        for path in save_file_paths:
            print(path, "is the path to a save file and it is", os.path.exists(path), "that the file exists")
    elif command == "pull":
        print("pulling")
else:
    print("error: incorrect syntax", file=sys.stderr)
