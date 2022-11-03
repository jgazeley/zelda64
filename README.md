# zelda64

Save Game Name Editor for **Zelda: Ocarina of Time** & **Majora's Mask** (N64 Version/Project 64/M64plus/Mupen64/RetroArch/Ares)<br>
_Written by Jayson Gazeley in Python_

A tool to change the player file names in Zelda 64 emulator save files or native saves dumped from a Gameshark or other device. Works with common formats: ( .sra / .fla / .ram / .srm )

Project 64, M64/Mupen64, and 1964 use (.sra/.fla) save files, Ares uses (.ram/.flash) files, and Retroarch uses (.srm) files. This program was tested and works with all of these formats.

Works with both (NTSC/PAL) versions of the game; you must specify when writing a new name which version (NTSC/PAL) you have.

Requires Python 3 - https://www.python.org/downloads/.


Examples from command line:

python 'zelda64.py' 'THE LEGEND OF ZELDA.sra'

py 'C:\Users\Desktop\zelda64.py' 'C:\Users\Games\Retroarch\N64\Saves\Legend of Zelda, The - Ocarina of Time.srm'
