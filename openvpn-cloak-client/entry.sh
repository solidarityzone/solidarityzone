#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

cleanup() {
    kill TERM "$openvpn_pid"
    kill TERM "$cloak_pid"
    exit 0
}

ck-client --verbosity debug -c /config/cloak-config.json &
cloak_pid=$!

openvpn \
  --script-security 2 \
  --up /usr/local/bin/update-resolv-conf.sh \
  --down /usr/local/bin/update-resolv-conf.sh \
  --config /config/openvpn-config.ovpn &

openvpn_pid=$!

trap cleanup TERM

wait $openvpn_pid
