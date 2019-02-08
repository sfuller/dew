# The Dewtorial
Welcome to the dewtorial! This tutorial will guide you through setting up a dew project and get you acquainted to the
most common dew operations.

## Step 1: Creating a dewfile
A dewfile defines your project's dependencies, where to retrieve (pull) them from, and what version of them to pull.

Dew uses the file in your project named `dewfile.json` a the project's dewfile. A dewfile looks like this:


    {
        "dependencies":
        [
            {
                "name": "glfw",
                "type": "git",
                "url": "git@github.com:glfw/glfw.git",
                "head": "master"
                "ref": "463ef7eb71268f57790fdb67f26d328b45d3346e"
            }
        ]
    }  
    
Most of the dependency fields should be pretty obvious. Each dependency (chosen by you) has a name by which it is 
addressed by. The `type` field describes which mechanism is used for pulling and updating it (remote). The `url` field 
is used to describe to the remote where the dependency is located.

The `head` and `ref` fields are less obvious. While the names of these fields are derived from git nomenclature, they
are have a specific meaning within the context of dew which is relevant to each type of remote within dew.

In dew, a head refers to a codeline, and a ref refers to a revision which occurs inside of that codeline. The head field
exists as a way for the remote to retrieve a ref at the tip of the head and as a potential hint to the remote mechanism 
to assist retrieval of the dependency.

For git remotes, the `head` field refers to a branch, and the `ref` field refers to a git commit hash.


## Step 2: Updating dependencies
Updating dependencies in dew means pulling and building each dependency, and then installing each dependency in the dew
output directory. By default, all dependencies are stored in `.dew/prefx`, and since they are installed using CMake,
they are organized in a prefix structure, ready for use by your CMake project or another buildsystem.

To update your dependencies, just run `dew update` from your project directory. (Remember, the project directory is the
directory where your dewfile is.)


## Step 3: Integrating dew with your CMake project
Dew offers a CMake module to help reduce friction between dew and your CMake project. You can instantiate the dew CMake
module into your project by running the `dew bootstrap` command in the directory which you want to place the dew CMake 
module in. It is recommended you check this module into your version control system. 

To use the module, include it at the top of your CMakeLists.txt file.

    include(./dew.cmake)
    integrate_dew()
    
The integrate_dew cmake function will look for the dew output directory. If it is found, it will add the dew output 
paths to your cmake prefix and module path variables, if they are not  part of those variables already.

If you wish to not integrate the dew CMake module, you may invoke CMake and include the dew output paths as part of the
invocation: 

    cmake .. -DCMAKE_PREFIX_PATH=[project dir]/.dew/prefix -DCMAKE_MODULE_PATH=[project dir]/.dew/prefix/share/cmake/Modules
    

## Step 4: Upgrading a dew dependency
It is easy to upgrade a dew dependency to the latest version. The `dew upgrade` command will update the dependency's ref
to the latest at the dependency's head. You may also manually edit the dewfile and adjust the head and/or ref.

After making such modifications, either using `dew upgrade` or by editing the dewfile, just run `dew update` again to 
install the new versions of the dependencies.


## Step 5: Local work
You may find yourself in a situation where you are working on a project within a dependening project. Dew supports this
use case with the `workon` and `finish` commands. These two commands give you a git-submodules-like workflow, but 
without the coupling that submodules often bring.

It is easy to start development on a dependency with the `workon` command. Specify the dependency you wish to work on 
and a path, and dew will place the source directory of that dependency at that path, and use your local copy for builds.
It is also possible to register existing source directories.

The `finish` command closes the loop. Use the `finish` command to update your dewfile with the head and ref of your 
local work and unregister the local source directory.    
 