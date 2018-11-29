#
# Dew Cmake Bootstrap + functionality module
# https://github.com/sfuller/dew
#
# If you see this file in your dew-using project:
# *****
# DO NOT MODIFY THIS FILE. YOUR CHANGES WILL BE OVERWRITTEN.
# *****
# This file is installed into your cmake project by dew and is managed by dew.
#
# It is encouraged to check this file into your project's VCS. Doing so will allow your cmake project to automatically
# manage installing dew.
#
cmake_minimum_required(VERSION 3.2)

# TODO: Have the dew bootstrap specify a version to get get from pip, so that everyone building the project stays on the
# same version of dew.
set (dew_pypi_package_name "dew-pacman")

option(DEW_CMAKE_INTEGRATION_ENABLED "Integrate Dew into the build process and update automatically" ON)

#
# Call this function at the very very beginning of your CMakeLists.txt to integrate dew with your cmake project.
# Note: This is not needed to use dew with your project, but doing so mean you will need to invoke dew manually
# whenever you update your dewfile. This module also installs dew if it is not installed, which makes it easier for
# others to build your project.
#
function(setup_dew target_name dewfile_path)

    #
    # Create dummy target if dew integration is disabled.
    #
    if (NOT DEW_CMAKE_INTEGRATION_ENABLED)
        add_custom_target("${target_name}")
        return()
    endif()

    #
    # Get name of python executable. We gotta add a '.exe' prefix if we're on windows, obviously.
    #
    if (WIN32)
        set(sep ";")
        set(python_executable_name "python.exe")
    else()
        set(sep ":")
        set(python_executable_name "python")
    endif()

    #
    # Find our python interpreter, and set up some python related variables. Also, set the current cmake system
    # environment to use our python path when running python commands during the CMake configure phase.
    #
    find_package(PythonInterp 3.6)

    if (NOT PYTHONINTERP_FOUND)
        message(FATAL_ERROR
            "Python 3.6 not found. Dew will not function. To build without Dew, set the cache variable "
            "DEW_CMAKE_INTEGRATION_ENABLED to OFF"
        )
    endif()

    set(pythonpath "")
    foreach(prefix_path ${CMAKE_PREFIX_PATH})
        set(pythonpath "${pythonpath}${sep}${prefix_path}/lib/python3")
    endforeach()
    set(ENV{PYTHONPATH} "${pythonpath}")

    set(venv_path "${CMAKE_CURRENT_BINARY_DIR}/dew_venv")

    set(dew_python_executable "${PYTHON_EXECUTABLE}")

    #
    # Check if dew is installed on main interpreter
    #
    execute_process(
        COMMAND "${PYTHON_EXECUTABLE}" -m dew --version
        RESULT_VARIABLE dew_check_result
        OUTPUT_VARIABLE dew_check_output
        ERROR_VARIABLE  dew_check_error
    )
    if (NOT dew_check_result EQUAL 0)
        #
        # No dew installed on given python interpreter. Let's use a virtual env with dew installed there.
        #

        #
        # Does the virtual env exist? If not, let's create it.
        #
        if (NOT EXISTS "${venv_path}")
            message(STATUS "Creating dew virtualenv at ${venv_path}")
            execute_process(
                COMMAND "${PYTHON_EXECUTABLE}" -m ensurepip
                RESULT_VARIABLE update_venv_result
                OUTPUT_VARIABLE update_venv_output
                ERROR_VARIABLE  update_venv_error
            )
            if (NOT update_venv_result EQUAL 0)
                # ensurepip module failed not installed. Check if pip is installed, and cause an error if it's not installed.
                execute_process(
                    COMMAND "${PYTHON_EXECUTABLE}" -m pip --version
                    RESULT_VARIABLE pip_version_result
                )
                if (NOT pip_version_result EQUAL 0)
                    message(FATAL_ERROR "Failed to run ensurepip module, and pip is not installed. Please install pip manually.")
                endif()
            endif()

            execute_process(
                COMMAND "${PYTHON_EXECUTABLE}" -m pip install virtualenv
                RESULT_VARIABLE update_venv_result
                OUTPUT_VARIABLE update_venv_output
                ERROR_VARIABLE  update_venv_error
            )
            if (NOT update_venv_result EQUAL 0)
                message(FATAL_ERROR "Failed to install virtualenv with pip: result: ${update_venv_result}. stderr:\n${update_venv_error}")
            endif()

            execute_process(
                COMMAND "${PYTHON_EXECUTABLE}" -m virtualenv "${venv_path}"
                RESULT_VARIABLE update_venv_result
                OUTPUT_VARIABLE update_venv_output
                ERROR_VARIABLE  update_venv_error
            )
            if (NOT update_venv_result EQUAL 0)
                message(FATAL_ERROR "Cannot update dew venv: result: ${update_venv_result}. stderr:\n${update_venv_error}")
            endif()
        endif()

        #
        # Determine the path of the virtual env python wrapper. It's different on Windows.
        #
        set(venv_python_executable_path "bin/${python_executable_name}")
        if (NOT EXISTS "${venv_python_executable_path}" AND WIN32)
            set(venv_python_executable_path "Scripts/${python_executable_name}")
        endif()

        set(dew_python_executable "${venv_path}/${venv_python_executable_path}")

        #
        # Is dew installed in this virtual env?
        #
        execute_process(
            COMMAND
                "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
                "${dew_python_executable}" -m dew --version
            RESULT_VARIABLE dew_check_result
        )
        if (NOT dew_check_result EQUAL 0)
            #
            # Dew not installed, we still need to install it.
            #
            execute_process(
                COMMAND
                    "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
                    "${dew_python_executable}" -m pip install "${dew_pypi_package_name}"
                RESULT_VARIABLE dew_install_result
                OUTPUT_VARIABLE dew_install_output
                ERROR_VARIABLE  dew_install_error
            )
            if (NOT dew_install_result EQUAL 0)
                message(FATAL_ERROR "Failed to install dew to virtual env, code ${dew_install_result}.\nstderr:\n${dew_install_error}")
            endif()
        endif()
    endif()

    #
    # Wow, dew is definitley installed by this point!
    #
    set(dew_output_path "${CMAKE_CURRENT_BINARY_DIR}/dew")
    set(dew_cmake_prefix_path "${dew_output_path}/prefix")
    set(dew_cmake_module_path "${dew_cmake_prefix_path}/share/cmake/Modules")

    #
    # Add a target to update dew when the dewfile changes.
    #
    add_custom_target(
        "${target_name}"
        COMMAND
            "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
            "${dew_python_executable}" -m dew update
            --dewfile "${dewfile_path}"
            --output-path "${dew_output_path}"
            --cmake-generator "${CMAKE_GENERATOR}"
            --cmake-executable "${CMAKE_COMMAND}"
        DEPENDS
            "${dewfile_path}"
    )

    #
    # Update dew now
    #
    message(STATUS "Updating dependencies with dew")
    execute_process(
        COMMAND
            "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
            "${dew_python_executable}" -m dew update
            --dewfile "${dewfile_path}"
            --output-path "${dew_output_path}"
            --cmake-generator "${CMAKE_GENERATOR}"
            --cmake-executable "${CMAKE_COMMAND}"
        RESULT_VARIABLE dew_update_result
        ERROR_VARIABLE  dew_update_error
    )
    if (NOT dew_update_result EQUAL 0)
        message(FATAL_ERROR "Failed to update dependencies with dew. code: ${dew_update_result}\nstderr:\n${dew_update_error}")
    endif()

    #
    # Set up the prefix path
    #
    set(needs_new_prefix TRUE)
    foreach (path ${CMAKE_PREFIX_PATH})
        if (path STREQUAL "${dew_cmake_prefix_path}")
            set(needs_new_prefix FALSE)
            break()
        endif()
    endforeach()

    set(needs_new_module_path TRUE)
    foreach (path ${CMAKE_MODULE_PATH})
        if (path STREQUAL "${dew_cmake_module_path}")
            set(needs_new_module_path FALSE)
            break()
        endif()
    endforeach()

    if ("${needs_new_prefix}")
        set(CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH} "${dew_cmake_prefix_path}" CACHE PATH "" FORCE)
    endif()

    if ("${needs_new_module_path}")
        set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${dew_cmake_module_path}" CACHE PATH "" FORCE)
    endif()

endfunction()

