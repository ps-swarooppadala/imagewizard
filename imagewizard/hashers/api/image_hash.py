from __future__ import (absolute_import, division, print_function)

from PIL import Image
import numpy
import os.path
with open(os.path.join(os.path.abspath(
	os.path.dirname(__file__)), 'VERSION')) as fi:
	__version__ = fi.read().strip()


def _binary_array_to_hex(arr):
	"""
	internal function to make a hex string out of a binary array.
	"""
	bit_string = ''.join(str(b) for b in 1 * arr.flatten())
	width = int(numpy.ceil(len(bit_string)/4))
	return '{:0>{width}x}'.format(int(bit_string, 2), width=width)


class ImageHash(object):
	"""
	Hash encapsulation. Can be used for dictionary keys and comparisons.
	"""
	def __init__(self, binary_array):
		self.hash = binary_array

	def __str__(self):
		return _binary_array_to_hex(self.hash.flatten())

	def __repr__(self):
		return repr(self.hash)

	def __sub__(self, other):
		if other is None:
			raise TypeError('Other hash must not be None.')
		if self.hash.size != other.hash.size:
			raise TypeError('ImageHashes must be of the same shape.', self.hash.shape, other.hash.shape)
		return numpy.count_nonzero(self.hash.flatten() != other.hash.flatten())

	def __eq__(self, other):
		if other is None:
			return False
		return numpy.array_equal(self.hash.flatten(), other.hash.flatten())

	def __ne__(self, other):
		if other is None:
			return False
		return not numpy.array_equal(self.hash.flatten(), other.hash.flatten())

	def __hash__(self):
		# this returns a 8 bit integer, intentionally shortening the information
		return sum([2**(i % 8) for i, v in enumerate(self.hash.flatten()) if v])


def hex_to_hash(hexstr):
	"""
	Convert a stored hash (hex, as retrieved from str(Imagehash))
	back to a Imagehash object.
	Notes:
	1. This algorithm assumes all hashes are bidimensional arrays
	   with dimensions hash_size * hash_size.
	2. This algorithm does not work for hash_size < 2.
	"""
	hash_size = int(numpy.sqrt(len(hexstr)*4))
	binary_array = '{:0>{width}b}'.format(int(hexstr, 16), width = hash_size * hash_size)
	bit_rows = [binary_array[i:i+hash_size] for i in range(0, len(binary_array), hash_size)]
	hash_array = numpy.array([[bool(int(d)) for d in row] for row in bit_rows])
	return ImageHash(hash_array)

def old_hex_to_hash(hexstr, hash_size=8):
	"""
	Convert a stored hash (hex, as retrieved from str(Imagehash))
	back to a Imagehash object. This method should be used for
	hashes generated by ImageHash up to version 3.7. For hashes
	generated by newer versions of ImageHash, hex_to_hash should
	be used instead.
	"""
	l = []
	count = hash_size * (hash_size // 4)
	if len(hexstr) != count:
		emsg = 'Expected hex string size of {}.'
		raise ValueError(emsg.format(count))
	for i in range(count // 2):
		h = hexstr[i*2:i*2+2]
		v = int("0x" + h, 16)
		l.append([v & 2**i > 0 for i in range(8)])
	return ImageHash(numpy.array(l))