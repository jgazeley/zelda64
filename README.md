# Zelda 64 Save Game Name Editor

A command-line tool to easily view and edit player file names in **The Legend of Zelda: Ocarina of Time** and **Majora's Mask** N64 save files.


## Key Features

* **Broad Compatibility:** Works with both *Ocarina of Time* and *Majora's Mask*.
* **Multi-Format Support:** Edits all common emulator and hardware save formats without needing conversion:
    * `.sra` / `.fla` (Project 64, Mupen64Plus)
    * `.ram` / `.flash` (Ares)
    * `.srm` (RetroArch)
* **Region Support:** Handles both `NTSC` and `PAL` versions of the games.
* **Intelligent & Safe:** Automatically detects endianness and creates a backup of your save file before making any changes.
* **Simple & Fast:** A lightweight, command-line tool with no external dependencies.


## Requirements

* **Python 3.x:** Download from [python.org](https://www.python.org/downloads/).


## Installation

No installation is needed. Simply download the `zelda64.py` script from the root of this repository.


## Usage Example

Run the script from your terminal or command prompt, providing the path to your save file as an argument. The script will then guide you through the process of viewing and changing the names.

```powershell
PS D:\Games\N64\Saves> python zelda64.py "THE LEGEND OF ZELDA.sra"

----------------------------------------------------------------
Zelda 64: Save Name Editor | Ocarina of Time
----------------------------------------------------------------
File 1: JAYSON
File 2:
File 3:
Enter a save slot number to change the file name, or any other key to quit: 1
Are you sure? y/n: y
Please enter a new name: Link
Please enter 1 for NTSC (US/JAPAN) or 2 for PAL (EUROPE): 1

Backup created at: THE LEGEND OF ZELDA.sra.bak
Name successfully written!

----------------------------------------------------------------
Zelda 64: Save Name Editor | Ocarina of Time
----------------------------------------------------------------
File 1: Link
File 2:
File 3:
Enter a save slot number to change the file name, or any other key to quit: x
PS D:\Games\N64\Saves>
```


## How It Works

N64 save files store player names at specific, fixed memory offsets. This script reads the file, displays the names found at these offsets, and then carefully overwrites the bytes at the correct location with your new name.

It intelligently handles different file formats and regional versions by detecting the file's endianness and calculating the correct checksum after the name is changed, ensuring the modified save file remains valid.


## Utilities

For advanced users, this repository also contains a general-purpose byteswapping utility. Please see the `README.md` file in the `/utils/` directory for more information.