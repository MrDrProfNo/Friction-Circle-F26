#!/usr/bin/python

import argparse
import os.path
import re
from decimal import Decimal
from pandas import ExcelWriter, DataFrame, Series

def parse(path, output_name):
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



def readParseToExcel(fromFileFront, fromFileRear, toFile, df_full):
	"""
	Takes
	:return:
	"""

	headers = generatePartialHeaders(df_full.shape[0])

	try:
		f = open(fromFileFront)
	except:
		print("Error in opening file:", fromFileFront,
			  "\n Could not find file.")
		raise


	line = f.readline()
	# Skip leading newlines in input file
	while (line == "\n"):
		line = f.readline()

	leftMargin = 3  # left margin of tables
	topMargin = 3  # top margin for tables (must be at least 1)
	displacement = 0  # number of tables from left; 0 indexed
	xspacing = 3  # horizontal space between each table
	yspacing = 3  # vertical space between each table
	tablewidth = 5  # width of each table
	tableheight = 13  # height of each table
	count = 0  # number of tables read so far

	writer = ExcelWriter(toFile, engine='xlsxwriter')
	dataDict = {}

	while (True):
		if (line == "\n"):
			if (displacement == 1 or displacement == 0):
				columnArray = [
					"Values",
					"Lower Outboard @ Upright",
					"Upper Outboard @ Upright",
					"Steering @ Upright",
					"Front Lower Front @ Chassis",
					"Front Lower Rear @ Chassis",
					"Push Rod @ Bellcrank",
					"Front Upper Front @ Chassis",
					"Front Upper Rear @ Chassis",
					"Bell Crank Pivot @ Post",
					"Bell Crank Pivot @ Post",
					"Shock @ Chassis"
				]
			else:
				columnArray = [
					"Values",
					"Lower Outboard @ Upright",
					"Upper Outboard @ Upright",
					"Toe Link @ Upright",
					"Rear Lower Front @ Chassis",
					"Rear Lower Rear @ Chassis",
					"Push Rod @ Bellcrank",
					"Rear Upper Front @ Chassis",
					"Rear Upper Rear @ Chassis",
					"Forward Bell Crank Pivot @ Post",
					"Bell Crank Pivot @ Post",
					"Shock @ Chassis"
				]

			df = DataFrame(dataDict, columns=columnArray,
						   index=["X", "Y", "Z", "Totals"])
			df = df.transpose()

			# Title text: The text written above each table
			titleText = ""
			# Alternate column displacement between left and right wheels
			# 0 and 1 cases are for front wheels; 2 and 3 are for rear
			caseIDX = (count // 2)
			caseData = df_full.iloc[caseIDX]

			addPositionColumn(caseIDX + 1, df)	# normal people don't 0 index

			# case = Decimal(case)
			# case = round(case, 1)
			if (displacement == 0):  # right front wheel
				displacement = 1
				titleText += "Right Front "
				df.loc["Values", "X":"Z"] = -caseData["RF_Fx"], \
											-caseData["RF_Fy"], \
											caseData["RF_Fz"]
			elif (displacement == 1):  # left front wheel
				displacement = 0
				titleText += "Left Front "
				df.loc["Values", "X":"Z"] = -caseData["LF_Fx"], \
											-caseData["LF_Fy"], \
											caseData["LF_Fz"]
			elif (displacement == 2):  # right rear wheel
				displacement = 3
				titleText += "Right Rear "
				df.loc["Values", "X":"Z"] = -caseData["RR_Fx"], \
											-caseData["RR_Fy"], \
											caseData["RR_Fz"]
			elif (displacement == 3):  # left rear wheel
				displacement = 2
				titleText += "Left Rear "
				df.loc["Values", "X":"Z"] = -caseData["LR_Fx"], \
											-caseData["LR_Fy"], \
											caseData["LR_Fz"]

			df.to_excel(writer, sheet_name="Sheet 1",
						startcol=leftMargin + (
						displacement * (tablewidth + xspacing)),
						startrow=topMargin + (
						(caseIDX) * (yspacing + tableheight))
						)

			# occasionally spits a message into console, but never crashes
			# message roughly "non-integers will soon cease to be supported"
			case_theta_coef = df_full.index[caseIDX]

			headerText = headers[caseIDX]

			titleText += headerText
			titleText += case_theta_coef.to_eng_string()


			ws = writer.sheets["Sheet 1"]
			ws.write(
				topMargin + ((count // 2) * (yspacing + tableheight)) - 1,
				leftMargin + (displacement * (tablewidth + xspacing)) + 1,
				titleText
			)

			count += 1
			line = f.readline()
			dataDict = {}
			continue

		if (line == ""):
			if (f.name == fromFileFront):  # End of front wheel file
				f.close()
				try:
					f = open(fromFileRear)
				except:
					print("Error in opening file:", fromFileRear,
						  "\nFile may not exist")
					raise

				count = 0
				displacement = 3
				line = f.readline()
				# Skip leading newlines
				while (line == "\n"):
					line = f.readline()
			else:  # already on rear file
				f.close()
				break

		line = line.split(",")
		if (line[0] == "N" or line[0] == "V" or
					replaceMitchellVariables(line[0]) in dataDict):
			line = f.readline()
			continue

		if (displacement <= 1):
			line[0] = replaceMitchellVariables(line[0], False)
		else:
			line[0] = replaceMitchellVariables(line[0], True)

		# X and Y values are negated to convert back from Mitchell's coordinate
		# system.
		line[1] = -Decimal(line[1])
		line[2] = -Decimal(line[2])
		line[3] = Decimal(line[3])
		dataDict[line[0]] = [line[1], line[2], line[3],
							 "=SQRT(INDIRECT(\"C[-1]\","
							 " FALSE)^2 +INDIRECT(\"C[-2]\", FALSE)^2 + "
							 "INDIRECT(\"C[-3]\", FALSE)^2)"
							 ]
		line = f.readline()
	writer.save()
	writer.close()


def replaceMitchellVariables(var, rear=False):
	"""
	Helper function for readParseToExcel()
	Takes in a variable from Mitchell and replaces it with the associated word.
	These associations were all grabbed from the original excel file with the
	final calculated forces in it (which readParseToExcel is producing a copy
	of).
	Some associations vary depending on whether the data is for the front or the
	rear axle; if the passed boolean is True, the rear-axle associations are
	used.
	A list of valid mitchell variables follows:
	B
	E
	S
	A
	C
	MW
	D
	F
	P
	Q
	W

	:param var: string from the above list of valid mitchell variables
	:param rear: boolean; true to use rear-axle phrase associations
	:return: The string to replace the passed variable with
	"""
	if (var == "B"):
		return "Lower Outboard @ Upright"
	elif (var == "E"):
		return "Upper Outboard @ Upright"
	elif (var == "S"):
		if (rear):
			return "Toe Link @ Upright"
		return "Steering @ Upright"
	elif (var == "A"):
		if (rear):
			return "Rear Lower Front @ Chassis"
		return "Front Lower Front @ Chassis"
	elif (var == "C"):
		if (rear):
			return "Rear Lower Rear @ Chassis"
		return "Front Lower Rear @ Chassis"
	elif (var == "MW"):
		return "Push Rod @ Bellcrank"
	elif (var == "D"):
		if (rear):
			return "Rear Upper Front @ Chassis"
		return "Front Upper Front @ Chassis"
	elif (var == "F"):
		if (rear):
			return "Rear Upper Rear @ Chassis"
		return "Front Upper Rear @ Chassis"
	elif (var == "P"):
		if (rear):
			return "Forward Bell Crank Pivot @ Post"
		return "Forward Bell Crank Pivot @ Post"
	elif (var == "Q"):
		return "Bell Crank Pivot @ Post"
	elif (var == "W"):
		return "Shock @ Chassis"
	else:
		print("Unrecognized Mitchell Variable: ", var)

def generatePartialHeaders(dfSize):
	"""
	Given the size of the dataframe, generates the headers to be applied to each
	of its cases, based off of a previously specified pattern. All headers should
	be preceded by "Left Front" or similar, and any other relevant information,
	externally.
	:param dfSize: Size of the dataframe to generate headers for
	:return: an array containing the headers to be used based on position. So the
			header for the 0 case will be first, and the header for the 1 case last
	"""

	headers = []
	headers.append("Max Brake: ")

	bcCount = dfSize // 2 - 1  # number of BC headers to add

	for i in range(1, bcCount):
		headers.append("BC " + str(i) + ": ")

	if(dfSize >= 4):
		headers.append("Max Corner 1: ")
		headers.append("Max Corner 2: ")

	acCount = dfSize // 2 - 1 # number of AC headers to add

	for i in range(1, acCount):
		headers.append("AC " + str(i) + ": ")

	headers.append("Max Accel: ")

	return headers

def addPositionColumn(index, df):
	"""
	Generates an array of the value "index", the length of the passed dataframe,
	and then appends it as a column of that dataframe.
	:param index: Number to populate with
	:param df: Dataframe to put column in
	"""
	size = df.shape[0]
	series = []
	for i in range(0, size):
		series.append(index)

	df["Load Case"] = Series(series, index=df.index)


if __name__ == '__main__':
	# if this is being run as main, asks for a file to read from and produces
	# the parsed files
	parser = argparse.ArgumentParser()
	parser.add_argument('path', type=str,
						help='Path to the input file. Must be the complete file path!')
	parser.add_argument('output_name', type=str,
						help='Name for the output file.')
	args = parser.parse_args()

	parse(args.path, args.output_name)
