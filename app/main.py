import json
import sys

# import bencodepy - available if you need it!
# import requests - available if you need it!


# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"
def decode_bencode(bencoded_value):
    if chr(bencoded_value[0]).isdigit():
        first_colon_index = bencoded_value.find(b":")
        if first_colon_index == -1:
            raise ValueError("Invalid encoded value")
        return bencoded_value[first_colon_index + 1 :]
    elif chr(bencoded_value[0]) == "i" and chr(bencoded_value[-1]) == "e":
        # return without quotations
        return int(bencoded_value[1:-1])
    elif chr(bencoded_value[0]) == "l":
        return decode_bencode_list(bencoded_value[1:])
    else:
        raise ValueError("Invalid encoded value")


def decode_bencode_list(bencoded_value):
    unparsed = bencoded_value
    res = []
    while unparsed:
        if len(unparsed) == 0:
            break
        if chr(unparsed[0]) == "l":
            l = decode_bencode_list(unparsed[1:])
            res.append(l)
            character_length_of_l = sum([len(str(item)) for item in l])
            unparsed = unparsed[1 + character_length_of_l :]

        if chr(unparsed[0]) == "e":
            break
        if chr(unparsed[0]).isdigit():
            first_colon_index = unparsed.find(b":")
            if first_colon_index == -1:
                raise ValueError("Invalid encoded value")
            length = int(unparsed[:first_colon_index])
            unparsed = unparsed[first_colon_index + 1 :]
            res.append(unparsed[:length])
            unparsed = unparsed[length:]
        elif chr(unparsed[0]) == "i":
            first_e_index = unparsed.find(b"e")
            if first_e_index == -1:
                raise ValueError("Invalid encoded value")
            res.append(int(unparsed[1:first_e_index]))
            unparsed = unparsed[first_e_index + 1 :]
        else:
            break
    return res


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

            raise TypeError(f"Type not serializable: {type(data)}")

        # TODO: Uncomment the code below to pass the first stage
        print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
