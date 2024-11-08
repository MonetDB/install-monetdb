A GitHub Action to install MonetDB
==================================

> **NOTE** This Action is in its early stages.
>
> This document describes the way it is intended to work, not how it currently
> works. Right now, only binary installs work, nothing is configurable and no
> server is started on Windows.


This [GitHub Action] installs [MonetDB].
It can be used to test projects that interact with MonetDB.
For example,

```
  run_mclient:
    runs-on: ubuntu-latest
    steps:
    - uses: MonetDB/install-monetdb@v1
    - run: mclient -d demo 'SELECT * FROM environment'
```

The step `uses: MonetDB/install-monetdb@v1` takes care of
1. Installing MonetDB and putting it on the PATH
2. Creating a database 'demo'
3. Starting the server
4. Creating a '.monetdb' file with user=monetdb and password=monetdb

It works on Linux, MacOS and Windows runners. It installs binary packages unless
configured to build from source.
* On Linux, it installs .deb packages downloaded from [monetdb.org][MonetDB].
* On Windows, it uses .msi installers from [monetdb.org][MonetDB].
* On MacOS, in installs MonetDB from [Homebrew].

When building from source, it can build from a pre-downloaded source tree or it
can check out code from MonetDB's Mercurial repository or its GitHub mirror.


Inputs
------

If no parameters are specified, this Action installs the latest binary packages.
If **version** is specified, it tries to install that specific version of the
binaries. If **source** is specified, it tries to compile the sources found in
that directory. If **rev** is specified, it tries to check out the given
revision from MonetDB's GitHub repository, or from whatever repository is
configured through **hg_repo** or **git_repo**.

* **version**: The version number, written either numerically (11.51.5) or as
  name (Aug2024-SP1 or Aug2024_SP1). The default is to install the latest
  version. Cannot be used together with **source** or **rev**.

* **source**: Path to the MonetDB source tree. If specified, MonetDB will be
  built from these sources. This action will try to install build dependencies
  such as cmake. No default.  Cannot be used together with **version** or **rev**.

* **rev**: Revision to check out from **git_repo** or **hg_repo**. No default.
  Cannot be used together with **version** or **source**.

  Uses the GitHub mirror rather than the primary Mercurial repository when
  neither **git_repo** nor **hg_repo** is given. This is because GitHub Action
  runners tend to have truly excellent network connectivity to GitHub. However,
  if you wish to compile bleeding edge sources make sure to specify **hg_repo**
  because the GitHub mirror may lag slightly behind.

* **hg_repo**: Mercurial repo to clone from when **rev** is given.
  Defaults to `https://dev.monetdb.org/hg/MonetDB/`.

* **git_repo**: Git repository to clone from when **rev** is given
  and **hg_repo** is not.


Outputs
-------

* **prefix**: Directory under which MonetDB will be installed.
  For example, `/usr`, `/usr/local` or `C:\Program Files\MonetDB\MonetDB5`.

* **bindir**: Directory where executables have been installed. Will contain for
  example `mclient` or `mclient.exe` on Windows.

* **libdir**: Directory where libraries have been installed. Will contain for
  example `libmonetdbe.so`, `libmonetdbe.dylib` or `monetdbe.dll`.

* **includedir**: Directory where header files have been installed. Will contain
  for example `monetdb/monetdb_config.h`.


Example
-------

TODO



[MonetDB]: https://monetdb.org/
[GitHub Action]: https://github.com/features/actions
[Homebrew]: https://brew.sh/