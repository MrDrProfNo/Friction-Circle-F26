"""Friction_Circle_F26.py
@author MrDrProfNo

z


Calculates Centripetal force applied on the car as it goes through a turn.
Takes specs of the car, theta-step (0-1), and runs calculations.
Runs some of the results of those calculations through Mitchell's Racing by
the numbers, and sends the results to an Excel Spreadsheet.

Numbers are all stored as Decimal objects to preserve float accuracy

pandas Dataframes are used to store data, due to their easy-to-use .to_excel
methods.



Applications of the various libraries:
decimal: forced accuracy in float addition and multiplication; used heavily
 in the initial calculations. Note that Decimal objects cannot be used in
 mathematical operations with floats.

pandas: Dataframe objects are used to store most of the data at any given
 moment. They are essentially just really fancy tables that make exporting to
 Excel really easy.

numpy: Used in conjunction with pandas

keyboard: python class to simulate keypresses on the active window. It's used
 as the primary method of entering information into the VDosPlus emulator for
 Mitchell's. Needs ~.5 seconds between keypressed for them to properly fire.

win32_____: Manipulating open windows so that keyboard targets the correct one
 and managing the system clipboard.f
"""

import subprocess

from pandas import DataFrame
import pandas as pd

from df_to_excel import full_dump, formatted_dump
from force_calculator import createDataframe
from forces_parser import parse, readParseToExcel
from friction_circle_init import init
from macro import macroMain
from traceback import print_tb

import os

## Constants
PATH_CONFIG_FILE = "path_config.txt"


def getDimensionForceDataframes(fullDF):
	"""
	Separates out 3 dataframes from the full one; these dataframes are 
	specifically used later in the program, and as such the columns separated
	are hardcoded.
	The three sets are:
	LF_Fx, RF_Fx, LR_Fx, RR_Fx;
	LF_Fy, RF_Fy, LR_Fy, RR_Fy;
	LF_Fz, RF_Fz, LR_Fz, RR_Fz;

	:param fullDF: the complete Dataframe from force_calculator
	:return: 3-tuple of the separated dataframes x,y,z
	"""
	# Create dataframe for x forces
	df_MCPFx = DataFrame(fullDF.loc[:, ["LF_Fx", "RF_Fx", "LR_Fx", "RR_Fx"] ])
	# Create dataframe for y forces
	df_MCPFy = DataFrame(fullDF.loc[:, ["LF_Fy", "RF_Fy", "LR_Fy", "RR_Fy"] ])
	# Create dataframe for z forces
	df_MCPFz = DataFrame(fullDF.loc[:, ["LF_Fz", "RF_Fz", "LR_Fz", "RR_Fz"] ])
	return df_MCPFx, df_MCPFy, df_MCPFz


def getInvertedDimensionForceDataframes(fullDF):
	"""
	The same as getDimensionForceDataframes, except it inverts values in the X
	and Y component dataframes. This puts them in the correct form for Mitchell's,
	which uses a different dimension system than the team, apparently.
	:param FullDF:
	:return:
	"""
	# Create dataframe for x forces
	df_MCPFx = -(DataFrame(fullDF.loc[:, ["LF_Fx", "RF_Fx", "LR_Fx", "RR_Fx"] ]))

	# Create dataframe for y forces
	df_MCPFy = -(DataFrame(fullDF.loc[:, ["LF_Fy", "RF_Fy", "LR_Fy", "RR_Fy"] ]))
	# Create dataframe for z forces
	df_MCPFz = DataFrame(fullDF.loc[:, ["LF_Fz", "RF_Fz", "LR_Fz", "RR_Fz"] ])
	return df_MCPFx, df_MCPFy, df_MCPFz


def main():
	"""
	Main controls the program, walking through the steps in order:
	1. Load from config files
	2. Ask user for number of load cases
	3. Generate full dataset using force_calculator.py
	4. Generate dump and formatted excel spreadsheets using df_to_excel.py
	5. Open VDosPlus, which should default to running Mitchell's Racing by the Numbers
	6. Run macro.py to put formatted dataset through Mitchell's
	7. Run forces_parser.py to take Mitchell's copied output and make it readable
	8. Continue running forces_parser.py to export the parsed Mitchell output to Excel
	"""
	print("########  Friction_Circle.py  ########")

	directory = os.path.dirname(__file__)
	os.chdir(directory)

	# init returns a Car object with attr. loaded from config
	car, paths = init(PATH_CONFIG_FILE)

	fullDF = None

	# We're gonna try to load the input from excel first, since that's the new
	# main use of the program.

	print("Are you using outboard braking? This "
		   "setting will determine whether rear axle forces are put "
		   "into Mitchell using the Force-At-Axle field for both"
		   "halves of the load cases, or just the second half.")
	while True:
		useOutboardStr = input("Type \"y\" for outboard, or \"n\" for inboard:\n")
		if useOutboardStr.lower() == "y" or useOutboardStr.lower() == "yes":
			car.use_outboard_breaks = True
			break
		elif useOutboardStr.lower() == "n" or useOutboardStr.lower() == "no":
			car.use_outboard_breaks = False
			break
		else:
			print("Unrecognized input.")

	try:
		# empty input path is the main signifier to do the calculations yourself
		if not (paths.excel_input_path == ""):
			# will throw error on fail; handled down below
			fullDF = pd.read_excel(paths.excel_input_path)
			print("Found Excel file to draw input from: "
				  + paths.excel_input_path + "\n")
			print("Do you want to use this data? Entering n will use the"
				  + " program's internal calculations for input forces instead. \n"
				  + " (MAY BE OUT OF DATE; this is a legacy testing feature"
				  + " maintained at Jake's request) (y/n)")
			while True:
				useExcel = input()

				if (useExcel.lower() == "n" or  # n or no answered
						useExcel.lower() == "no"):
					fullDF = None
					break
				elif (not (useExcel.lower() == "y" or  # not y or yes
						   useExcel.lower() == "yes")):
					print("Unrecognized answer. Try again?\n")
					continue
				else:  # y or yes answered
					break  # exit the input request loop and set values

		else:
			print("No input Excel path given; defaulting to program calculations \n"
				  + " (MAY BE OUT OF DATE; this is a legacy testing feature"
				  + " maintained at Jake's request)")
	except FileNotFoundError:
		print("Invalid path given for Excel input file; defaulting to program"
			  	  + " caclculations (MAY BE OUT OF DATE; this is a legacy testing"
				  + " feature maintained at Jake's request)")

	if(fullDF is None):
		loadCases = int(
			input("Number of load cases to distribute evenly on the "
				  "range [0, pi]. 0 Case will be added, but not counted  \n"
				  "Estimated runtime of the program is ~50sec per load case\n"
				  "Enter # Load cases: "))

		fullDF = createDataframe(car, loadCases)


		print("Resulting dataframe will contain", fullDF.shape[0], " load cases." +
			" Number was increased by 1 to add case 0, and may have been increased by" +
			" an additional 1 if the .5 case was split into 2 cases.")
	else:
		print("Input dataframe contains", fullDF.shape[0], " load cases.")

	dim_force_dfs = getDimensionForceDataframes(fullDF)


	full_dump(paths.output_folder, paths.dump_excel_path, fullDF)
	formatted_dump(paths.output_folder, paths.format_excel_path, dim_force_dfs)

	# Produces and outputs a variant of the data set with the correct signs for
	# Mitchell's coordinate system
	dim_force_dfs_CSYS = getInvertedDimensionForceDataframes(fullDF)
	formatted_dump(paths.output_folder, "formatted_CSYS.xlsx", dim_force_dfs_CSYS)


	input("Friction_Circle.py is going to open vDosPlus. While the program is"
		  " open, do not attempt to change windows. Expected runtime is ~80 sec"
		  " per load case. \nPress Enter when ready: ")

	print("--- Opening vDosPlus, give me a minute ---")

	# Creates a new subprocess running VDosPlus
	pid = subprocess.Popen(paths.VDosPlus_path).pid
	print("Generated vDosPlus process with PID:", pid)

	# Run the macro
	macroMain(dim_force_dfs_CSYS, paths, car)

	parse(paths.temp_front, paths.front_parsed)
	parse(paths.temp_rear, paths.rear_parsed)

	readParseToExcel(paths.front_parsed,
					 paths.rear_parsed,
					 paths.output_folder + '/' + paths.parsed_excel_path,
					 fullDF)


if __name__ == "__main__":

	# this setup just catches errors when running from terminal or python shell
	# so it doesn't close immediately.
	try:
		main()
	except Exception as e:
		print("Encountered Error during runtime: \n", e.args)
		print_tb(e.__traceback__)
	finally:
		input("Press Enter when done")
