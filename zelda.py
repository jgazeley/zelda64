from sys import argv
from ntpath import exists, getsize, realpath
from shutil import copy2

ntsc = 1
pal = 2

#################################################################################
# Reads existing name in a given file position.
# Parameters: .sra/.ram/.srm filepath and save position (1-3)
def read(sram, slot):
	endian = format(sram)[0]
	address = format(sram)[1][slot - 1]
	f = open(sram, 'rb')
	f.seek(address + 0x24)

	name = ""
	for x in range(0, 8):
		val = int.from_bytes(f.read(1), 'big')

		if val >= 0x0 and val <= 0x9: # (0-9)
			name += str(val)

		elif val == 0xdf or val == 0x3e: # (space " ")
			name += " "

		else:
			if val >= 0xa and val <= 0x3d: # PAL (A-z)
				if val <= 0x23:
					val += 0x37
				elif val >= 0x24:
					val += 0x3d

			elif val >= 0xab and val <= 0xde: # NTSC (A-z)
				if val <= 0xc4:
					val -= 0x6a
				elif val >= 0xc5:
					val -= 0x64

			elif val == 0xea or val == 0x40: # (period ".")
				val = 0x2e

			elif val == 0xe4 or val == 0x3f: # (dash "-")
				val = 0x2d

			name += chr(val)

	f.close()

	if endian == 'little':
		name = name[0:4][::-1] + name[4:8][::-1]

	return name

#################################################################################
# Writes a new name to the desired file position. 
# Parameters: .sra/.ram/.srm <filepath>, save position (1-3), region (ntsc/pal), and new name (string)
def write(sram, slot, region, name):
	endian = format(sram)[0]
	address = format(sram)[1][slot - 1]
	padcount = 8 - len(name)
	data = []

	# Converts characters to Unicode for display in menu
	for x in range(0, len(name)):
		val = ord(name[x])

		if val >= 0x41 and val <= 0x5a: # (A-Z)
			if region == ntsc:
				val += 0x6a
			if region == pal:
				val -= 0x37

		elif val >= 0x61 and val <= 0x7a: # (a-z)
			if region == ntsc:
				val += 0x64
			if region == pal:
				val -= 0x3d

		elif val >= 0x30 and val <= 0x39: # (0-9)
			val -= 0x30

		elif val == 0x2e: # (period ".")
			if region == ntsc:
				val = 0xea
			if region == pal:
				val = 0x40

		elif val == 0x2d: # (dash "-")
			if region == ntsc:
				val = 0xe4
			if region == pal:
				val = 0x3f

		elif val == 0x20: # (space " ")
			if region == ntsc:
				val = 0xdf
			if region == pal:
				val = 0x3e

		data.append(val)

	# Pads name with values 0xDF/0x3E (NTSC/PAL) if less than 8 characters
	if padcount > 0:
		for x in range(0, padcount):
			if region == ntsc:
				data.append(0xdf)
			if region == pal:
				data.append(0x3e)

	# Creates backup copy of input file before writing data
	copy = realpath(sram) + '.bak'
	existing = exists(copy)
	while existing:
		copy += '.bak'
		existing = exists(copy)
	copy2(sram, copy)

	f = open(sram, 'r+b')
	f.seek(address + 0x24)

	# Rearranges letters for display if file is in little endian
	if endian == 'little':
		data = data[0:4][::-1] + data[4:8][::-1]

	f.write(bytes(data))
	f.close()

	# Gets new checksum and splits 16-bit result into two bytes
	cksum = checksum(sram, slot)
	data = [(cksum >> 8) & 0xff, cksum & 0xff]

	f = open(sram, 'r+b')

	# Reverses the 2 bytes for the checksum (if not big endian) and chooses the address 
	# of the final 2 bytes based on endianness due to asymmetry.
	# Done so algorithm works with all file types without byteswapping
	if endian == 'big':
		f.seek(address + 0x1352)
	if endian == 'little':
		f.seek(address + 0x1350)
		data = data[::-1]

	f.write(bytes(data))
	f.close()

#################################################################################
# Adds up 16-bit words from save file offset position to checksum position (length 0x1352)
# Returns 16-bit checksum in big endian (N64 native)
# Parameters: .sra/.ram/.srm <filepath> and save position (1-3)
def checksum(sram, slot):
	endian = format(sram)[0]
	address = format(sram)[1][slot - 1]
	f = open(sram, 'rb')
	f.seek(address)
	result = 0

	x = address
	while x < address + 0x1350:
		val = int.from_bytes(f.read(2), endian)
		result += val
		if result > 0xffff:
			result & 0xffff
		x += 0x2

	# Chooses the address of the final 2 bytes based on endianness due to asymmetry
	# Done so algorithm works with all file types without byteswapping
	if endian == 'big':
		f.seek(address + 0x1350)
	if endian == 'little':
		f.seek(address + 0x1352)

	result += int.from_bytes(f.read(2), endian)
	f.close()
	return result & 0xffff

#################################################################################
# Checks the endianness and file size to verify input file is a valid format
# Parameters: .sra/.ram/.srm <filepath>
def format(sram):
	f = open(sram, 'rb')
	fsize = getsize(sram)

	# 32 KB saves (.sra, .ram) / Project 64, Mupen64, 1964
	if fsize == 32768:
		f.seek(0x8)
		flag = int.from_bytes(f.read(2), 'big')
		if flag == 0x4144:
			endian = 'little'
		if flag == 0x454c:
			endian = 'big'
		else:
			print('Invalid format!')
			exit()
		offsets = [0x20, 0x1470, 0x28c0]

	# 290 KB saves (.srm) / Retroarch
	elif fsize == 296960:
		f.seek(0x20808)
		flag = int.from_bytes(f.read(2), 'big')
		if flag != 0x4144:
			print('Invalid format!')
			exit()
		else:
			endian = 'little'
			offsets = [0x20820, 0x21c70, 0x230c0]

	else:
		print('Invalid format, file size incorrect!')
		exit()

	f.close()	
	result = [endian, offsets]
	return result

#################################################################################
# Checks if the name contains valid characters and is a valid length (1-8 characters)
# Parameters: User entered name (string)
def valid_name(name):
	chars = [0x20, 0x2d, 0x2e]
	i = 0x30
	for i in range(i, 0x3a):
		chars.append(i)
	i = 0x41
	for i in range(i, 0x5b):
		chars.append(i)
	i = 0x61
	for i in range(i, 0x7b):
		chars.append(i)
	i = 0
	for i in range(i, len(name)):
		ch = ord(name[i])
		if ch in chars:
			pass
		else:
			print('Name contains invalid characters.')
			return False
	if len(name) > 8:
		print('Name must be between 1 and 8 characters.')
		return False
	if len(name) == 0:
		print('Name cannot be empty.')
		return False
	if name[0] == " ":
		print('Name cannot begin with a space.')
		return False
	return True

#################################################################################
# Main menu
# Parameter: .sra/.ram/.srm <filepath> (argument comes from command line/Powershell; see readme or comment below)
def menu(sram):
	print("----------------------------------------------------------------")
	print("The Legend of Zelda: Ocarina of Time | Save Name Editor")
	print("----------------------------------------------------------------")

	for x in range(1, 4):
		print("File " + str(x) + ": " + read(sram, x))

	key = input('Enter 1, 2 or 3 to change a file name, or any other key to quit: ')

	if key == '1' or key == '2' or key == '3':
		x = int(key, 10)

		a = True
		while a:
			key = input('Are you sure? y/n: ')
			if key == 'n':
				menu(sram)
				exit()
			elif key == 'y':
				a = False
			else:
				print('You must enter y or n.')
		b = True
		while b:
			name = input('Please enter a new name: ')
			if valid_name(name):
				b = False
		c = True
		while c:
			key = input('Please enter 1 for NTSC or 2 for PAL: ')
			if key != '1' and key != '2':
				print('Enter a valid entry.')
			else:
				region = int(key, 10)
				c = False

		write(sram, x, region, name)
		print('\nName successfully written!\n')
		menu(sram)

# Run from command line/Powershell using ~$ python3 zelda.py <filepath>
# Example: $ python3 'zelda.py' 'D:/Desktop/THE LEGEND OF ZELDA.sra'
menu(argv[1])
