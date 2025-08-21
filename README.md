# Game Cloud

Save game progress to the cloud.

## Setup

1. Create a Dropbox app at https://www.dropbox.com/developers/apps, scoped to an app folder.

2. Set the permissions `files.metadata.write`, `files.metadata.read`, `files.content.write`, `files.content.read`.

3. Ensure the shell environment variables `GAMECLOUD_KEY` and `GAMECLOUD_SECRET` are set to the app key and secret respectively.

4. In a web browser go to `https://www.dropbox.com/oauth2/authorize?client_id=<APP_KEY>&token_access_type=offline&response_type=code`, where `APP_KEY` is the actual value of the app key, and copy the `ACCESS_CODE` you receive from this process.

5. Ensure the packages in `requirements.txt` are installed and that `python` is callable from the command line.

6. Run the following Python code.
    ```python
    import requests
    import json
    import os
    import sys

    response = requests.post("https://api.dropboxapi.com/oauth2/token",
                            data=f"code=ACCESS_CODE&grant_type=authorization_code",
                            auth=(os.environ["GAMECLOUD_KEY"], os.environ["GAMECLOUD_SECRET"]))

    print(json.dump(json.loads(response.text), indent=4))
    ```
    where `ACCESS_CODE` is the access code above. Save the refresh token given in the JSON output to the shell environment variable `GAMECLOUD_TOKEN`. For more information on steps 4 to 6, see [this StackOverflow question](https://stackoverflow.com/questions/70641660/how-do-you-get-and-use-a-refresh-token-for-the-dropbox-api-python-3-x).

7. Add the `bin` directory to your `PATH`.

## Usage

```
gamecloud [command] [game]
```
Currently available commands are `upload` and `download`.

Currently available games are `undertale` and `terraria`.

## Schema format

The file name of the schema should be the name of the game. Each line of the file has a special meaning, as follows.

0. No meaning. You can use this line as a comment.

1. Windows local save directory that contains all save files.

2. MacOS local save directory that contains all save files.

3. Linux local save directory that contains all save files.

Each of the remaining lines represents a glob pattern matching different save files, relative to the local save directory.

## Other information

- If you accidentally download saves from the cloud and overwrite local saves, you can find the saves you overwrote in `tmp/old/GAME_NAME`.

## Todo

- Support config files as well as save files.

- Support multiple local save directories for a given game.

- Handle possible errors more cleanly.

- Support more games
