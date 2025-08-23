#!/usr/bin/env python

import dropbox
import os
import sys
import shutil
import glob
import getpass

"""
Defintions
Cloud save: a save file's path in the cloud.
Local save: a local save file's path.
Manifest: the file name of a file that describes a game's local saves.
Save name: the largest subpath of a cloud save that is the same as a subpath of a local save.
Cloud save dir: a cloud save, minus the save name.
Local save dir: a local save, minus the save name.
Cloud save dirname: the path to a directory containing a cloud save file.
Local save dirname: the path to a directory containing a local save file.
Save pattern: a glob pattern expressing the form of a save name.
"""

def dir_exists(dbx, dir):
    try:
        result = isinstance(dbx.files_get_metadata(dir), dropbox.files.FolderMetadata)
    except dropbox.exceptions.ApiError:
        result = False

    return result

def create_dir(dbx: dropbox.Dropbox, dir):
    if not dir_exists(dbx, dir):
        dbx.files_create_folder_v2(dir)

def file_exists(dbx: dropbox.Dropbox, file):
    try:
        result = isinstance(dbx.files_get_metadata(file), dropbox.files.FileMetadata)
    except dropbox.exceptions.ApiError:
        result = False
        
    return result

def get_game_info(manifest):
    manifest_lines = []
    with open(manifest) as f:
        manifest_lines = [line.strip() for line in f]
    assert(len(manifest_lines) > 4)

    local_save_dir = ""
    if sys.platform == "win32":
        local_save_dir = os.path.expandvars(manifest_lines[1])
    elif sys.platform == "darwin":
        local_save_dir = os.path.expandvars(manifest_lines[2])
    elif sys.platform == "linux":
        local_save_dir = os.path.expandvars(manifest_lines[3])

    game_info = {
        "local_save_dir": local_save_dir,
        "save_patterns": manifest_lines[4:]
    }
    return game_info

def get_save_names(save_patterns, save_dir):
    save_names = []
    for save_pattern in save_patterns:
        matches = glob.glob(os.path.normpath(save_pattern), root_dir=save_dir, recursive=True)
        for save_name in matches:
            if os.path.isfile(os.path.join(save_dir, save_name)):
                save_names.append(save_name)

    return save_names

def upload(dbx, src, dst):
    with open(src, "rb") as f:
        dbx.files_upload(f.read(), dst, mode=dropbox.files.WriteMode.overwrite)

def download(dbx: dropbox.Dropbox, src, dst):
    if file_exists(dbx, src):
        _, res = dbx.files_download(src)
        with open(dst, "wb") as f:
            f.write(res.content)

def os_replace_dir(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def copy_saves(save_patterns, src_save_dir, dst_save_dir):
    src_save_names = get_save_names(save_patterns, src_save_dir)
    for src_save_name in src_save_names:
        dst_save = os.path.join(dst_save_dir, src_save_name)
        os.makedirs(os.path.dirname(dst_save), exist_ok=True)
        shutil.copyfile(os.path.join(src_save_dir, src_save_name), dst_save)

GAMECLOUD_KEY = getpass.getpass("Enter gamecloud key: ")
GAMECLOUD_SECRET = getpass.getpass("Enter gamecloud secret: ")
GAMECLOUD_TOKEN = getpass.getpass("Enter gamecloud token: ")

dbx = dropbox.Dropbox(app_key=GAMECLOUD_KEY, app_secret=GAMECLOUD_SECRET, oauth2_refresh_token=GAMECLOUD_TOKEN)

cloud_saves_dir = "/saves"
create_dir(dbx, cloud_saves_dir)

manifests_dir = os.path.join(os.path.dirname(__file__), "manifests")
games = os.listdir(manifests_dir)

commands = ["upload", "download"]

if len(sys.argv) == 3 and sys.argv[1] in commands and sys.argv[2] in games:
    command = sys.argv[1]
    game = sys.argv[2]
    cloud_save_zip = '/'.join([cloud_saves_dir, game+".zip"])

    manifest = os.path.join(manifests_dir, game)
    game_info = get_game_info(manifest)

    tmp_save_dir = os.path.join(os.path.dirname(__file__), "tmp", command, game)

    for match in glob.glob(tmp_save_dir+"*"):
        if os.path.isfile(match):
            os.remove(match)

    os_replace_dir(tmp_save_dir)

    tmp_save_zip = tmp_save_dir+".zip"
    
    if command == "upload":
        copy_saves(game_info["save_patterns"], game_info["local_save_dir"], tmp_save_dir)

        shutil.make_archive(tmp_save_dir, "zip", tmp_save_dir)
        upload(dbx, tmp_save_zip, cloud_save_zip)

    if command == "download":
        old_local_save_dir = os.path.join(os.path.dirname(__file__), "tmp", "old", game)
        os_replace_dir(old_local_save_dir)
        copy_saves(game_info["save_patterns"], game_info["local_save_dir"], old_local_save_dir)

        download(dbx, cloud_save_zip, tmp_save_zip)
        shutil.unpack_archive(tmp_save_zip, tmp_save_dir)

        copy_saves(game_info["save_patterns"], tmp_save_dir, game_info["local_save_dir"])
else:
    print("error: incorrect syntax", file=sys.stderr)

