# Friction_Circle_F26.py
# @author Arthur Heiles ; amh8850@g.rit.edu
#
# Calculates Centripetal force applied on the car as it goes through a turn.
# Takes specs of the car, theta-step (0-1), and runs calculations.
# Runs some of the results of those calculations through Mitchell's Racing by
# the numbers, and sends the results to an Excel Spreadsheet.

# Applications of the various libraries:
# decimal: forced accuracy in float addition and multiplication; used heavily
#  in the initial calculations. Note that Decimal objects cannot be used in
#  mathematical operations with floats.
#
# pandas: Dataframe objects are used to store most of the data at any given
#  moment. They are essentially just really fancy tables that make exporting to
#  Excel really easy.
#
# numpy: Used in conjunction with pandas
#
# keyboard: python class to simulate keypresses on the active window. It's used
#  as the primary method of entering information into the VDosPlus emulator for
#  Mitchell's. Needs ~.5 seconds between keypressed for them to properly fire.
#
# win32_____: Manipulating open windows so that keyboard targets the correct one
#  and managing the system clipboard.


from decimal import Decimal
from numpy import *
from pandas import *

import forces_parser

from force_calculator import createDataframe

from friction_circle_init import init


## Constants
CONFIG_FILE = "carConfig.txt"


def getDimensionForceDataframes(fullDF):
	# Create dataframe for x forces
	df_MCPFx = DataFrame(fullDF.loc[:, ["LF_Fx", "RF_Fx", "LR_Fx", "RR_Fx"] ])
	# Create dataframe for y forces
	df_MCPFy = DataFrame(fullDF.loc[:, ["LF_Fy", "RF_Fy", "LR_Fy", "RR_Fy"] ])
	# Create dataframe for z forces
	df_MCPFz = DataFrame(fullDF.loc[:, ["LF_Fz", "RF_Fz", "LR_Fz", "RR_Fz"] ])
	return df_MCPFx, df_MCPFy, df_MCPFz

def readParseToExcel(fromFileFront, fromFileRear, toFile, df_full):
	"""
	Takes
	:return:
	"""
	try:
		f = open(fromFileFront)
	except:
		print("Error in opening file:", fromFileFront,
			  "\n Could not find file.")
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

			# case = Decimal(case)
			# case = round(case, 1)
			if (displacement == 0):  # right front wheel
				displacement = 1
				titleText += "Right Front "
				df.loc["Values", "X":"Z"] = caseData["RF_Fx"], \
											caseData["RF_Fy"], \
											caseData["RF_Fz"],
			elif (displacement == 1):  # left front wheel
				displacement = 0
				titleText += "Left Front "
				df.loc["Values", "X":"Z"] = caseData["LF_Fx"], \
											caseData["LF_Fy"], \
											caseData["LF_Fz"]
			elif (displacement == 2):  # right rear wheel
				displacement = 3
				titleText += "Right Rear "
				df.loc["Values", "X":"Z"] = caseData["RR_Fx"], \
											caseData["RR_Fy"], \
											caseData["RR_Fz"]
			elif (displacement == 3):  # left rear wheel
				displacement = 2
				titleText += "Left Rear "
				df.loc["Values", "X":"Z"] = caseData["LR_Fx"], \
											caseData["LR_Fy"], \
											caseData["LR_Fz"]

			df.to_excel(writer, sheet_name="Sheet 1",
						startcol=leftMargin + (
						displacement * (tablewidth + xspacing)),
						startrow=topMargin + (
						(count // 2) * (yspacing + tableheight))
						)

			case = (count // 2)

			# occasionally spits a message into console, but never crashes
			# message roughly "non-integers will soon cease to be supported"
			case_theta_coef = df_full.index[case]

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
					print("Error in opening file:", fromFileRear, "\n "
																  "File may not exist")

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

		line[1] = Decimal(line[1])
		line[2] = Decimal(line[2])
		line[3] = Decimal(line[3])
		dataDict[line[0]] = [line[1], line[2], line[3],
							 "=SQRT(INDIRECT(\"C[-1]\","
							 " FALSE)^2 +INDIRECT(\"C[-2]\", FALSE)^2 + "
							 "INDIRECT(\"C[-3]\", FALSE)^2)"
							 ]
		line = f.readline()

	writer.close()


def replaceMitchellVariables(var, rear=False):
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


def main():
	print("Friction_Circle.py\n")

	loadCases = int(input("Number of load cases to distribute evenly on the "
						  "range [0, pi], inclusive on both ends. \n"
						  "Enter # Load cases: "))

	car = init(CONFIG_FILE) # init returns a Car object with attr. loaded from config
	fullDF= createDataframe(car, loadCases)
	dim_force_dfs = getDimensionForceDataframes(fullDF)


	outputFolderPath = "./Friction_Circle_F26_Output/"
	DFToExcel.full_dump(outputFolderPath, "dump.xlsx", fullDF)
	DFToExcel.formatted_dump(outputFolderPath, "formatting.xlsx", dim_force_dfs)

	# input("Ensure that vDosPlus running Mitchell is open before continuing.\n"
	# 	  "Press Enter to continue:")

	# # Run the macro
	# macroMain(dim_force_dfs)

	forces_parser.main("tmpF.txt", "FOutput.txt")
	forces_parser.main("tmpR.txt", "ROutput.txt")

	# readParseToExcel("FOutput.txt", "ROutput.txt", "./Parsed_Forces.xlsx",
	# 				 fullDF)


if __name__ == "__main__":
	main()
