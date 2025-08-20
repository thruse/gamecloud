#!/usr/bin/env python

import os
import sys
import shutil

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
saves_dir = os.path.join(os.path.dirname(__file__), "saves")
os.makedirs(saves_dir, exist_ok=True)
games = os.listdir(schemas_dir)
for game in games:
    os.makedirs(os.path.join(saves_dir, game), exist_ok=True)

commands = ["push", "pull"]
if len(sys.argv) == 3 and sys.argv[1] in commands and sys.argv[2] in games:
    command = sys.argv[1]
    game = sys.argv[2]
    game_save_dir = os.path.join(saves_dir, game)
    
    schema_file = os.path.join(schemas_dir, game)
    if command == "push":
        with open(schema_file) as f:
            schema_lines = f.readlines()
        
        schema = [line.strip() for line in schema_lines]
        if sys.platform == "win32":
            local_save_dir = os.path.expandvars(schema[1])
        elif sys.platform == "darwin":
            local_save_dir = os.path.expandvars(schema[2])
        elif sys.platform == "linux":
            local_save_dir = os.path.expandvars(schema[3])
        
        local_save_files = [os.path.join(local_save_dir, file_name) for file_name in schema[4:] if os.path.exists(os.path.join(local_save_dir, file_name))]
        for local_save_file in local_save_files:
            shutil.copy(local_save_file, game_save_dir)
    elif command == "pull":
        print("pulling")
else:
    print("error: incorrect syntax", file=sys.stderr)
