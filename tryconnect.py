#!/usr/bin/env python3

import socket

addrs = [
    ('::1', 50_000),
    ('127.0.0.1', 50_000),
]

for a in addrs:
    print(f"Connecting to {a}")
    try:
        sock = socket.create_connection(a, timeout=5.0)
    except OSError as e:
        print(f"==> failed: {e}")
        continue
    local_addr = sock.getsockname()
    peer_addr = sock.getpeername()
    print(f"==> connected: local={local_addr}, peer={peer_addr}")
    break

print("Bye")