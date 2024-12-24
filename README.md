# jellyfin-language-tags

A small python script to add language tags based on the audio files using Jellyfin REST API

Dependencies:
- python (i used python 3 but may works on others?)
- requests python lib
- [Jellyfin REST API](https://api.jellyfin.org/)

## Run

Replace the enviroment variable values with the correct ones for you.
```sh
JELLYFIN_URL=https://jellfin.example.com JELLYFIN_USER=admin JELLYFIN_PASSWORD=example python add_language_tag.py
```

See the comments in the files for more details

Special thanks to this gist that helped https://gist.github.com/mcarlton00/f7bd7218828ed465ce0f309cebf9a247

Feel free to fork or PR if you feel it could be better.

## Docker

To run this as a Docker Container:

1. Download the repo with the "Code" Button on Github, download as ZIP file or clone with Git
2. Make sure you have Docker installed
3. Open a Terminal in the folder with all the downloaded files
4. Edit docker-compose.yml
5. `docker-compose up`