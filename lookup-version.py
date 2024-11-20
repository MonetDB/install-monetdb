#!/usr/bin/env python3

"""
Interpret MonetDB version strings and convert them to what Apt, Homebrew and
Windows need.

Usage: map-monet-version [--msi] [VERSION_STRING]

VERSION_STRING: nothing, '', 'latest', or for example '11.51.5', 'Aug2024-SP1'
or 'Aug2024_SP1'.

The mapping is performed by scraping https://www.monetdb.org/downloads/.

Output: something like:
    numeric=11.51.5
    name=Aug2024-SP1
    main_msi=https://www.monetdb.org/downloads/Windows/Aug2024-SP1/MonetDB5-SQL-Installer-x86_64-20241024.msi
    odbc_msi=https://www.monetdb.org/downloads/Windows/Aug2024-SP1/MonetDB-ODBC-Installer-x86_64-20241024.msi
"""


import argparse
import functools
import html.parser
import logging
import re
from typing import List, Optional
import unittest
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import urlopen


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

MONETDB_DOWNLOADS = 'https://www.monetdb.org/downloads/'
SOURCE_DOWNLOADS = MONETDB_DOWNLOADS + 'sources/'
WINDOWS_DOWNLOADS = MONETDB_DOWNLOADS + 'Windows/'


class IndexHtmlParser(html.parser.HTMLParser):
    """Parser for the index pages returned by monetdb.org/downloads/"""

    base_url: str
    in_pre: int
    hrefs: List[str]

    def __init__(self, base: str):
        super().__init__()
        self.base_url = base
        self.in_pre = 0
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.in_pre += 1
        elif tag == 'a' and self.in_pre > 0:
            for name, value in attrs:
                if name == 'href':
                    href = urljoin(self.base_url, value)
                    self.hrefs.append((value, href))
                    break
        return super().handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.in_pre -= 1
        return super().handle_endtag(tag)


def remote_ls(url: str):
    logger.info(f'Listing {url!r}')
    try:
        with urlopen(url) as req:
            bindata = req.read()
            encoding = req.headers.get_content_charset('utf-8')
            data = str(bindata, encoding)
    except HTTPError as e:
        exit(f'Could not retrieve {url}: {e}')
    except OSError as e:
        exit(f'Could not retrieve {url}: {e}')
    parser = IndexHtmlParser(url)
    parser.feed(data)
    links = [l for l in parser.hrefs if not l[0].startswith('?')]
    for link in links:
        logger.debug(f'  - {link}')
    return links


class VersionInfo:
    _numeric: Optional[str]
    _name: Optional[str]
    _main_msi: Optional[str]
    _odbc_msi: Optional[str]

    def __init__(self, version_string: str):
        self._numeric = None
        self._name = None
        self._main_msi = None
        self._odbc_msi = None

        if version_string in ['', 'latest', 'Latest']:
            self._numeric = self.lookup_numeric('Latest')
        elif re.match(r'^\d+[.]\d+[.]\d+$', version_string):
            self._numeric = version_string
        else:
            self._name = version_string.replace('_', '-')

    @property
    def name(self):
        if not self._name:
            assert self._numeric
            self._name = self.lookup_name(self._numeric)
        return self._name

    @property
    def numeric(self):
        if not self._numeric:
            assert self._name
            self._numeric = self.lookup_numeric(self._name)
        return self._numeric

    @property
    def split_numeric(self):
        v = self.numeric
        return split_numeric(v)

    @property
    def main_msi(self):
        if not self._main_msi:
            name = self.name
            (self._main_msi, self._odbc_msi) = self.lookup_msi(name)
        return self._main_msi

    @property
    def odbc_msi(self):
        if not self._odbc_msi:
            name = self.name
            (self._main_msi, self._odbc_msi) = self.lookup_msi(name)
        return self._odbc_msi

    def lookup_numeric(self, name):
        assert name
        logger.info(f'Looking up numeric form of named version {name!r}')
        url = urljoin(SOURCE_DOWNLOADS, name + '/')
        links = remote_ls(url)
        prefix = 'MonetDB-'
        suffix = '.zip'
        for name, url in links:
            if name.startswith(prefix) and name.endswith(suffix):
                numeric = name[len(prefix):-len(suffix)]
                logger.info(f'Found {numeric!r}')
                return numeric
        raise Exception('Could not find MonetDB-xx.yy.zz.zip in {url}')

    def lookup_msi(self, name):
        if not name:
            name = 'Latest'
        logger.info(
            f'Looking up Windows installers for named version {name!r}')
        url = urljoin(WINDOWS_DOWNLOADS, name + '/')
        links = remote_ls(url)
        main_msi = None
        odbc_msi = None
        for name, url in links:
            if not name.endswith('.msi'):
                continue
            if '-x86_64-' not in name:
                continue
            if '-SQL-Installer-' in name:
                main_msi = url
            if '-ODBC-Installer-' in name:
                odbc_msi = url
        if not main_msi:
            raise Exception(
                'Could not find MonetDB5-SQL-Installer-x86_64-XXXXXXXX.msi  in {url}')
        if not odbc_msi:
            raise Exception(
                'Could not find MonetDB5-ODBC-Installer-x86_64-XXXXXXXX.msi  in {url}')
        return (main_msi, odbc_msi)

    def lookup_name(self, numeric):
        # This one is the hardest because the website only has a mapping name->num.
        # We'll use bisection.

        logger.info(f"Looking up release name of version {numeric!r}")

        # This is what we're looking for
        desired = split_numeric(numeric)

        # This is what we're searching
        candidates = self.lookup_releases()

        # And this is what we compare
        @functools.lru_cache(maxsize=1000)
        def name2num(name):
            num = self.lookup_numeric(name)
            return split_numeric(num)

        while len(candidates) > 0:
            pos = len(candidates) // 2
            candidate = candidates[pos]
            num = name2num(candidate)
            if desired < num:
                # discard high side
                candidates = candidates[:pos]
            elif desired > num:
                candidates = candidates[pos + 1:]
            else:
                return candidate

        # Not found
        raise Exception(
            f'Could not find a release with version number {numeric!r}')

    def lookup_releases(self):
        pattern = re.compile(r'^(([A-Z][a-z][a-z])(\d\d\d\d)(?:-SP(\d+))?)/$')
        months = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6,
                      Jul=7, Aug=8, Sep=9, Oct=10, Nov=11, Dec=12)
        releases = []
        parsed_release = {}
        hrefs = remote_ls(SOURCE_DOWNLOADS)
        for name, url in hrefs:
            m = pattern.match(name)
            if not m:
                continue
            release = m[1]
            year = int(m[3])
            month = months[m[2]]
            sp = int(m[4] or 0)
            releases.append(release)
            parsed_release[release] = (year, month, sp)
        releases.sort(key=lambda r: parsed_release[r])
        return releases


def split_numeric(numeric):
    return tuple(int(part) for part in numeric.split('.'))


class VersionInfoTests(unittest.TestCase):
    # These may need adjusting from time to time
    RECENT = ('Aug2024', '11.51.3', '20240819.msi')
    LESS_RECENT = ('Dec2023-SP4', '11.49.11', '20240629.msi')

    def test_getters(self):
        # These shouldn't need to do I/O
        self.assertEqual(VersionInfo('Aug2024-SP9').name, 'Aug2024-SP9')
        self.assertEqual(VersionInfo('11.51.9').numeric, '11.51.9')
        self.assertEqual(VersionInfo('11.51.9').split_numeric, (11, 51, 9))

    def test_recent_by_name(self):
        name, numeric, msi_tail = self.RECENT
        version_info = VersionInfo(name)
        self.assertEqual(version_info.name, name)
        self.assertEqual(version_info.numeric, numeric)
        main_msi = version_info.main_msi
        self.assertIn('SQL', main_msi)
        self.assertIn(msi_tail, main_msi)
        odbc_msi = version_info.odbc_msi
        self.assertIn('ODBC', odbc_msi)
        self.assertIn(msi_tail, odbc_msi)

    def test_recent_by_num(self):
        name, numeric, msi_tail = self.RECENT
        version_info = VersionInfo(numeric)
        self.assertEqual(version_info.name, name)
        self.assertEqual(version_info.numeric, numeric)
        main_msi = version_info.main_msi
        self.assertIn('SQL', main_msi)
        self.assertIn(msi_tail, main_msi)
        odbc_msi = version_info.odbc_msi
        self.assertIn('ODBC', odbc_msi)
        self.assertIn(msi_tail, odbc_msi)

    def test_latest_by_name(self):
        latest = VersionInfo('Latest')
        recent = VersionInfo(self.RECENT[0])
        older = VersionInfo(self.LESS_RECENT[0])

        self.assertGreaterEqual(latest.split_numeric, recent.split_numeric)
        self.assertGreater(recent.split_numeric, older.split_numeric)

        # The .name attribute should be a proper release name, not 'Latest'.
        # Look up that name and check that the other attributes match
        self.assertNotEqual(latest.name, 'Latest')
        self.assertNotEqual(latest.name, '')
        proper = VersionInfo(latest.name)
        proper_numeric_parts = proper.split_numeric
        self.assertEqual(proper_numeric_parts, latest.split_numeric)
        proper_main_msi = proper.main_msi
        self.assertEqual(proper_main_msi, latest.main_msi)
        proper_odbc_msi = proper.odbc_msi
        self.assertEqual(proper_odbc_msi, latest.odbc_msi)

    def test_lowercase_latest(self):
        reference = VersionInfo('Latest')
        latest = VersionInfo('latest')
        self.assertEqual(latest.numeric, reference.numeric)
        self.assertEqual(latest.name, reference.name)

    def test_empty_latest(self):
        reference = VersionInfo('Latest')
        empty = VersionInfo('')
        self.assertEqual(empty.numeric, reference.numeric)
        self.assertEqual(empty.name, reference.name)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('version_string')
    argparser.add_argument('--name', action='store_true',
                           help='Print release name')
    argparser.add_argument('--msi', action='store_true',
                           help='Print Windows installer URLs')
    argparser.add_argument('-v', '--verbose', action='store_true')
    args = argparser.parse_args()
    # print(args)

    if args.verbose:
        logger.setLevel(logging.INFO)

    version_info = VersionInfo(args.version_string)
    print(f'numeric={version_info.numeric or ""}')
    if args.name:
        print(f'name={version_info.name or ""}')
    if args.msi:
        print(f'main_msi={version_info.main_msi or ""}')
        print(f'odbc_msi={version_info.odbc_msi or ""}')
