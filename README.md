# zelda
Save Game Name Editor for Zelda: Ocarina of Time (N64 Version/Project 64/Mupen64/RetroArch/Ares) written in Python

An easy tool to change the file names in The Legend of Zelda | Ocarina of Time save files. Works with 3 common formats: .sra, .ram, and .srm.

Project 64, M64/Mupen64, and 1964 use .sra save files, Ares uses .ram files, and Retroarch uses .srm files. This program was tested and works with all 3 formats.

Works with both (NTSC/PAL) versions of the game, but you must specify when writing a new name which version (NTSC/PAL) you have.


Examples from command line: 

python3 'zelda.py' 'THE LEGEND OF ZELDA.sra'

py 'C:\Users\Downloads\zelda.py' 'C:\Users\Games\Retroarch\N64\Saves\Legend of Zelda, The - Ocarina of Time.srm'
