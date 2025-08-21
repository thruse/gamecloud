#!/usr/bin/env python

import dropbox
import os
import sys

def folder_exists(dbx, folder):
    try:
        result = isinstance(dbx.files_get_metadata(folder), dropbox.files.FolderMetadata)
    except dropbox.exceptions.ApiError:
        result = False

    return result

def create_folder(dbx: dropbox.Dropbox, folder):
    if not folder_exists(dbx, folder):
        dbx.files_create_folder_v2(folder)

def file_exists(dbx: dropbox.Dropbox, file):
    try:
        result = isinstance(dbx.files_get_metadata(file), dropbox.files.FileMetadata)
    except dropbox.exceptions.ApiError:
        result = False
        
    return result

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
            if os.path.isfile(local_save):
                local_saves.append(local_save)

    return local_saves

def upload(dbx, src, dst):
    with open(src, "rb") as f:
        dbx.files_upload(f.read(), dst, mode=dropbox.files.WriteMode.overwrite)

def download(dbx: dropbox.Dropbox, src, dst):
    if file_exists(src):
        _, res = dbx.files_download(src)
        with open(dst, "wb") as f:
            f.write(res.content)

token = os.environ["GAMECLOUD_TOKEN"]
dbx = dropbox.Dropbox(token)

saves_dir = "/saves"
create_folder(dbx, saves_dir)

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
games = os.listdir(schemas_dir)

for game in games:
    create_folder(dbx, '/'.join([saves_dir, game]))

commands = ["push", "pull"]
if len(sys.argv) == 3 and sys.argv[1] in commands and sys.argv[2] in games:
    command = sys.argv[1]
    game = sys.argv[2]
    save_dir = '/'.join([saves_dir, game])
    
    schema = os.path.join(schemas_dir, game)
    local_saves = get_local_saves(schema)

    if command == "push":
        for local_save in local_saves:
            save_name = os.path.basename(local_save)
            upload(dbx, local_save, '/'.join([save_dir, save_name]))
    
    if command == "pull":
        for local_save in local_saves:
            save_name = os.path.basename(local_save)
            download(dbx, '/'.join([save_dir, save_name]), local_save)
else:
    print("error: incorrect syntax", file=sys.stderr)
