import hashlib
import json
import sys
from typing import Any, List, Tuple


def decode_bencode(bencoded_value):
    if chr(bencoded_value[0]).isdigit():
        first_colon_index = bencoded_value.find(b":")
        if first_colon_index == -1:
            raise ValueError("Invalid encoded value")
        return bencoded_value[first_colon_index + 1 :]
    elif chr(bencoded_value[0]) == "i" and chr(bencoded_value[-1]) == "e":
        # return without quotations
        return int(bencoded_value[1:-1])
    elif chr(bencoded_value[0]) == "l" and chr(bencoded_value[-1]) == "e":
        decoded_list, _ = decode_bencode_list(bencoded_value[1:])
        return decoded_list
    elif chr(bencoded_value[0]) == "d" and chr(bencoded_value[-1]) == "e":
        decoded_dict, _ = decode_bencode_dict(bencoded_value[1:])
        return decoded_dict
    else:
        raise ValueError("Invalid encoded value")


def decode_bencode_string(bytes: bytes) -> Tuple[bytes, int]:
    unparsed = bytes
    bytes_consumed = 0
    if chr(unparsed[0]).isdigit():
        first_colon_index = unparsed.find(b":")
        if first_colon_index == -1:
            raise ValueError("Invalid encoded value")
        length = int(unparsed[:first_colon_index])
        bytes_consumed = first_colon_index + 1 + length
    else:
        raise ValueError("Expected integer, got " + str(unparsed))
    return (unparsed[first_colon_index + 1 : bytes_consumed], bytes_consumed)


def decode_bencode_int(bytes: bytes) -> Tuple[int, int]:
    unparsed = bytes
    bytes_consumed = 0
    if chr(unparsed[0]) == "i":
        first_e_index = unparsed.find(b"e")
        if first_e_index == -1:
            raise ValueError("Invalid encoded value")
        bytes_consumed += first_e_index + 1
    else:
        raise ValueError("Expected int, got " + str(unparsed))
    return (int(unparsed[1:first_e_index]), bytes_consumed)


def decode_bencode_list(unparsed_bytes: bytes) -> Tuple[List[Any], int]:
    unparsed = unparsed_bytes
    bytes_consumed = 0
    res = []
    while unparsed:
        if len(unparsed) == 0:
            break
        if chr(unparsed[0]) == "l":
            decoded_list, bytes_consumed_l = decode_bencode_list(unparsed[1:])
            res.append(decoded_list)
            bytes_consumed += 1 + bytes_consumed_l
            unparsed = unparsed[1 + bytes_consumed_l :]
        if chr(unparsed[0]) == "e":
            bytes_consumed += 1
            break
        if chr(unparsed[0]).isdigit():
            decoded_string, bytes_consumed_s = decode_bencode_string(unparsed)
            res.append(decoded_string)
            bytes_consumed += bytes_consumed_s
            unparsed = unparsed[bytes_consumed_s:]
        elif chr(unparsed[0]) == "i":
            decoded_int, bytes_consumed_i = decode_bencode_int(unparsed)
            res.append(decoded_int)
            unparsed = unparsed[bytes_consumed_i:]
            bytes_consumed += bytes_consumed_i
        else:
            break
    return (res, bytes_consumed)


def decode_bencode_dict(unparsed_bytes: bytes) -> Tuple[dict, int]:
    # keys must be strings, values can be any bencode type
    unparsed = unparsed_bytes
    bytes_consumed = 0
    res = {}
    while True:
        if not unparsed:
            raise ValueError("Unexpected end of input")
        elif chr(unparsed[0]) == "e":
            bytes_consumed += 1
            break
        decoded_key, bytes_consumed_key = decode_bencode_string(unparsed)
        unparsed = unparsed[bytes_consumed_key:]
        bytes_consumed += bytes_consumed_key
        if not unparsed:
            raise ValueError("Unexpected end of input")
        decoded_value, bytes_consumed_v = decode_bencode_value(unparsed)
        unparsed = unparsed[bytes_consumed_v:]
        bytes_consumed += bytes_consumed_v
        res[decoded_key] = decoded_value
    return (res, bytes_consumed)


def decode_bencode_value(unparsed_bytes: bytes) -> Tuple[Any, int]:
    if not unparsed_bytes:
        raise ValueError("Unexpected end of input")
    elif chr(unparsed_bytes[0]).isdigit():
        return decode_bencode_string(unparsed_bytes)
    elif chr(unparsed_bytes[0]) == "i":
        return decode_bencode_int(unparsed_bytes)
    elif chr(unparsed_bytes[0]) == "l":
        return decode_bencode_list(unparsed_bytes[1:])
    elif chr(unparsed_bytes[0]) == "d":
        return decode_bencode_dict(unparsed_bytes[1:])
    else:
        raise ValueError(f"Invalid encoded value: {unparsed_bytes}")


def bencode_dict(dict: dict) -> bytes:
    result = b"d"
    for key, value in sorted(dict.items()):
        result += bencode_string(key) + bencode_arbitrary(value)
    result += b"e"
    return result


def bencode_string(string: bytes) -> bytes:
    return f"{len(string)}:{string}".encode()


def bencode_int(number: int) -> bytes:
    return f"i{number}e".encode()


def bencode_list(list: list) -> bytes:
    result = b"l"
    for item in list:
        result += bencode_arbitrary(item)
    result += b"e"
    return result


def bencode_arbitrary(value) -> bytes:
    if isinstance(value, bytes):
        return bencode_string(value)
    if isinstance(value, int):
        return bencode_int(value)
    if isinstance(value, list):
        return bencode_list(value)
    if isinstance(value, dict):
        return bencode_dict(value)
    raise ValueError(f"Unsupported type: {type(value)}")


def parse_file_info(bencoded_value: bytes):
    if chr(bencoded_value[0]) != "d":
        raise ValueError("Invalid torrent file: must be a dictionary")
    try:
        decoded_dict, _ = decode_bencode_dict(bencoded_value[1:])
        encoded_info = bencode_dict(decoded_dict[b"info"])
        decoded_encoded_info, _ = decode_bencode_dict(encoded_info[1:])
        print(f"Original info: {decoded_dict[b'info']}")
        print(f"Decoded encoded info: {decoded_encoded_info}")
        print(f"Tracker URL: {decoded_dict[b'announce'].decode()}")
        print(f"Length: {decoded_dict[b'info'][b'length']}")
        print(f"Info hash: {hashlib.sha1(encoded_info).hexdigest()}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def main():
    command = sys.argv[1]

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.
        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()
            if isinstance(data, list):
                return [bytes_to_str(item) for item in data]
            if isinstance(data, dict):
                return {
                    bytes_to_str(key): bytes_to_str(value)
                    for key, value in data.items()
                }

            return data

        # TODO: Uncomment the code below to pass the first stage
        print(json.dumps(bytes_to_str(decode_bencode(bencoded_value))))
    elif command == "info":
        with open(sys.argv[2], "rb") as f:
            bencoded_value = f.read()
        parse_file_info(bencoded_value)
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
