Dew
===
*D*evelopment *E*nvironment *W*rangler

What is this?
-------------
Dew is a package manager for C/C++ dependencies. It aims to make dependency management and configuration easier, like what Cargo does for Rust. For each dependency listed in a 'dewfile', Dew downloads the source of the dependency, builds it, and installs it's files in a prefix directory that can be used by your project.

What is supported?
------------------
Right now it supports dependencies built with CMake. Later it will support dependencies built with Make.

Is it stable? Is it a good idea to use this for projects in production?
-----------------------------------------------------------------------
lol no
