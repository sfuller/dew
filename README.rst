Dew
===
**D**\ evelopment **E**\ nvironment **W**\ rangler

What is this?
-------------
Dew is a package manager for C/C++ dependencies. It aims to make dependency management and configuration easier, like
what Cargo does for Rust. For each dependency listed in a 'dewfile', Dew downloads the source of the dependency, builds
it, and installs it's files in a prefix directory that can be used by your project.

What is supported?
------------------
Right now it supports dependencies built with CMake. Later it will support dependencies built with Make.

Is it stable? Is it a good idea to use this for projects in production?
-----------------------------------------------------------------------
lol no

Installing and Usage
--------------------
.. code-block:: bash

    pip3 install dew-pacman
    python3 -m dew

Run dew in a directory which contains a ``dewfile.json`` file.

What does a dewfile look like?
------------------------------
Right now dewfiles look like this. Here is an example of a dewfile requiring the dependency glfw:

.. code-block:: json

    {
        "dependencies":
        [
            {
                "name": "glfw",
                "type": "git",
                "url": "git@github.com:glfw/glfw.git",
                "ref": "master"
            }
        ]
    }

After running dew, glfw will be installed in the ``.dew/install`` prefix directory located in the root of your project
containing the dewfile. You can pass this prefix path into your buildsystem to use all of the installed dependencies.

Better documentation for dewfiles will surface in the future.
