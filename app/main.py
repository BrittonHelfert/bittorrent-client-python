import hashlib
import json
import sys

from app import bencode


def bytes_to_str(data):
    """Recursively decode bytes to str so json.dumps can serialize a value."""
    if isinstance(data, bytes):
        return data.decode()
    if isinstance(data, list):
        return [bytes_to_str(item) for item in data]
    if isinstance(data, dict):
        return {bytes_to_str(key): bytes_to_str(value) for key, value in data.items()}
    return data


def parse_file_info(bencoded_value: bytes):
    decoded = bencode.decode(bencoded_value)
    info = decoded[b"info"]
    encoded_info = bencode.encode(info)
    print(f"Tracker URL: {decoded[b'announce'].decode()}")
    print(f"Length: {info[b'length']}")
    print(f"Info Hash: {hashlib.sha1(encoded_info).hexdigest()}")
    print(f"Piece Length: {info[b'piece length']}")
    pieces = info[b"pieces"]
    hashes = [pieces[i : i + 20].hex() for i in range(0, len(pieces), 20)]
    print(f"Piece Hashes: {hashes}")


def main():
    command = sys.argv[1]

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    if command == "decode":
        bencoded_value = sys.argv[2].encode()
        print(json.dumps(bytes_to_str(bencode.decode(bencoded_value))))
    elif command == "info":
        with open(sys.argv[2], "rb") as f:
            bencoded_value = f.read()
        parse_file_info(bencoded_value)
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
