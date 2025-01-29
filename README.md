# solidarityzone

## Requirements

* Python Version `3.10.11`
* Optional: `docker` & `docker-compose`

## Development

### Setup

```bash
# Install dependencies in virtual environment
pip install -r requirements-development.txt

# Copy configuration and change it to your needs (usually not necessary for development)
cp .env.example .env
```

### Redis

```bash
# Run redis for development
docker-compose -f docker-compose.development.yml up -d
```

### Database

```bash
# Create SQLite database file, run migrations and populate with initial data
flask --app solidarityzone init-db

# Delete database
rm -rf ./instance
```

### HTTP

```bash
# Run development HTTP server, open browser at http://localhost:5000
flask --app solidarityzone run --debug
```

### Scraper

```bash
# Run task worker
celery -A solidarityzone worker -l INFO

# Run periodic scheduler (set to run midnight)
celery -A solidarityzone beat -l INFO

# Manually start scraper with <court-code>, <article>, <sub_type_index>
# arguments. sub_type_index can be 0 or 1
flask --app solidarityzone scrape "pgr--spb" 205 0

# Manuall start task scraping _all_ articles and sub-types for <court-code>
flask --app solidarityzone scrape-all "pgr--spb"
```

### Monitor

```bash
# Start a Celery Task Monitor dashboard, open browser at http://localhost:5555
celery -A solidarityzone flower
```

## Docker

Builds and runs all services within a docker environment. This setup is meant to be used in production. It exposes the HTTP server at port 8000 and a Celery Task Monitor HTTP server at port 5556 which can be used in combination with a reverse proxy.

```bash
# Copy configuration and change it to your needs
cp .env.example .env

# Deploy applications via docker, this exposes a HTTP server at port 8000 and 5556
docker-compose up -d

# Run `scrape-all` task manually
docker exec solidarityzone_server_1 flask --app solidarityzone scrape-all "pgr--sbp"
```

## VPN

The current Docker setup is using OpenVPN and Cloak for the scraper process. Add your `openvpn-config.ovpn` and `cloak-config.json` into this folder to connect to a VPN server (for example Amnezia VPN).

Newer versions of Amnezia VPN combine, compress and encode all configuration files. Use the "Share" functionality to create a `config.ovpn` file (contents starting with "vpn://") and run the following script right next to it to extract the correct configuration files:

<details>
<summary>convert.py</summary>

```python
import base64
import json
import zlib

file = open('config.ovpn', 'r', encoding="utf-8")
content = file.read()
file.close()
encoded = content.replace("vpn://", "")
compressed = base64.urlsafe_b64decode(encoded)
corrected = compressed[4:]
data = zlib.decompress(corrected)
parsed = json.loads(data.decode())

for container in parsed["containers"]:
    for name in container.keys():
        if "last_config" in container[name]:
            data = container[name]["last_config"]
            if name == "openvpn":
                data = json.loads(data)["config"]
            file = open("{}.config".format(name), 'w', encoding="utf-8")
            file.write(data)
            file.close()
            print("Parsed {}".format(name))
```

</details>

Make sure that the `ProxyMethod` config is set to `openvpn` in your Cloak and `remote` is set to `127.0.0.1 1984` in your OpenVPN configuration if you exported the files from Amnezia VPN.

## License

[`AGPL-3.0`](/LICENSE)
