#!/usr/bin/env python

'''
Definitions
Save: full path of a cloud save file
Local save: full path of a local save file
Schema: full path of a schema file. A schema describes the local saves.
'''

import os
import sys
import shutil

def get_local_saves(schema):
    schema_lines = []
    with open(schema) as f:
        for line in f:
            schema_lines.append(line.strip())

    if len(schema_lines) > 4:
        if sys.platform == "win32":
            local_save_dir = os.path.expandvars(schema_lines[1])
        elif sys.platform == "darwin":
            local_save_dir = os.path.expandvars(schema_lines[2])
        elif sys.platform == "linux":
            local_save_dir = os.path.expandvars(schema_lines[3])
        save_file_names = schema_lines[4:]
        
        local_saves = []
        for save_file_name in save_file_names:
            local_save = os.path.join(local_save_dir, save_file_name)
            if os.path.exists(local_save):
                local_saves.append(local_save)

    return local_saves

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
    save_dir = os.path.join(saves_dir, game)
    
    schema = os.path.join(schemas_dir, game)
    local_saves = get_local_saves(schema)

    if command == "push":
        for local_save in get_local_saves(schema):
            shutil.copy(local_save, save_dir)
    elif command == "pull":
        ;
else:
    print("error: incorrect syntax", file=sys.stderr)
