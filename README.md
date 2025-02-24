# jellyfin-language-tags

A small python script to add language tags based on the audio files using Jellyfin REST API

It will add a tag based on the Audio tracks in the videos.
The format of the tag is : `language_<language_found>` for example: `language_eng` for english
If the tag already exists, it will not duplicate, so you can run this script safely every hour, or months for example.

When the process is done, you should launch a Library scan in Jellyfin to apply tags everywhere.

> The process took me 10 minutes for ~500 files in my Jellyfin server.
> 
> See the comments in the `add_language.py` files for more details about the process of the script
>
> Special thanks to this gist that helped https://gist.github.com/mcarlton00/f7bd7218828ed465ce0f309cebf9a247

_Feel free to fork or PR if you feel it could be better._

## Getting started

### Build the docker container
```sh
docker build -t jellyfin-language-tags:latest .
```

### Docker run: one shot
```sh
docker run --rm \
  --name language_tag_tool \
  -e JELLYFIN_URL=https://jellyfin.example.com \
  -e JELLYFIN_USERNAME=admin \
  -e JELLYFIN_PASSWORD=example \
  jellyfin-language-tags:latest
```

### Docker run: deamon, cronjob-like, every 3hours
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

### Docker compose:
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

## Know bugs:
- Some video may not have a Language define in the Audio, resulting in a `language_` or `language_und` tag added.
  - I kept it like that cause it may help you edit manually if you care... I dont !
- if you find one, feel free to open an Issue !


## Contributors
Thanks [ToasterUwU](https://github.com/ToasterUwU) for the docker integration!
