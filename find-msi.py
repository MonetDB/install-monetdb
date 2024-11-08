#!/usr/bin/env python3

"""Scrape the MonetDB downloads page for the URL of the .msi files for the latest release"""


import html.parser
import urllib.request


dir = 'https://www.monetdb.org/downloads/Windows/Latest/'

with urllib.request.urlopen(dir) as req:
    bindata = req.read()
    encoding = req.headers.get_content_charset('utf-8')
    data = str(bindata, encoding)

# <a href="MonetDB-ODBC-Installer-i386-20241024.msi">MonetDB-ODBC-Installer-i386-20241024.msi</a>
# <a href="MonetDB-ODBC-Installer-x86_64-20241024.msi">MonetDB-ODBC-Installer-x86_64-20241024.msi</a>
# <a href="MonetDB5-SQL-Installer-i386-20241024.msi">MonetDB5-SQL-Installer-i386-20241024.msi</a>
# <a href="MonetDB5-SQL-Installer-x86_64-20241024.msi">MonetDB5-SQL-Installer-x86_64-20241024.msi</a>

class MyHTMLParser(html.parser.HTMLParser):
    """Parse HTML and find the href of all A tags inside a PRE.

    Store them in .hrefs
    """
    def __init__(self):
        super().__init__()
        self.in_pre = 0
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.in_pre += 1
        if tag == 'a' and self.in_pre > 0:
            for name, value in attrs:
                if name == 'href':
                    self.hrefs.append(value) 

        return super().handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.in_pre -= 1
        return super().handle_endtag(tag)

parser = MyHTMLParser()
parser.feed(data)
hrefs = parser.hrefs


def classify(href):
    if not href.endswith('.msi'):
        return None
    if '-x86_64-' not in href:
        return None
    if '-SQL-Installer-' in href:
        return 'main'
    if '-ODBC-Installer-' in href:
        return 'odbc'
    return None

msi_links = {}
for href in hrefs:
    cl = classify(href)
    if not cl:
        continue
    existing = msi_links.get(cl)
    if existing is not None:
        exit("Found more than one {cl} link: {existing!r} and {href!r}")
    msi_links[cl] = href

#print(msi_links)
print(f'main_msi={dir}{msi_links["main"]}')
print(f'odbc_msi={dir}{msi_links["odbc"]}')
