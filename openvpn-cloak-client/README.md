# openvpn-cloak-client

Dockerized OpenVPN and Cloak client.

## Usage

```bash
# Set up configuration with your own values
touch cloak-config.json
touch openvpn-config.ovpn

# Start OpenVPN + Cloak container
docker-compose up -d

# Other container using network
docker run --net=container:openvpn <target_image>
```

## License

`UNLICENSE`
