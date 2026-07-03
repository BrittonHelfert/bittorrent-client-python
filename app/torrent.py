"""Parsed representation of a .torrent metainfo file.

The raw metadata is decoded once into a ``Torrent`` object so later stages
(tracker request, handshake, piece download) can reuse the derived values
instead of re-parsing the file. ``info_hash`` is kept as the raw 20-byte
SHA-1 digest — the form the tracker and peer protocol actually need — and
rendered to hex only when printing.
"""

import hashlib
from dataclasses import dataclass

from .bencode import decode, encode


@dataclass
class Torrent:
    announce: str  # tracker URL
    length: int  # total file size in bytes
    info_hash: bytes  # 20-byte SHA-1 of the bencoded info dict
    piece_length: int  # bytes per piece
    piece_hashes: list[bytes]  # one 20-byte SHA-1 per piece
    info: dict  # raw info dict, for fields we don't surface yet

    @classmethod
    def from_bytes(cls, data: bytes) -> "Torrent":
        meta = decode(data)
        info = meta[b"info"]
        pieces = info[b"pieces"]
        return cls(
            announce=meta[b"announce"].decode(),
            length=info[b"length"],
            info_hash=hashlib.sha1(encode(info)).digest(),
            piece_length=info[b"piece length"],
            piece_hashes=[pieces[i : i + 20] for i in range(0, len(pieces), 20)],
            info=info,
        )

    @classmethod
    def from_file(cls, path: str) -> "Torrent":
        with open(path, "rb") as f:
            return cls.from_bytes(f.read())
