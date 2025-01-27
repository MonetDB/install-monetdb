A GitHub Action to install MonetDB
==================================


This [GitHub Action] installs [MonetDB].
It can be used to test projects that interact with MonetDB.
For example,

```
  run_mclient:
    runs-on: ubuntu-latest
    steps:
    - uses: MonetDB/install-monetdb@v0.6
    - run: mclient -d demo -s 'SELECT * FROM environment'
```

The step `uses: MonetDB/install-monetdb@v0.6` takes care of
1. Installing MonetDB and putting it on the PATH
2. Creating a database 'demo'
3. Starting the server
4. Creating a '.monetdb' file with user=monetdb and password=monetdb

It works on Linux, MacOS and Windows runners.
* On Linux, it installs .deb or .rpm packages downloaded from [monetdb.org][MonetDB].
* On Windows, it uses .msi installers from [monetdb.org][MonetDB].
* On MacOS, it installs MonetDB from [Homebrew].

<br>

> **NOTE** Not everything works as it's supposed to yet:
> 1. On Windows, `mclient` does not work, for unclear reasons.
> 2. On MacOS, only the latest version can be installed because earlier versions
>    are no longer available through Homebrew.

<br>

See [CHANGELOG](./CHANGELOG.md) for the release history of this Action.

Inputs
------

* **version**: Version to install, either as a number (11.51.5) or as a name
  (Aug2024-SP1). Names with underscores (Aug2024_SP1) are also accepted.
  The default is to install the latest version.


Outputs
-------

* **prefix**: Directory under which MonetDB will be installed.
  For example, `/usr/local`, `/opt` or `C:\Program Files\MonetDB\MonetDB5`.

* **bindir**: Directory where executables have been installed.
  Contains `mclient` or `mclient.bat`.

* **libdir**: Directory where libraries have been installed.
  Contains `libmonetdbe.so`, `libmonetdbe.dylib` or `monetdbe.lib`.

* **includedir**: Directory where header files have been installed.
  Contains `monetdbe_config.h`.

* **dbfarm**: Location of the dbfarm.
  Except on Windows because monetdbd does not support Windows.


[MonetDB]: https://monetdb.org/
[GitHub Action]: https://github.com/features/actions
[Homebrew]: https://brew.sh/

