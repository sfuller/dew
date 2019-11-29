#
# Dew Cmake Bootstrap + functionality module
# https://github.com/sfuller/dew
#
# It is not recommended to modify this file, as it may need to be updated to ensure future dew version compatibility.
#
# It is encouraged to check this file into your project's VCS. Doing so will allow your cmake project to easily
# integrate with Dew.
#

#
# For FindPython3 (3.12) and IN_LIST operator (3.4)
#
cmake_minimum_required(VERSION 3.12)

function(integrate_dew)
    #
    # Skip everything if we are building from dew
    #
    if ($ENV{INVOKED_BY_DEW})
        return()
    endif()

    #
    # Advise the user that setting the build type is necessary for debug dependencies.
    #
    if (NOT CMAKE_BUILD_TYPE)
        message(WARNING "CMAKE_BUILD_TYPE is not set. Dew will build release dependencies by default.")
    endif()

    #
    # Acquaint CMake with dew prefix
    #
    if ("${CMAKE_BUILD_TYPE}" STREQUAL Debug)
        set(dew_cmake_prefix_suffix debug)
    else()
        set(dew_cmake_prefix_suffix release)
    endif()

    #
    # Run dew update
    #
    option(DEW_AUTOUPDATE "Automatically update dew prefixes as part of cmake generation." ON)
    if (DEW_AUTOUPDATE)
        find_package(Python3 COMPONENTS Interpreter REQUIRED)
        message(STATUS "Installing dew")
        execute_process(
            COMMAND "${Python3_EXECUTABLE}" -m pip install --user dew-pacman
            RESULT_VARIABLE install_dew_result
        )
        if (NOT install_dew_result EQUAL 0)
            message(FATAL_ERROR "Failed to install dew with pip: result: ${install_dew_result}.")
        endif()
        message(STATUS "Building dew dependencies")
        execute_process(COMMAND "${Python3_EXECUTABLE}" -m dew update --CC "${CMAKE_C_COMPILER}"
                        --CXX "${CMAKE_CXX_COMPILER}" --build-type ${dew_cmake_prefix_suffix}
                        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
                        RESULT_VARIABLE dew_res)
        if(NOT dew_res EQUAL 0)
            message(FATAL_ERROR "Unable to run dew: ${dew_res}")
        endif()
    endif()

    set(dew_output_path "${CMAKE_CURRENT_SOURCE_DIR}/.dew")
    set(dew_cmake_prefix_path "${dew_output_path}/prefix-${dew_cmake_prefix_suffix}")
    set(dew_cmake_module_path "${dew_cmake_prefix_path}/share/cmake/Modules")

    #
    # Create a warning and return early if dew directory does not exist.
    #
    if (NOT EXISTS "${dew_output_path}")
        message(WARNING "Could not find .dew directory. Please follow the project's instructions for installing and running dew.")
        return()
    endif()

    #
    # Check if we have already added the dew directory to CMAKE_PREFIX_PATH
    #
    set(needs_new_prefix TRUE)
    if ("${dew_cmake_prefix_path}" IN_LIST CMAKE_PREFIX_PATH)
        set(needs_new_prefix FALSE)
    endif()

    #
    # Check if we have already added the dew cmake module directory to CMAKE_MODULE_PATH
    #
    set(needs_new_module_path TRUE)
    if ("${dew_cmake_module_path}" IN_LIST CMAKE_MODULE_PATH)
        set(needs_new_module_path FALSE)
    endif()

    #
    # Add dew directory to CMAKE_PREFIX_PATH if necessary
    #
    if ("${needs_new_prefix}")
        set(CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH} "${dew_cmake_prefix_path}" CACHE PATH "" FORCE)
    endif()

    #
    # Add dew cmake module directory to CMAKE_MODULE_PATH if necessary
    #
    if ("${needs_new_module_path}")
        set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${dew_cmake_module_path}" CACHE PATH "" FORCE)
    endif()

    set(DEW_CMAKE_PREFIX_PATH ${dew_cmake_prefix_path} PARENT_SCOPE)
endfunction()
