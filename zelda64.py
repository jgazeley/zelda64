from sys import argv
from ntpath import exists, getsize, realpath
from shutil import copy2

REG = ['ntsc', 'pal']

class Save:
	def __init__(self, file, name, endian, game, address, valid, slot, bound):
		self.file = file # file path to .sra/.fla/.ram/.srm file
		self.name = name # player name stored in a list as ASCII characters
		self.endian = endian # big or little endian (checksum must be calculated in big endian)
		self.address = address # contains address of save file offset, player name, and checksum
		self.game = game # Ocarina of Time or Majora's Mask
		self.valid = valid # determines if there is a valid save in each file position
		self.slot = slot # player file position from the in-game file select menu
		self.bound = bound # number of slots (ocarina: 3 / majora: 2)

	def __str__(self):
		result = "Slot: " + str(self.slot)
		result += "\nName: " + str(self.name)
		# result += "\nChecksum: " + (self.checksum)
		
		return result

	#################################################################################
	# Converts player name between ASCII and the games encoding (NTSC/PAL specific)
	# data: list of byte values from game save file or a string <= 8 characters
	# enc: options are 'ascii', 'ntsc', and 'pal'
	# Returns: an array representing player name in hex values or as a string converted to ASCII
	def convert_name(self, data, enc):
		if enc == 'ascii':
			result = ""
			for x in range(0, 8):
				if data[x] >= 0x0 and data[x] <= 0x9: # (0-9)
					result += str(data[x])
				elif data[x] == 0xdf or data[x] == 0x3e: # (space " ")
					result += " "
				else:
					if data[x] >= 0xa and data[x] <= 0x3d: # PAL (A-z)
						if data[x] <= 0x23:
							data[x] += 0x37
						elif data[x] >= 0x24:
							data[x] += 0x3d
					elif data[x] >= 0xab and data[x] <= 0xde: # NTSC (A-z)
						if data[x] <= 0xc4:
							data[x] -= 0x6a
						elif data[x] >= 0xc5:
							data[x] -= 0x64
					elif data[x] == 0xea or data[x] == 0x40: # (period ".")
						data[x] = 0x2e
					elif data[x] == 0xe4 or data[x] == 0x3f: # (dash "-")
						data[x] = 0x2d
					result += chr(data[x])
			return result

		if enc == 'ntsc' or enc == 'pal':
			result = []
			for x in range(0, len(data)):
				val = ord(data[x])
				if val >= 0x41 and val <= 0x5a: # (A-Z)
					if enc == 'ntsc':
						val += 0x6a
					elif enc == 'pal':
						val -= 0x37
				elif val >= 0x61 and val <= 0x7a: # (a-z)
					if enc == 'ntsc':
						val += 0x64
					elif enc == 'pal':
						val -= 0x3d
				elif val >= 0x30 and val <= 0x39: # (0-9)
					val -= 0x30
				elif val == 0x2e: # (period ".")
					if enc == 'ntsc':
						val = 0xea
					elif enc == 'pal':
						val = 0x40
				elif val == 0x2d: # (dash "-")
					if enc == 'ntsc':
						val = 0xe4
					elif enc == 'pal':
						val = 0x3f
				elif val == 0x20: # (space " ")
					if enc == 'ntsc':
						val = 0xdf
					elif enc == 'pal':
						val = 0x3e
				result.append(val)

			# Pads name with values (0xDF/0x3E) if less than 8 characters.
			padcount = 8 - len(data)
			if padcount > 0:
				for x in range(0, padcount):
					if enc == 'ntsc':
						result.append(0xdf)
					elif enc == 'pal':
						result.append(0x3e)
			return result

	#################################################################################
	# Writes a new name to the desired file position. 
	# name: new player name to write to save file
	# enc: user must determine whether their game is NTSC or PAL for the appropriate conversion
	def write_name(self, name, enc):

		# Converts characters from ASCII to proprietary game character set.
		data = self.convert_name(name, enc)
		self.name = data

		# Creates backup copy of input file before writing data.
		copy = realpath(self.file) + '.bak'
		existing = exists(copy)
		while existing:
			copy += '.bak'
			existing = exists(copy)
		copy2(self.file, copy)

		f = open(self.file, 'r+b')
		f.seek(self.address[1])
		
		# Rearranges letters for writing if file is in little endian.
		if self.endian == 'little':
			data = data[0:4][::-1] + data[4:8][::-1]

		f.write(bytes(data))
		f.close()

		# Gets new checksum and splits 16-bit result into two bytes.
		cksum = self.checksum()
		data = [(cksum >> 8) & 0xff, cksum & 0xff]

		f = open(self.file, 'r+b')

		# Reverses the 2 bytes for the checksum (if not big endian) and chooses the address
		# of the final 2 bytes based on endianness due to asymmetry.
		# Done so algorithm works with all file types without byteswapping.
		if self.endian == 'big':
			f.seek(self.address[2] + 2)
		if self.endian == 'little':
			f.seek(self.address[2])
			data = data[::-1]

		f.write(bytes(data))
		f.close()

	#################################################################################
	# Checks if the name contains valid characters and is the correct length. (1-8 characters)
	# name: list of byte values representing character name (ASCII)
	# Returns: true if name is acceptable for conversion (A-Z, a-z, 0-9, '.', '-', ' ')
	def valid_name(self, name):
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
				print('Name cannot contain special characters.')
				return False
		if len(name) > 8:
			print('Name cannot be more than 8 characters.')
			return False
		if len(name) == 0:
			print('Name cannot be empty.')
			return False
		if name[0] == " ":
			print('Name cannot begin with a space.')
			return False
		return True

	#################################################################################
	# Adds up 16-bit words from save file offset position to checksum position. (Ocarina of Time only; see below)
	# Returns: 16-bit checksum in big endian (N64 native)
	def checksum(self):
		f = open(self.file, 'rb')
		x = self.address[0]
		f.seek(x)

		# Majora's Mask uses a slightly different algorithm, adding each individual byte with a 16-bit result.
		i = 2; result = 0; end = self.endian
		if self.game == "Majora's Mask":
			i = 1; end = 'big'

		while x < self.address[2]:
			val = int.from_bytes(f.read(i), end)
			result += val
			if result > 0xffff:
				result &= 0xffff
			x += i

		# Chooses the address of the final 2 bytes based on endianness due to asymmetry.
		# Done so algorithm works with all file types without byteswapping.
		if self.endian == 'big':
			f.seek(self.address[2])
		if self.endian == 'little':
			f.seek(self.address[2] +2)
			# print(hex(self.address[2] +2))

		if self.game == "Ocarina of Time":
			result += int.from_bytes(f.read(2), self.endian)
		if self.game == "Majora's Mask":
			result += int.from_bytes(f.read(1), 'big') + int.from_bytes(f.read(1), 'big')

		f.close()
		return result & 0xffff

#################################################################################
# Valid file sizes are: 32 KB (Ocarina) / 64 KB to 128 KB (Majora) / 290 KB (Retroarch)
# Creates save objects for each file position and assigns the appropriate address for the name and checksum data.
# file: the input file containing game saves (.sra/.fla/.ram/.srm)
# Returns: 2 or 3 Save objects as an array
def initiate(file):

	if getsize(file) < 0x8000:
		print('File size too small.')
		exit()

	# Reads 32 KB from file; adjusts starting address if Retroarch save. (.srm)
	buffer = 0x8000
	if getsize(file) == 0x48800:
		retroarch = True
	else:
		retroarch = False

	data = 0
	with open(file, 'rb') as f:
		if retroarch:
			f.seek(0x20800)
		data = f.read(buffer)
		f.close()
		del(f)

	# Each save is checked for the special flag 'ZELDAZ' ('ZELDA3' for Majora's Mask) to determine game and endianness.
	game = ""; endian = None
	if valid_save(data):
		if b'\x41\x5a' in data or b'\x5a\x41' in data:
			game = "Ocarina of Time"
		elif b'\x41\x33' in data or b'\x33\x41' in data:
			game = "Majora's Mask"
	else:
		print('No valid saves found!')
		exit()
	if b'\x5a\x45\x4c\x44' in data:
		endian = 'big'
	elif b'\x44\x4c\x45\x5a' in data:
		endian = 'little'

	offset = 0x20
	n = 0x24 # player name
	chk = 0x1350; # checksum (minus 2 bytes)
	size = 0x1450; # save slot sector length
	bound = 3; # number of save slots
	if game == "Majora's Mask":
		offset = 0x0; n = 0x2c; chk = 0x1008; size = 0x4000; bound = 2;
		# Adjusts offset for Majora's Mask Retroarch files.
		if retroarch:
			offset += 0x8000

	# Creates new save objects. (2 or 3; for Majora's Mask or Ocarina of Time respectively)
	i = 0; saves = []
	for i in range(i, bound):
		name = list(data[offset + n : offset + (n+8)])
		address = (offset, offset + n, offset + chk)
		valid = valid_save(data[offset : offset + 0x50])
		slot = i + 1
		offset += size
		i += 1
		if endian == 'little':
			name = name[0:4][::-1] + name[4:8][::-1]
		save = Save(file, name, endian, game, address, valid, slot, bound)
		saves.append(save)

	return saves

def valid_save(data):
	if b'\x5a\x45\x4c\x44' in data or b'\x44\x4c\x45\x5a' in data:
		return True

#################################################################################
# Main menu
# Run from command line/Powershell: $ python3 zelda64.py 'THE LEGEND OF ZELDA.sra'
def menu():

	# file = input('Enter the save file path. Valid formats include .sra, .ram, .fla, and .srm.\nSave location: ')
	# saves = initiate(file)
	# game = saves[0].game

	while True:
		print("----------------------------------------------------------------")
		print("Zelda 64: Save Name Editor | " + saves[0].game)
		print("----------------------------------------------------------------")

		# Displays save files
		x = 0
		for x in range(0, saves[x].bound):
			if saves[x].valid:
				txt = saves[x].convert_name(saves[x].name, 'ascii')
			else:
				txt = ''
			print("File " + str(x + 1) + ": " + txt)
			# print(hex(saves[x].address[0]&0xffff) + "  " + hex(saves[x].address[2]&0xffff))

		# Prompts user to pick a save slot
		a = True
		while a:
			key = input('Enter a save slot number to change the file name, or any other key to quit: ')
			if key == '1' or key == '2' or key == '3':
				x = int(key, 10) - 1
				f = 0
				if game == "Majora's Mask":
					if x == 2:
						exit()
					else:
						f += 1
				if not saves[x].valid:
					print('Save appears empty or corrupt. Cannot write to this slot.')
				else:
					a = False
			else:
				exit()

		# Confirms user's intent to change player name
		b = True
		while b:
			key = input('Are you sure? y/n: ')
			if key == 'n':
				menu()
				exit()
			elif key == 'y':
				b = False
			else:
				print('You must enter y or n.')
		c = True
		while c:
			name = input('Please enter a new name: ')
			if saves[x].valid_name(name):
				c = False

		# Determines NTSC / PAL for re-encoding
		if game == 'Ocarina of Time':
			d = True
			while d:
				key = input('Please enter 1 for NTSC (US/JAPAN) or 2 for PAL (EUROPE): ')
				if key != '1' and key != '2':
					print('Enter a valid entry.')
				else:
					region = REG[int(key, 10) - 1]
					d = False
		else:
			region = 'pal'

		saves[x].write_name(name, region)
		print('\nName successfully written!\n')

if len(argv) < 2:
	print("Must enter a .sra file.")

elif len(argv) == 2:

	if argv[1] == '--help' or argv[1] == '-help' or argv[1] == '-h' or argv[1] == '-H':
		print("Usage: py zelda64.py <PATH-TO-SRA-FILE>")
		print("Example: py 'D:\\Desktop\\zelda64.py' 'D:\\Desktop\\THE LEGEND OF ZELDA.sra'")
		exit()

	if exists(argv[1]):
		saves = initiate(argv[1])
		game = saves[0].game
		menu()
	else:
		print("File '" + argv[1] + "' does not exist.")

else:
	print("Only a single file can be modified at a time.")