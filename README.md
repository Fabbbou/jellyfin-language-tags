# jellyfin-language-tags

A small python script to add language tags based on the audio files using Jellyfin REST API

Dependencies:
- python (i used python 3 but may works on others?)
- requests python lib
- [Jellyfin REST API](https://api.jellyfin.org/)

## Run

### Docker

**Docker run (one shot)**
```sh
docker run --rm \
  --name language_tag_tool \
  -e JELLYFIN_URL=https://jellyfin.example.com \
  -e JELLYFIN_USERNAME=admin \
  -e JELLYFIN_PASSWORD=example \
  jellyfin-language-tags:latest
```

**Docker run (cronjob-like, every 3hours)**
```sh
docker run -d \
  --name language_tag_tool \
  -e JELLYFIN_URL=https://jellyfin.example.com \
  -e JELLYFIN_USERNAME=admin \
  -e JELLYFIN_PASSWORD=example \
  -e INTERVAL_HOURS=3 \
  --restart unless-stopped \
  jellyfin-language-tags:latest
```

**Docker compose:**
- Edit docker-compose.yml
    - INTERVAL_HOURS make it working as a cronjob.  
- `docker compose up`

### Local install

Replace the enviroment variable values with the correct ones for you.
```sh
# oneliner
JELLYFIN_URL=https://jellfin.example.com JELLYFIN_USER=admin JELLYFIN_PASSWORD=example python add_language_tag.py

#or
JELLYFIN_URL=https://jellyfin.example.com
JELLYFIN_USER=admin
JELLYFIN_PASSWORD=example
python add_language_tag.py
```

See the comments in the files for more details

Special thanks to this gist that helped https://gist.github.com/mcarlton00/f7bd7218828ed465ce0f309cebf9a247

Feel free to fork or PR if you feel it could be better.

-----

## Contributors
Thanks [ToasterUwU](https://github.com/ToasterUwU) for the docker integration!