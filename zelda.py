from sys import argv
from ntpath import exists, getsize, realpath
from shutil import copy2

ntsc = 1
pal = 2

def read(sram, slot):
	name = ""
	p = format(sram)
	endian = p[0]
	address = p[1][slot - 1]

	if endian != 'big' and endian != 'little':
		print("Invalid format!")
		return

	f = open(sram, 'rb')
	f.seek(address + 0x24)

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

def write(sram, slot, region, name):
	data = []
	padcount = 8 - len(name)
	p = format(sram)
	endian = p[0]
	address = p[1][slot - 1]

	if endian != 'big' and endian != 'little':
		print("Invalid format!")
		return

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

	if padcount > 0:
		for x in range(0, padcount):
			if region == ntsc:
				data.append(0xdf)
			if region == pal:
				data.append(0x3e)

	copy = realpath(sram) + '.bak'
	existing = exists(copy)
	while existing:
		copy += '.bak'
		existing = exists(copy)
	copy2(sram, copy)

	f = open(sram, 'r+b')
	f.seek(address + 0x24)

	if endian == 'little':
		data = data[0:4][::-1] + data[4:8][::-1]

	f.write(bytes(data))
	f.close()

	cksum = checksum(sram, slot)
	data = [(cksum >> 8) & 0xff, cksum & 0xff]

	f = open(sram, 'r+b')

	if endian == 'big':
		f.seek(address + 0x1352)
	if endian == 'little':
		f.seek(address + 0x1350)
		data = data[::-1]

	f.write(bytes(data))
	f.close()

def checksum(sram, slot):
	result = 0
	p = format(sram)
	endian = p[0]
	address = p[1][slot - 1]
	f = open(sram, 'rb')
	f.seek(address)

	x = address
	while x < address + 0x1350:
		val = int.from_bytes(f.read(2), endian)
		result += val
		if result > 0xffff:
			result & 0xffff
		x += 0x2

	if endian == 'big':
		f.seek(address + 0x1350)
	if endian == 'little':
		f.seek(address + 0x1352)

	result += int.from_bytes(f.read(2), endian)
	f.close()
	return result & 0xffff

def format(sram):
	f = open(sram, 'rb')
	fsize = getsize(sram)
	endian = ''
	result = []

	if fsize == 32768:
		f.seek(0x8)
		flag = int.from_bytes(f.read(2), 'big')
		if flag == 0x4144:
			endian = 'little'
		if flag == 0x454c:
			endian = 'big'
		slots = [0x20, 0x1470, 0x28c0]
	elif fsize == 296960:
		endian = 'little'
		slots = [0x20820, 0x21c70, 0x230c0]
	else:
		print('Invalid format, file size incorrect!')
		return
	result = [endian, slots]
	f.close()
	return result

def menu(sram):
	print("----------------------------------------------------------------")
	print("The Legend of Zelda: Ocarina of Time | Save Name Editor")
	print("----------------------------------------------------------------")

	for x in range(1, 4):
		print("File " + str(x) + ": " + read(sram, x))

	key = input('Enter 1, 2 or 3 to change a file name, or any other key to quit: ')

	if key == '1' or key == '2' or key == '3':
		x = int(key, 10)

		b = True
		while b:
			key = input('Are you sure? y/n: ')
			if key == 'n':
				return
			elif key == 'y':
				name = ""
				while len(name) == 0 or len(name) > 8:
					name = input('Please enter a new name: ')
					if name == "" or len(name) > 8:
						print('Name must be between 1 and 8 characters.')
				c = True
				while c:
					key = input('Please enter 1 for NTSC or 2 for PAL: ')
					if key == '1':
						region = 1
						c = False
					elif key == '2':
						region = 2
						c = False
					else:
						print('Enter a valid entry.')
				b = False
			else:
				print('You must enter y or n.')



		write(sram, x, region, name)
		print('\nName successfully written!\n')
		menu(sram)

menu(argv[1])