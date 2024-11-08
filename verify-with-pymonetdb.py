#!/usr/bin/env python3

import argparse
import pymonetdb

argparser = argparse.ArgumentParser()
argparser.add_argument('url')

def main(args):
    with pymonetdb.connect(args.url) as conn, conn.cursor() as c:
        c.execute("SELECT name, value FROM sys.environment")
        props = {}
        for k, v in c.fetchall():
            props[k] = v
        for k, v in props.items():
            if k in ['gdk_dbpath', 'monet_pid', 'revision', 'monet_version', 'monet_release']:
                print(f"{k}={v!r}")
        try:
            # run this in a try block because 'peer' was introduced only in Aug2024.
            c.execute('SELECT peer FROM sys.sessions WHERE sessionid = current_sessionid()')
            peer = c.fetchone()[0]
            print(f'peer={peer}')
        except pymonetdb.Error:
            pass


if __name__ == "__main__":
    args = argparser.parse_args()
    exit(main(args) or 0)