CHANGELOG
=========


Unreleased
----------



Version 0.6.0 - 2024-12-05
--------------------------

Features:

* Installs MonetDB from binary distributions
  * .deb and .rpm packages from [monetdb.org][downloads] on Linux
  * .msi installers from [monetdb.org][downloads] on Windows
  * [Homebrew](https://brew.sh) packages on MacOS (only latest version of MonetDB)

* Sets outputs `prefix`, `bindir`, `includedir`,`libdir` and `versionnumber`

* Creates and starts a database `demo` for use in tests.

* Creates `~/.monetdb` so `mclient` does not prompt for a password.

Known defects:

* `mclient` does not work on Windows

* Only the latest version of MonetDB is available from Homebrew so older
  versions cannot be installed on MacOS.



[downloads]: https://monetdb.org/downloads