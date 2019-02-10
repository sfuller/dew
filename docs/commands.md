
# Commands

Dew functionality is split up into commands. Each command is invoked by specifying the command name as the first
positional argument of the dew command.

Commands operate on a project. A project is a directory containing a dewfile. By default, dew looks for a dewfile named 
`dewfile.json` in the present working directory.

## Shared Arguments

There are a few arguments shared between all commands.
 
##### `-h`, `--help`
Show help information and exit with a non-zero exit code. If a command is given, help for the command will be shown. 

##### `--verbose`
Show verbose output. Useful for debugging issues.

##### `-v`, `--version`   
Output the version of dew and exit with exit code 0.

##### `--output-path`
Specify the path to the dew output directory. By default, the output directory is `.dew` of the project directory. This
argument can be used to specify a different directory to use.

##### `--dewfile`
Specify the path to the project's dewfile. Note that the project directory will always be the present working directory 
of the dew command. The dewfile does not have to reside in the project directory. By default, the `dewfile.json` file in
the project directory is used as the dewfile. 




## `update`
The update command updates your dew prefix directory to contain the dependencies you have speicified in your dewfile.

#### Optional Arguments

##### `--CC`
Specify a path to the C compiler to use.

##### `--CXX`
Specify a path to the C++ compiler to use.

##### `--prefix`
Specify an additional prefix path to use. This argument can be used multiple times.

##### `--cmake-generator`
Specify the CMake generator to use.

##### `--cmake-executable`
Specify the path to the CMake executable to use.




## `bootsrap`
The bootstrap command places a CMake module in the current directory. This CMake module provides helpful functionality
for your CMake project.




## `clean`
Comming soon.




## `upgrade`
The upgrade command updates the ref of a dependency to the latest ref associated with the dependency's head.

##### `DEPENDENCY`
The name of the dependency to upgrade.




## `workon`
The workon command sets up a dependency for local work. It will create a copy of the dependency's source to the 
specified path, or can register an existing directory as the source for local work. When a local source directory is 
registered with dew, the dependency will be built from the local source directory instead of the pulled source directory
inside of the dew output directory.  

After finishing local work, use the `finish` command. 

###### `DEPENDENCY`
The name of the dependency to work on locally

##### `PATH`
The path to register for the local dependency. By default, the dependency's source will be copied to this path. If the 
path is not empty, and the `--existing` argument is not given, the dependency's source will not be copied and the 
dependency will not be registered for local development.

##### `--existing`
If this argument is given, the dependency will be registered for development at the given PATH. No checking is done on 
the given path if this argument is given.




## `finish`
The finish command finishes local work done on a dependency registered for local work by the `workon` command. Work is
finished by detecting the current ref and head of the local source directory, applying the new ref and head to the
dewfile, and then unregister the local directory for local work. The local source directory is not modified or deleted.

If there are pending changes in the local source directory, nothing will be done and you will be warned. This is to  

##### `DEPENDENCY`
The name of the dependency to finish work on. 




## `build`
The build command is a convenience command which invokes cmake using the properties that have been previously defined
through the arguments of the `update` command.

Run this command in your dew project directory and specify the build directory to be used or created.

##### `BUILD_DIRECTORY`
The build directory use. CMake will be invoked from this directory, and the present working directory will be used as
the source path. 
