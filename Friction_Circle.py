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

from forces_parser import parse, readParseToExcel
from force_calculator import createDataframe
from friction_circle_init import init
from df_to_excel import full_dump, formatted_dump
from macro import macroMain

## Constants
CONFIG_FILE = "carConfig.txt"


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
	print("Friction_Circle.py\n")

	loadCases = int(input("Number of load cases to distribute evenly on the "
						  "range [0, pi], inclusive on both ends. \n"
						  "Enter # Load cases: "))

	car = init(CONFIG_FILE) # init returns a Car object with attr. loaded from config
	fullDF= createDataframe(car, loadCases)
	dim_force_dfs = getDimensionForceDataframes(fullDF)


	outputFolderPath = "./Friction_Circle_F26_Output/"
	full_dump(outputFolderPath, "dump.xlsx", fullDF)
	formatted_dump(outputFolderPath, "formatting.xlsx", dim_force_dfs)

	input("Ensure that vDosPlus running Mitchell is open before continuing.\n"
		  "Press Enter to continue:")

	# Run the macro
	macroMain(dim_force_dfs)

	parse("tmpF.txt", "FOutput.txt")
	parse("tmpR.txt", "ROutput.txt")

	readParseToExcel("FOutput.txt", "ROutput.txt", "./Parsed_Forces.xlsx",
	 				 fullDF)


if __name__ == "__main__":
	main()
