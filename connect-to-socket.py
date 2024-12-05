#!/usr/bin/env python3

"""Connect to port 50_000 to verify MonetDB is running"""

import socket
import time

addrs = [
    ('::1', 50_000),
    ('127.0.0.1', 50_000),
]

duration = 10.0
start_time = time.time()
deadline = start_time + duration
sleep_interval = 0.3
fudge = 0.5


while True:
    for a in addrs:
        print(f'Connecting to {a}', end='', flush=True)
        try:
            timeout = deadline = time.time()
            timeout = min(timeout, 2.0)    # never more than 2s
            timout = max(0.2, timeout)     # never less than 0.2s
            sock = socket.create_connection(a, timeout=timeout)
            print(' ==> connected!')
            print('Bye')
            exit(0)
        except OSError as e:
            print(f' ==> failed: {e}')

    now = time.time()
    if now > deadline:
        print(f"Abort: It's been {now - start_time:.2f}s and port 50_000 is still not reachable")
        exit(1)

    sleep_time = min(sleep_interval, deadline - now)
    print(f'Sleeping {sleep_time:.2f}s')
    time.sleep(sleep_time)
    sleep_interval *= 1.5
