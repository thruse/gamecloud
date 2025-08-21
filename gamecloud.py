#!/usr/bin/env python

import dropbox
import os
import sys
import shutil
import glob

"""
Defintions
Save: a save file's path in the cloud.
Local save: a local save file's path.
Schema: the file name of a file that describes a game's local saves.
Save name: the largest subpath of a save that is the same as a subpath of a local save.
Save dir: a save, minus the save name.
Local save dir: a local save, minus the save name.
Save dirname: the directory containing a save file (in the cloud).
Local save dirname: the directory containing a local save file.
Save pattern: a glob pattern expressing the form of a save name.
"""

def dir_exists(dbx, folder):
    try:
        result = isinstance(dbx.files_get_metadata(folder), dropbox.files.FolderMetadata)
    except dropbox.exceptions.ApiError:
        result = False

    return result

def create_dir(dbx: dropbox.Dropbox, folder):
    if not dir_exists(dbx, folder):
        dbx.files_create_folder_v2(folder)

def file_exists(dbx: dropbox.Dropbox, file):
    try:
        result = isinstance(dbx.files_get_metadata(file), dropbox.files.FileMetadata)
    except dropbox.exceptions.ApiError:
        result = False
        
    return result

def get_schema_lines(schema):
    schema_lines = []
    with open(schema) as f:
        schema_lines = [line.strip() for line in f]
    assert(len(schema_lines) > 4)
    return schema_lines

def get_local_save_dir(schema):
    schema_lines = get_schema_lines(schema)
    if sys.platform == "win32":
        local_save_dir = os.path.expandvars(schema_lines[1])
    elif sys.platform == "darwin":
        local_save_dir = os.path.expandvars(schema_lines[2])
    elif sys.platform == "linux":
        local_save_dir = os.path.expandvars(schema_lines[3])
    
    return local_save_dir

def get_save_patterns(schema):
    return get_schema_lines(schema)[4:]

def get_local_saves(schema):
    local_save_dir = get_local_save_dir(schema)
    save_patterns = get_save_patterns(schema)

    local_save_names = []
    for save_pattern in save_patterns:
        local_save_names.extend(glob.glob(os.path.normpath(save_pattern), root_dir=local_save_dir))

    return local_save_dir, local_save_names

"""
def get_save_names(dbx, schema, save_dir):
    save_patterns = get_save_patterns(schema)

    save_names = []
    for save_pattern in save_patterns:
        save_names.extend()
        save = '/'.join([save_dir, save_file_name])
        if file_exists(dbx, save):
            saves.append(save)
    
    return saves
"""
def upload(dbx, src, dst):
    with open(src, "rb") as f:
        dbx.files_upload(f.read(), dst, mode=dropbox.files.WriteMode.overwrite)

def download(dbx: dropbox.Dropbox, src, dst):
    if file_exists(dbx, src):
        _, res = dbx.files_download(src)
        with open(dst, "wb") as f:
            f.write(res.content)

dbx = dropbox.Dropbox(app_key=os.environ["GAMECLOUD_KEY"], app_secret=os.environ["GAMECLOUD_SECRET"], oauth2_refresh_token=os.environ["GAMECLOUD_TOKEN"])

saves_dir = "/saves"
create_dir(dbx, saves_dir)

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
games = os.listdir(schemas_dir)

for game in games:
    create_dir(dbx, '/'.join([saves_dir, game]))

commands = ["push", "pull"]
if len(sys.argv) == 3 and sys.argv[1] in commands and sys.argv[2] in games:
    command = sys.argv[1]
    game = sys.argv[2]
    save_zip = '/'.join([saves_dir, game+".zip"])

    schema = os.path.join(schemas_dir, game)

    tmp_dir = os.path.join(os.environ["MYDIR"], "tmp", "gamecloud", game)
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    for match in glob.glob(tmp_dir+"*"):
        if os.path.isfile(match):
            os.remove(match)
    
    if command == "push":
        local_save_dir, local_save_names = get_local_saves(schema)
        for local_save_name in local_save_names:
            local_save_tmp = os.path.join(tmp_dir, local_save_name)
            os.makedirs(os.path.dirname(local_save_tmp), exist_ok=True)
            shutil.copyfile(os.path.join(local_save_dir, local_save_name), local_save_tmp)
        
        shutil.make_archive(tmp_dir, "zip", tmp_dir)
        upload(dbx, os.path.join(local_save_dir, local_save_name), save_zip)
    """
    if command == "pull":
        saves = get_saves(dbx, schema, save_dir)
        for save in saves:
            save_name = os.path.basename(save)
            download(dbx, save, os.)
    """
else:
    print("error: incorrect syntax", file=sys.stderr)
