TODO
====

The end goal is to create GitHub Action that installs MonetDB for use
in tests of other components. For example, pymonetdb.

The plan is to install a binary distribution from monetdb.org, not build
it from source. This is quicker and provides 'official' binaries.

It should support

- Linux (x86_64)
- Windows (x86_64)
- MacOS through Homebrew (arm64 and x86_64)

After running the action.

- MonetDB should be installed and on the path
- monetbd should be running and a database 'demo' should exist


Future work
===========

Picking a specific version. For binary installs this depends on what's still
available at monetdb.org.

Source installs


Steps
=====

1. Create an embeddable workflow that installs MonetDB on Ubuntu, and a workflow
   that tests it.

2. MacOS

3. Outputs: bindir, libdir, includedir