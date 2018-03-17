#!/usr/bin/python

import argparse
import os.path
import re


def main(path, output_name):
	print('Opening input text file...')
	f = open(path).readlines()
	print('Text file open!')

	output_dir = os.path.abspath(os.path.join(path, os.pardir))
	output_file = output_dir + "/" + output_name

	print('Creating output file at this directory: {}'.format(output_file))
	o = open(output_file, 'w+')
	print('Output file created! Now going to populate...')

	lines = {}

	for index, line in enumerate(f):
		letter_regex = re.findall(r" \w{1,2}$", line)
		if letter_regex:
			letter_regex[0] = letter_regex[0].strip()
			lines[index] = ('letter', letter_regex[-1])
			continue

		force_regex = re.findall(r"force\s+[-0123456789.]+", line)
		if force_regex:
			lines[index] = ('force', force_regex[0].split()[1])
			continue

	# for entry in lines.itervalues():   # depreciated for Python3
	for entry in iter(lines.values()):
		if entry[0] == 'letter':
			if 'N' in entry[1]:
				o.write('\n')
			o.write('\n')
			o.write('{},'.format(entry[1]))
			continue
		if entry[0] == 'force':
			o.write('{},'.format(entry[1]))

	o.write('\n')
	o.write('\n')
	o.close()

	print('All done!')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('path', type=str,
						help='Path to the input file. Must be the complete file path!')
	parser.add_argument('output_name', type=str,
						help='Name for the output file.')
	args = parser.parse_args()

	main(args.path, args.output_name)
