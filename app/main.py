import json
import sys

from .bencode import decode
from .torrent import Torrent


def bytes_to_str(data):
    """Recursively decode bytes to str so json.dumps can serialize a value."""
    if isinstance(data, bytes):
        return data.decode()
    if isinstance(data, list):
        return [bytes_to_str(item) for item in data]
    if isinstance(data, dict):
        return {bytes_to_str(key): bytes_to_str(value) for key, value in data.items()}
    return data


def print_torrent_info(torrent: Torrent):
    print(f"Tracker URL: {torrent.announce}")
    print(f"Length: {torrent.length}")
    print(f"Info Hash: {torrent.info_hash.hex()}")
    print(f"Piece Length: {torrent.piece_length}")
    print(f"Piece Hashes: {[h.hex() for h in torrent.piece_hashes]}")


def main():
    command = sys.argv[1]

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    if command == "decode":
        bencoded_value = sys.argv[2].encode()
        print(json.dumps(bytes_to_str(decode(bencoded_value))))
    elif command == "info":
        print_torrent_info(Torrent.from_file(sys.argv[2]))
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
