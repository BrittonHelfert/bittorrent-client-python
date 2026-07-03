"""Bencode decoding and encoding.

Every decoder returns ``(value, bytes_consumed)`` so callers can parse
composite values (lists, dicts) without guessing where each element ends.
Bencoded "strings" are kept as raw ``bytes`` since they may hold non-UTF-8
data (e.g. the SHA-1 piece hashes in a torrent file).
"""

from typing import Any, Tuple


def decode(data: bytes) -> Any:
    """Decode a single bencoded value, ignoring any trailing bytes."""
    value, _ = decode_value(data)
    return value


def decode_value(data: bytes) -> Tuple[Any, int]:
    if not data:
        raise ValueError("Unexpected end of input")
    prefix = chr(data[0])
    if prefix.isdigit():
        return decode_string(data)
    elif prefix == "i":
        return decode_int(data)
    elif prefix == "l":
        return decode_list(data)
    elif prefix == "d":
        return decode_dict(data)
    else:
        raise ValueError(f"Invalid encoded value: {data!r}")


def decode_string(data: bytes) -> Tuple[bytes, int]:
    colon = data.find(b":")
    if colon == -1:
        raise ValueError("Invalid string: missing ':'")
    length = int(data[:colon])
    start = colon + 1
    end = start + length
    if end > len(data):
        raise ValueError("Invalid string: declared length exceeds input")
    return data[start:end], end


def decode_int(data: bytes) -> Tuple[int, int]:
    end = data.find(b"e")
    if end == -1:
        raise ValueError("Invalid integer: missing 'e'")
    return int(data[1:end]), end + 1


def decode_list(data: bytes) -> Tuple[list, int]:
    items = []
    index = 1  # skip the leading 'l'
    while index < len(data) and chr(data[index]) != "e":
        value, consumed = decode_value(data[index:])
        items.append(value)
        index += consumed
    if index >= len(data):
        raise ValueError("Invalid list: missing 'e'")
    return items, index + 1  # skip the trailing 'e'


def decode_dict(data: bytes) -> Tuple[dict, int]:
    result = {}
    index = 1  # skip the leading 'd'
    while index < len(data) and chr(data[index]) != "e":
        key, consumed = decode_string(data[index:])
        index += consumed
        value, consumed = decode_value(data[index:])
        index += consumed
        result[key] = value
    if index >= len(data):
        raise ValueError("Invalid dict: missing 'e'")
    return result, index + 1  # skip the trailing 'e'


def encode(value: Any) -> bytes:
    if isinstance(value, bytes):
        return encode_string(value)
    if isinstance(value, str):
        return encode_string(value.encode())
    if isinstance(value, bool):
        raise ValueError("bool is not a valid bencode type")
    if isinstance(value, int):
        return encode_int(value)
    if isinstance(value, list):
        return encode_list(value)
    if isinstance(value, dict):
        return encode_dict(value)
    raise ValueError(f"Unsupported type: {type(value)}")


def encode_string(value: bytes) -> bytes:
    return str(len(value)).encode() + b":" + value


def encode_int(value: int) -> bytes:
    return b"i" + str(value).encode() + b"e"


def encode_list(value: list) -> bytes:
    return b"l" + b"".join(encode(item) for item in value) + b"e"


def encode_dict(value: dict) -> bytes:
    result = b"d"
    for key, item in sorted(value.items()):
        result += encode_string(key) + encode(item)
    result += b"e"
    return result
