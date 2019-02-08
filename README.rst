Dew
===
**D**\ evelopment **E**\ nvironment **W**\ rangler

What is this?
-------------
Dew is a dependency manager for C/C++ dependencies. It aims to make dependency management and configuration easier,
while keeping out of the way. For each dependency listed in a 'dewfile', Dew downloads the source of the dependency, builds
it, and installs it's files in a prefix directory which can be used by your project.

Dew is inspired by Cargo, the defacto package manager and build system for Rust.


Is it stable? Is it a good idea to use this for projects in production?
-----------------------------------------------------------------------
It's getting there. Most of the architecture and scope of Dew is hardening, so be sure to check back for a 1.0 release.


Installation
------------
Dew is hosted on PyPI and can be installed with pip.

.. code-block:: bash

    pip3 install dew-pacman


Note: dew requires python 3.6 and above.

It is recommended to include a requirements.txt file in your dew-using projects specifying the version of dew you are
using.


Usage
-----
Check out the following pages for information on how to use dew:

* `The Dewtorial`_
* `Command Reference`_

.. _The Dewtorial: docs/dewtorial.md
.. _Command Reference: docs/commands.md
