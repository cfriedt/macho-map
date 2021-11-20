if (${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Darwin" AND CONFIG_ARCH_POSIX)
zephyr_interface_library_named(MACHO_MAP)

zephyr_include_directories(include)
endif()
