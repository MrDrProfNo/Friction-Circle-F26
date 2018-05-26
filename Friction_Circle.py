"""Friction_Circle_F26.py
@author Arthur Heiles ; amh8850@g.rit.edu


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

	loadCases = int(input("Number of load cases to distribute evenly on the "
						  "range [0, pi]. 0 Case will be added, but not counted  \n"
						  "Estimated runtime of the program is ~50sec per load case\n"
						  "Enter # Load cases: "))
	fullDF = createDataframe(car, loadCases)

	print("Resulting dataframe will contain", fullDF.shape[0], " load cases." +
		" Number was increased by 1 to add case 0, and may have been increased by" +
		" an additional 1 if the .5 case was split into 2 cases.")

	dim_force_dfs = getDimensionForceDataframes(fullDF)


	full_dump(paths.output_folder, paths.dump_excel_path, fullDF)
	formatted_dump(paths.output_folder, paths.format_excel_path, dim_force_dfs)

	input("Friction_Circle.py is going to open vDosPlus. While the program is"
		  " open, do not attempt to change windows. Expected runtime is ~80 sec"
		  "per load case. \nPress Enter when ready: ")

	print("--- Opening vDosPlus, give me a minute ---")

	# Creates a new subprocess running VDosPlus
	pid = subprocess.Popen(paths.VDosPlus_path).pid
	print("Generated vDosPlus process with PID:", pid)

	# Run the macro
	macroMain(dim_force_dfs, paths)

	parse(paths.temp_front, paths.front_parsed)
	parse(paths.temp_rear, paths.rear_parsed)

	readParseToExcel(paths.front_parsed,
					 paths.rear_parsed,
					 paths.parsed_excel_path,
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
