#!/usr/bin/env python

import shutil
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
        for line in schema[1:]:
            print(os.path.expandvars(line))
    elif command == "pull":
        print("pulling")
else:
    print("error: incorrect syntax", file=sys.stderr)
