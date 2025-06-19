# Supplemental Utilities

This directory contains optional command-line utilities for advanced users or developers working with N64 save files.

**These scripts are NOT required to use the main `zelda64.py` save editor.**

## `byteswap.py`

* **Purpose:** A general-purpose utility to perform a 32-bit byteswap on a file. This permanently converts a file's endianness (from big-endian to little-endian, or vice versa).
* **Use Case:** This tool is useful for developers or users who need to permanently convert a save file for use with a specific emulator or tool that does not handle endianness automatically.
* **Usage:**
    ```bash
    python byteswap.py <path_to_file>
    ```
* **Safety:** The script will create a `.bak` backup of the original file before making any permanent changes.