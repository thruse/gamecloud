#!/usr/bin/env python

import dropbox
import os
import sys
import shutil
import glob

"""
Defintions
Cloud save: a save file's path in the cloud.
Local save: a local save file's path.
Schema: the file name of a file that describes a game's local saves.
Save name: the largest subpath of a cloud save that is the same as a subpath of a local save.
Cloud save dir: a cloud save, minus the save name.
Local save dir: a local save, minus the save name.
Cloud save dirname: the path to a directory containing a cloud save file.
Local save dirname: the path to a directory containing a local save file.
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

def get_save_names(schema, save_dir):
    save_dir = get_local_save_dir(schema)
    save_patterns = get_save_patterns(schema)

    save_names = []
    for save_pattern in save_patterns:
        save_names.extend(glob.glob(os.path.normpath(save_pattern), root_dir=save_dir))

    return save_names

def upload(dbx, src, dst):
    with open(src, "rb") as f:
        dbx.files_upload(f.read(), dst, mode=dropbox.files.WriteMode.overwrite)

def download(dbx: dropbox.Dropbox, src, dst):
    if file_exists(dbx, src):
        _, res = dbx.files_download(src)
        with open(dst, "wb") as f:
            f.write(res.content)

def copy_saves(schema, src_save_dir, dst_save_dir):
    src_save_names = get_save_names(schema, src_save_dir)
    for src_save_name in src_save_names:
        dst_save = os.path.join(dst_save_dir, src_save_name)
        os.makedirs(os.path.dirname(dst_save), exist_ok=True)
        shutil.copyfile(os.path.join(src_save_dir, src_save_name), dst_save)

dbx = dropbox.Dropbox(app_key=os.environ["GAMECLOUD_KEY"], app_secret=os.environ["GAMECLOUD_SECRET"], oauth2_refresh_token=os.environ["GAMECLOUD_TOKEN"])

cloud_saves_dir = "/saves"
create_dir(dbx, cloud_saves_dir)

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
games = os.listdir(schemas_dir)

for game in games:
    create_dir(dbx, '/'.join([cloud_saves_dir, game]))

commands = ["upload", "download"]
if len(sys.argv) == 3 and sys.argv[1] in commands and sys.argv[2] in games:
    command = sys.argv[1]
    game = sys.argv[2]
    cloud_save_zip = '/'.join([cloud_saves_dir, game+".zip"])

    schema = os.path.join(schemas_dir, game)
    local_save_dir = get_local_save_dir(schema)

    tmp_save_dir = os.path.join(os.environ["MYDIR"], "tmp", "gamecloud", command, game)
    if os.path.isdir(tmp_save_dir):
        shutil.rmtree(tmp_save_dir)
    for match in glob.glob(tmp_save_dir+"*"):
        if os.path.isfile(match):
            os.remove(match)

    os.makedirs(tmp_save_dir)

    tmp_save_zip = tmp_save_dir+".zip"
    
    if command == "upload":
        copy_saves(schema, local_save_dir, tmp_save_dir)
        
        shutil.make_archive(tmp_save_dir, "zip", tmp_save_dir)
        upload(dbx, tmp_save_zip, cloud_save_zip)

    if command == "download":
        download(dbx, cloud_save_zip, tmp_save_zip)
        shutil.unpack_archive(tmp_save_zip, tmp_save_dir)

        copy_saves(schema, tmp_save_dir, local_save_dir)
else:
    print("error: incorrect syntax", file=sys.stderr)

