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



import \
	math as m  # imput math library for sin, cos, pi. All such references must be preceeded by m.
from decimal import *
from numpy import *
from pandas import *
import os  # filepath related functions
import win32gui  # EnumWindows, GetWindowText, FindWindow, SetForegroundWindow
import keyboard
from time import sleep
from win32clipboard import OpenClipboard, CloseClipboard, GetClipboardData
import traceback

import forces_parser


class Car:
	def __init__(self, cfg):
		# Params
		params = self.ParamsFromConfig(cfg)  # Grab car params from file

		self.M = params["M"]  # Car Weight
		self.D = params["D"]  # Driver Weight
		self.W_d = params["W_d"]  # Weight Distribution
		self.CG = params["CG"]  # CG height
		self.WB = params["WB"]  # Wheelbase
		self.TW = params["TW"]  # Track Width
		self.A = params["A"]  # Aero
		self.A_d = params["A_d"]  # Aero Distribution
		self.Long_WT = params["Long_WT"]  # Longitudinal Weight Transfer
		self.Lat_WT = params["Lat_WT"]  # Lateral Weight Transfer
		# a and b (max long accel, max lat accel)
		self.a, self.b, self.fz_f, self.fz_r = self.secondaryParams(params)


	def ParamsFromConfig(self, cfg):
		"""
		Draws initial car parameters from a config file, whose path is given
		by cfg. Any additional parameters will need to be hardcoded in here
		:param cfg: string path to config file
		:return:
		"""
		params = {}
		for line in open(cfg):
			if line.startswith("#"):
				continue  # Skip comments
			param, value = map(str.strip, line.split("="))
			params[param] = Decimal(value)
		CG = params["CG"]
		WB = params["WB"]
		TW = params["TW"]
		params["Long_WT"] = Decimal(CG / WB)
		params["Lat_WT"] = Decimal(CG / TW)
		return params

	def secondaryParams(self, params):
		"""
		Generates the secondary set of constant parameters based on those read
		from the config file.
		:param params: params dictionary produced by ParamsFromConfig
		:return: tuple containing variables a, b, Fz_f, Fz_r (Max Long Accel,
				Max Lat Accel, Front Static Corner weight, Rear Static Corner
				weight)
		"""

		W_d = params["W_d"]
		M = params["M"]
		D = params["D"]
		A = params["A"]
		A_d = params["A_d"]
		# In order for math-related operations to work, Decimal cannot be
		# multiplied by a float. Separate Decimals are kept around for pi
		Fz_f = Decimal((W_d * (M + D)) / 2)  # Front Static Corner weight
		Fz_r = Decimal(((1 - W_d) * (M + D)) / 2)  # Rear Static Corner weight
		# A and B
		Fr_A = Decimal(Fz_f * 2 + A * A_d)  # Front Axle Weight
		Re_A = Decimal(Fz_r * 2 + A * (1 - A_d))  # Rear Axle Weight
		Mux_f = Decimal(2.2677) - Decimal(.0007) * (Fr_A)  # Front Mu_x
		Mux_r = Decimal(2.2677) - Decimal(.0007) * (Re_A)  # Rear Mu_x
		Muy_f = Decimal(1.7625) - Decimal(.0004) * (Fr_A)  # Front Mu_y
		Muy_r = Decimal(1.7625) - Decimal(.0004) * (Re_A)  # Rear Mu_y
		Fr_Fx = Mux_f * Fr_A  # Front Cornering Force (x)
		Fr_Fy = Muy_f * Fr_A  # Front Cornering Force (y)
		Re_Fx = Mux_r * Re_A  # Rear Cornering Force (x)
		Re_Fy = Muy_r * Re_A  # Rear Cornering Force (y)
		Total_x = Fr_Fx + Re_Fx  # Total X Cornering Force
		Total_y = Fr_Fy + Re_Fy  # Total Y Cornering Force
		a = Total_x / (M + D)  # Max Long Accel
		b = Total_y / (M + D)  # Max Lat Accel

		return a, b, Fz_f, Fz_r

		# Doesn't work because current version of python does not support format strings
		# def __str__(self):
		#     s = ("Car:\n"
		#          f"  Params:\n"
		#          f"    M={self.M}\n"
		#          f"    D={self.D}\n"
		#          f"    W_d={self.W_d}\n"
		#          f"    CG={self.CG}\n"
		#          f"    WG={self.WB}\n"
		#          f"    TW={self.TW}\n"
		#          f"    A={self.A}\n"
		#          f"    A_d={self.A_d}\n"
		#          f"    Long_WT={self.Long_WT}\n"
		#          f"    Lat_WT={self.Lat_WT}\n")
		#     return s


def createDataframe(car, loadCases):
	"""

	:param car: Car object containing data for the car
	:param loadCases: Number of loadcases to run with; should be int, checked
					internally
	:return: Dataframe containing the calculated values in a dictionary
	"""

	# Error checking with more descriptive crash errors.
	if (not isinstance(loadCases, int)):
		raise TypeError("number of load cases must be of type int")


	elif (loadCases <= 0):
		raise ValueError("number of load cases must be greater than 0")

	# dictionary to store all of the calculations. Order is irrelevant, but
	# all keys must match the strings in columns array below.
	datadict = {'r_theta':	[],	'XG':	 	[],	'YG':		[],
				'RF_Fz':	[],	'LF_Fz': 	[], 'RR_Fz':	[],
				'LR_Fz': 	[],	'LF_Mu_x':	[],	'RF_Mu_x':	[],
				'LR_Mu_x':	[],	'RR_Mu_x':	[],	'LF_Mu_y':	[],
				'RF_Mu_y':	[],	'LR_Mu_y':	[],	'RR_Mu_y':	[],
				'LF_Fx':	[],	'RF_Fx':	[],	'LR_Fx':	[],
				'RR_Fx':	[],	'Fx':		[],	'LoG':		[],
				'LF_Fy':	[],	'RF_Fy':	[],	'LR_Fy':	[],
				'RR_Fy':	[],	'Fy':		[], 'LaG':		[],
				'LF_c':		[], 'RF_c':		[], 'LR_c':		[],
				'RR_c':		[]}

	# all values of theta coefficient that calculations are run for [0, 1]
	theta_coef_all = []

	columns = ["r_theta", 	"XG", 		"YG",		"LF_Fz",	"RF_Fz",	"LR_Fz",
			"RR_Fz",	"LF_Mu_x", 	"RF_Mu_x", 	"LR_Mu_x", 	"RR_Mu_x",	"LF_Mu_y",
			"RF_Mu_y", 	"LR_Mu_y", 	"RR_Mu_y",	"LF_Fx", 	"RF_Fx", 	"LR_Fx",
			"RR_Fx", 	"Fx", 		"LoG",		"LF_Fy", 	"RF_Fy", 	"LR_Fy",
			"RR_Fy", 	"Fy", 		"LaG",		"LF_c", 	"RF_c", 	"LR_c",
			"RR_c"]

	# in special case 1, only generate the 1 case
	if(loadCases == 1):
		calculateForCaseN(datadict, car, 1)
		theta_coef_all.append( Decimal(1) )
		df = DataFrame(data=datadict, index=theta_coef_all, columns=columns)
		return df
	else:
		for case in range(0, loadCases): # endpoint will be loadcases - 1


			# dividing by loadcases - 1 ensures we're on range [0, 1]
			theta_coef = Decimal(case / (loadCases - 1 ) )
			if(theta_coef == Decimal(.5) ):
				theta_coef_all.append(theta_coef - theta_coef / 1000)
				theta_coef_all.append(theta_coef + theta_coef / 1000)
				continue
			theta_coef_all.append( Decimal( case / (loadCases - 1) ) )




	for coef in theta_coef_all:

		# run calculations for this n. Output goes directly into datadict, no
		# return. If n == .5, run for cases slightly on either side of it.
		# if(coef == Decimal(.5) ):
		# 	mod = coef / Decimal(100)
		# 	calculateForCaseN(datadict, car, coef - mod)
		# 	calculateForCaseN(datadict, car, coef + mod)

		# else:
			calculateForCaseN(datadict, car, coef)


	df = DataFrame(data=datadict, index=theta_coef_all, columns=columns)

	return df

def calculateForCaseN(datadict, car, n):
	"""
	Runs calculations for all values for the given theta-coefficient n. Uses
	default values for the Car as given by the car object, which should have read
	them from carConfig.txt

	Some values require division by cos(n * pi). In the .5 case, this evaluates
	to zero. Such cases are substituted with a value extremely close to n.

	The passed datadict MUST contain all of the expected keys, or the code WILL
	crash. This function will add data directly to it, assuming that the keys
	exist. Workaround is pending.

	:param datadict: dictionary mapping the expected key set to Decimal values
	:param car: Car object with car-related variables initialized
	:param n: current theta-coefficient, which corresponds to a load case.
	"""

	# Decimal variants of all frequently used math library tools;
	# these should be subbed into the code where needed
	# instead of running Decimal conversions every time.
	pi = Decimal(m.pi)
	cosNPi = Decimal(m.cos(n * pi))
	sinNPi = Decimal(m.sin(n * pi))



	# constants that really need a better name but I don't know what they are
	# name origin is that this is how they were in the original matlab code.
	# The 6-position calculation for YG and 1-position for XG were being reused
	# later in the code as constants with no explanation. Something to do with
	# their theta coefficients.
	YG_6 = (car.a * car.b) / Decimal(
		m.sqrt((car.b * Decimal(m.cos(0.49 * m.pi))) ** 2 + \
			   ((car.a * Decimal(m.sin(0.49 * m.pi)))) ** 2)) * \
		   Decimal(m.sin(0.49 * m.pi))
	XG_1 = -((car.a * car.b) / Decimal(m.sqrt(car.b ** 2)))


	# define variables for car constants to make code easier to read
	a = car.a
	b = car.b
	Fz_f = car.fz_f
	Fz_r = car.fz_r
	M = car.M
	D = car.D
	Long_WT = car.Long_WT
	Lat_WT = car.Lat_WT
	A = car.A
	A_d = car.A_d


	r_theta_n = (a * b) / Decimal(
		m.sqrt(((b * cosNPi) ** 2 + ((a * sinNPi)) ** 2)))
	XG_n = -(r_theta_n * cosNPi)
	YG_n = r_theta_n * sinNPi
	RF_Fz_n = Fz_f + (M + D) / 2 * (-Long_WT * XG_n + Lat_WT * YG_n) + (
		A * A_d / 2)
	LF_Fz_n = Fz_f + (M + D) / 2 * (-Long_WT * XG_n - Lat_WT * YG_n) + (
		A * A_d / 2)
	RR_Fz_n = Fz_r + (M + D) / 2 * (Long_WT * XG_n + Lat_WT * YG_n) + (
		A * (n - A_d) / 2)
	LR_Fz_n = Fz_r + (M + D) / 2 * (Long_WT * XG_n - Lat_WT * YG_n) + (
		A * (1 - A_d) / 2)
	LF_Mu_x_n = (Decimal(2.2677) - Decimal(.0007) * (abs(LF_Fz_n))) * (
		XG_n / XG_1)
	RF_Mu_x_n = (Decimal(2.2677) - Decimal(.0007) * (abs(RF_Fz_n))) * (
		XG_n / XG_1)
	LR_Mu_x_n = (Decimal(2.2677) - Decimal(.0007) * (abs(LR_Fz_n))) * (
		XG_n / XG_1)
	RR_Mu_x_n = (Decimal(2.2677) - Decimal(.0007) * (abs(RR_Fz_n))) * (
		XG_n / XG_1)
	LF_Mu_y_n = (Decimal(1.7625) - Decimal(.0004) * (abs(LF_Fz_n))) * (
		YG_n / YG_6)
	RF_Mu_y_n = (Decimal(1.7625) - Decimal(.0004) * (abs(RF_Fz_n))) * (
		YG_n / YG_6)
	LR_Mu_y_n = (Decimal(1.7625) - Decimal(.0004) * (abs(LR_Fz_n))) * (
		YG_n / YG_6)
	RR_Mu_y_n = (Decimal(1.7625) - Decimal(.0004) * (abs(RR_Fz_n))) * (
		YG_n / YG_6)
	LFX_n = -LF_Mu_x_n * LF_Fz_n
	RFX_n = -RF_Mu_x_n * RF_Fz_n
	LRX_n = -LR_Mu_x_n * LR_Fz_n
	RRX_n = -RR_Mu_x_n * RR_Fz_n
	Fx_n = LFX_n + RFX_n + LRX_n + RRX_n
	LoG_n = Fx_n / (M + D)
	LFY_n = LF_Mu_y_n * LF_Fz_n
	RFY_n = RF_Mu_y_n * RF_Fz_n
	LRY_n = LR_Mu_y_n * LR_Fz_n
	RRY_n = RR_Mu_y_n * RR_Fz_n
	Fy_n = LFY_n + RFY_n + LRY_n + RRY_n
	LaG_n = Fy_n / (M + D)
	LF_c_n = Decimal(
		m.sqrt(abs(LF_Fz_n) ** 2 + abs(LFX_n) ** 2 + abs(LFY_n) ** 2))
	RF_c_n = Decimal(
		m.sqrt(abs(RF_Fz_n) ** 2 + abs(RFX_n) ** 2 + abs(RFY_n) ** 2))
	LR_c_n = Decimal(
		m.sqrt(abs(LR_Fz_n) ** 2 + abs(LRX_n) ** 2 + abs(LRY_n) ** 2))
	RR_c_n = Decimal(
		m.sqrt(abs(RR_Fz_n) ** 2 + abs(RRX_n) ** 2 + abs(RRY_n) ** 2))

	# Collect all values of n; used for row labeling later
	datadict["r_theta"].append(r_theta_n)
	datadict["XG"].append(XG_n)
	datadict["YG"].append(YG_n)
	datadict["RF_Fz"].append(RF_Fz_n)
	datadict["LF_Fz"].append(LF_Fz_n)
	datadict["RR_Fz"].append(RR_Fz_n)
	datadict["LR_Fz"].append(LR_Fz_n)
	datadict["LF_Mu_x"].append(LF_Mu_x_n)
	datadict["RF_Mu_x"].append(RF_Mu_x_n)
	datadict["LR_Mu_x"].append(LR_Mu_x_n)
	datadict["RR_Mu_x"].append(RR_Mu_x_n)
	datadict["LF_Mu_y"].append(LF_Mu_y_n)
	datadict["RF_Mu_y"].append(RF_Mu_y_n)
	datadict["LR_Mu_y"].append(LR_Mu_y_n)
	datadict["RR_Mu_y"].append(RR_Mu_y_n)
	datadict["LF_Fx"].append(LFX_n)
	datadict["RF_Fx"].append(RFX_n)
	datadict["LR_Fx"].append(LRX_n)
	datadict["RR_Fx"].append(RRX_n)
	datadict["Fx"].append(Fx_n)
	datadict["LoG"].append(LoG_n)
	datadict["LF_Fy"].append(LFY_n)
	datadict["RF_Fy"].append(RFY_n)
	datadict["LR_Fy"].append(LRY_n)
	datadict["RR_Fy"].append(RRY_n)
	datadict["Fy"].append(Fy_n)
	datadict["LaG"].append(LaG_n)
	datadict["LF_c"].append(LF_c_n)
	datadict["RF_c"].append(RF_c_n)
	datadict["LR_c"].append(LR_c_n)
	datadict["RR_c"].append(RR_c_n)

	# no return, data is all stored in passed dictionary

def getDimensionForceDataframes(fullDF):
	# Create dataframe for x forces
	df_MCPFx = DataFrame(fullDF.loc[:, ["LF_Fx", "RF_Fx", "LR_Fx", "RR_Fx"] ])
	# Create dataframe for y forces
	df_MCPFy = DataFrame(fullDF.loc[:, ["LF_Fy", "RF_Fy", "LR_Fy", "RR_Fy"] ])
	# Create dataframe for z forces
	df_MCPFz = DataFrame(fullDF.loc[:, ["LF_Fz", "RF_Fz", "LR_Fz", "RR_Fz"] ])
	return df_MCPFx, df_MCPFy, df_MCPFz

class DFToExcel:
	@staticmethod
	def full_dump(dirpath, filename, dataframe):
		### Full dump to Excel ###
		# Original target directory: ./Friction_Circle_F26_Output/dump.xlsx
		# ./ references current directory;
		# './Friction_Circle_F26_Output/formatting.xlsx' recommended.
		if not os.path.exists(dirpath):
			try:
				os.makedirs(dirpath)  # use os.makedirs to create the directory
			except:
				traceback.print_exc()
				print("Error in makedirs(", dirpath, ")")
		dataframe.to_excel(dirpath + filename)

	@staticmethod
	def formatted_dump(dirpath, filename, dataframes):
		### Separate out Max Contact Patch Forces ###
		df_MCPFx, df_MCPFy, df_MCPFz = dataframes
		# Set the filepath for the target file by appending to path to output
		# folder
		formattedPath = dirpath + filename

		# Define the pandas ExcelWriter using xlsxwriter as the engine
		writer = ExcelWriter(formattedPath, engine='xlsxwriter')

		# Dump each of the above dataFrames to the spreadsheet.
		# NOTE: This will not work if there is a variable currently assigned to
		#  the worksheet being modified. Why? Couldn't say.
		# <DataFrame>.to_excel(<ExcelWriter>, <name of target sheet (will create)>,<origin row>, <origin column>
		# Start at col 1
		df_MCPFx.to_excel(writer, sheet_name="Sheet 1", startrow=3, startcol=0)
		# Start at col 6
		df_MCPFy.to_excel(writer, sheet_name="Sheet 1", startrow=3, startcol=5)
		# Start at col 11
		df_MCPFz.to_excel(writer, sheet_name="Sheet 1", startrow=3, startcol=10)

		workbook = writer.book
		ws = writer.sheets["Sheet 1"]

		### Declare format for header cells
		# <Workbook>.add_format(<singleton dictionary declaration>{<list of tags in '<tag>': state form>}
		formatHeader = workbook.add_format(
			{'bold': True, 'align': 'center', 'font_size': 24})
		formatSubHeader = workbook.add_format({'bold': True, 'align': 'center'})
		# <Worksheet>.write(<column>, <row>, <value to write>, <Format (optional)>
		ws.write(2, 2, "Longitudinal Force (X+)", formatSubHeader)
		ws.write(2, 7, "Lateral Force (Y+)", formatSubHeader)
		ws.write(2, 12, "Vertical Force (Z+)", formatSubHeader)
		# <Worksheet>.merge_range('<corner1 Coord:corner2 Coord>', <value to write>, <Format (optional)>)
		ws.merge_range('C1:N2', "Max Contact Patch Forces", formatHeader)

		# Setup cell color formatting
		format_bg_red = workbook.add_format({"bg_color": "red"})
		format_bg_yellow = workbook.add_format({"bg_color": "yellow"})
		format_bg_green = workbook.add_format({"bg_color": "green"})

		# Number of elements present; treating it as though zero-indexed
		dataLength = df_MCPFx.shape[0] - 1

		# Row that data starts at; hardcoded for now
		dataStart = 5

		# Strings labeling the start and end points of each coloring segment
		# for the formatting (by row). Names should be fairly self-evident.

		GREEN_START_STR = str(dataStart)

		GREEN_END_STR = str(dataStart + dataLength // 2 - 1)

		YELLOW_START_STR = str(dataStart + dataLength // 2)

		YELLOW_END_STR = str(dataStart + (dataLength + 1) // 2)

		RED_START_STR = str(dataStart + 1 + (dataLength + 1) // 2)

		RED_END_STR = str(dataStart + dataLength)


		if(df_MCPFx.shape[0] % 2 == 0):
			CENTER_THICKNESS = 1
		else:
			CENTER_THICKNESS = 0


		# So... this works. Select cell range, tell it to look for text not
		# containing "t"; they're all numbers, so that will always evaluate true
		### Longitudinal Force Formatting ###
		ws.conditional_format('B' + GREEN_START_STR + ':E' + GREEN_END_STR,
							  {"type": "text", "criteria": "not containing",
							   "value": "t", "format": format_bg_red})
		ws.conditional_format('B' + YELLOW_START_STR + ':E' + YELLOW_END_STR,
							  {"type": "text", "criteria": "not containing",
							   "value": "t", "format": format_bg_yellow})
		ws.conditional_format('B' + RED_START_STR + ':E' + RED_END_STR,
							  {"type": "text", "criteria": "not containing",
							   "value": "t", "format": format_bg_green})
		### Lateral Force Formatting ###
		ws.conditional_format('G' + GREEN_START_STR + ':J' + GREEN_END_STR,
							  {"type": "text", "criteria": "not containing",
							   "value": "t", "format": format_bg_red})
		ws.conditional_format('G' + YELLOW_START_STR + ':J' + YELLOW_END_STR,
							  {"type": "text", "criteria": "not containing",
							   "value": "t", "format": format_bg_yellow})
		ws.conditional_format('G' + RED_START_STR + ':J' + RED_END_STR,
							  {"type": "text", "criteria": "not containing",
							   "value": "t", "format": format_bg_green})
		### Vertical Force Formatting ###
		ws.conditional_format('L' + GREEN_START_STR + ':O' + GREEN_END_STR,
							  {"type": "text", "criteria": "not containing",
							   "value": "t", "format": format_bg_red})
		ws.conditional_format('L' + YELLOW_START_STR + ':O' + YELLOW_END_STR,
							  {"type": "text", "criteria": "not containing",
							   "value": "t", "format": format_bg_yellow})
		ws.conditional_format('L' + RED_START_STR + ':O' + RED_END_STR,
							  {"type": "text", "criteria": "not containing",
							   "value": "t", "format": format_bg_green})

		writer.save()


def pullToFront(handle, windowName):
	"""
	Use this function as a referenace pass to win32gui.EnumWindows.
	Pulls the first window whose text contains windowName to the front

	The behavior of EnumWindows is sporadic; sometimes it passes a handle,
	sometimes it passes an int, and I can't find a reason why. So both cases
	are dealt with below.
	:param handle: handle OR int passed by EnumWindows
	:param windowName: text to check for in the passed handle
	:return:
	"""
	if (isinstance(handle, int)):
		windowText = win32gui.GetWindowText(handle)
		window = win32gui.FindWindow(None, windowText)
		if (windowName in windowText.lower()):
			# Sends an alt keypress. For some reason, SetForegroundWindow throws an error
			# with message 'no error message is available' unless alt is pressed right before
			# it. I don't understand, I don't need to understand. Just leave it be.
			keyboard.send('alt')
			win32gui.SetForegroundWindow(window)
	elif (windowName in handle[1].lower()):
		# Sends an alt keypress. For some reason, SetForegroundWindow throws an error
		# with text 'no error message is available' unless alt is pressed right before
		# it. I don't understand, I don't need to understand. Just leave it be.
		keyboard.send('alt')
		win32gui.SetForegroundWindow(handle)

def macroMain(dim_force_dfs):
	"""
	Runs the macro for Racing by the Numbers, inputting data drawn from the
	partial dataframes. dim_force_dfs must be a 3-tuple of Dataframes, otherwise
	there will be problems.

	The steps to reach the config files is hardcoded below. Directional instructions
	followed by "enter" will select a file; just give the directions needed to
	reach the correct file.

	:param dim_force_dfs:
	:return:
	"""

	pressToFront = ("down", "right", "enter")
	pressToRear =  ("down", "down", "right", "enter")

	macroSetup(pressToFront)

	macroRunAxle(dim_force_dfs, "F", "tmpF.txt")

	keyboard.send("q")
	keyboard.send("q")
	keyboard.send("n")
	keyboard.send("n")

	macroSetup(pressToRear)

	macroRunAxle(dim_force_dfs, "R", "tmpR.txt")

	macroQuit()



def macroSetup(configSteps):
	# Should be "vdosplus", may change when testing
	win32gui.EnumWindows(pullToFront, "vdosplus")
	sleep(1)
	keyboard.send("enter")
	sleep(.5)
	for step in configSteps:
		keyboard.send(step)
		sleep(.5)
	sleep(.5)
	keyboard.send("enter")
	sleep(.5)
	keyboard.send("enter")
	sleep(.5)
	keyboard.send("x")
	sleep(.5)
	keyboard.send("f")
	sleep(3)

def macroRunAxle(dim_force_dfs, axle, fOutput):
	"""
	Run the macro for the front or rear axle of the car (requires different
	configs in Mitchell). Takes the passed 3-tuple of dataframes, which contain
	the x, y, z values respectively for each wheel (so Front-rightx, front-leftx
	rear-rightx, rear-leftx) and inputs them into mitchell, copying the output to
	a file.
	:param dim_force_dfs: 3-tuple of DFs containing the x, y, z forces acting on
						the wheels, as specified above.
	:param axle: "F" or "R" for front or rear respectively
	:param fOutput Filepath to send front output file to
	:param rOutput Filepath to send rear output file to
	:return:
	"""

	df_MCPFx, df_MCPFy, df_MCPFz = dim_force_dfs
	dataSize = df_MCPFx.shape[0]
	file = open(fOutput, "w")

	for case in range(0, dataSize // 2):
		for wheel in ["R" + axle, "L" + axle]: # Creates FR, FL, RR, RL as needed
			xField = df_MCPFx[wheel + "_Fx"][case]
			yField = df_MCPFy[wheel + "_Fy"][case]
			zField = df_MCPFz[wheel + "_Fz"][case]
			print("Running: " + wheel + "; Case: ", case + 1)
			print("x:", xField)
			print("y:", yField)
			print("z:", zField, "\n")


			### Enter dim data ###

			# x
			keyboard.send("x")
			sleep(.5)
			keyboard.write(xField.to_eng_string())
			sleep(.5)
			keyboard.send("enter")

			# y

			keyboard.send("y")
			sleep(.5)
			keyboard.write(yField.to_eng_string())
			sleep(.5)
			keyboard.send("enter")

			# z

			keyboard.send("z")
			sleep(.5)
			keyboard.write(zField.to_eng_string())
			sleep(.5)
			keyboard.send("enter")

			for i in range(4):
				keyboard.send("c")
				sleep(.5)
				keyboard.send("f")
				sleep(1)
				keyboard.send("ctrl+a")
				sleep(.5)
				OpenClipboard()
				data = GetClipboardData()

				# removes the \r char, which writelines adds again
				data = data.split("\r")
				CloseClipboard()

				# Produces chinese characters at the end of clipboard; truncate at 24
				file.writelines(data[:24])
				file.write("\n")
				keyboard.send("enter")
				sleep(.5)

			keyboard.send("c")


		sleep(1)
		# Run another case?
		keyboard.send("y")

		sleep(.5)
		print("Complete", wheel, "run", case)

	# For the second half of the data set, all x values go into the A field instead
	for case in range(dataSize // 2, dataSize):
		for wheel in ["R" + axle, "L" + axle]: # Creates FR, FL, RR, RL as needed
			aField = df_MCPFx[wheel + "_Fx"][case]
			yField = df_MCPFy[wheel + "_Fy"][case]
			zField = df_MCPFz[wheel + "_Fz"][case]
			print("Running: " + wheel + "; Case: ", case + 1)
			print("a:", aField)
			print("y:", yField)
			print("z:", zField, "\n")


			### Enter dim data ###

			# a
			keyboard.send("a")
			sleep(.5)
			keyboard.write(aField.to_eng_string())
			sleep(.5)
			keyboard.send("enter")

			# y

			keyboard.send("y")
			sleep(.5)
			keyboard.write(yField.to_eng_string())
			sleep(.5)
			keyboard.send("enter")

			# z

			keyboard.send("z")
			sleep(.5)
			keyboard.write(zField.to_eng_string())
			sleep(.5)
			keyboard.send("enter")

			for i in range(4):
				keyboard.send("c")
				sleep(.5)
				keyboard.send("f")
				sleep(1)
				keyboard.send("ctrl+a")
				sleep(.5)
				OpenClipboard()
				data = GetClipboardData()

				# removes the \r char, which writelines adds again
				data = data.split("\r")
				CloseClipboard()

				# Produces chinese characters at the end of clipboard; truncate at 24
				file.writelines(data[:24])
				file.write("\n")
				keyboard.send("enter")
				sleep(.5)

			keyboard.send("c")

		sleep(1)
		# Run another case?
		keyboard.send("y")

		sleep(.5)
		print("Complete run", case + 1)

	file.close()

def macroQuit():
	sleep(.5)
	keyboard.send("q")
	sleep(.5)
	keyboard.send("q")
	sleep(.5)
	keyboard.send("n")
	sleep(.5)
	keyboard.send("y")
	sleep(.5)
	keyboard.write("exit")
	sleep(.5)
	keyboard.send("enter")

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
	print("Friction_Circle_F26.py\n")

	loadCases = int(input("Number of load cases to distribute evenly on the "
						  "range [0, pi], inclusive on both ends. \n"
						  "Enter # Load cases: "))
	#
	fullDF= createDataframe(Car("carConfig.txt"), loadCases)
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
