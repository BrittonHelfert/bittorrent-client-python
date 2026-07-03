import struct

import requests

from .bencode import decode
from .torrent import Torrent

# arbitrary peer ID for testing
PEER_ID = b"-CC0001-britton12345"
PORT = 6881


def get_peers(torrent: Torrent) -> list[tuple[str, int]]:
    response = requests.get(
        torrent.announce,
        params={
            "info_hash": torrent.info_hash,
            "peer_id": PEER_ID,
            "port": PORT,
            "uploaded": 0,
            "downloaded": 0,
            "left": torrent.length,
            "compact": 1,
        },
    )
    response.raise_for_status()
    decoded = decode(response.content)
    return parse_peers(decoded[b"peers"])


def parse_peers(peers: bytes) -> list[tuple[str, int]]:
    result = []
    for i in range(0, len(peers), 6):
        record = peers[i : i + 6]
        ip = ".".join(str(byte) for byte in record[:4])
        (port,) = struct.unpack(">H", record[4:6])
        result.append((ip, port))
    return result
