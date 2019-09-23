from numpy import float64
import numpy
from pandas import DataFrame

import math as m


def createDataframe(car, loadCases):
	"""

	:param car: Car object containing data for the car
	:param loadCases: Number of loadcases to run with; should be int, checked
					internally
	:return: Dataframe containing the calculated values in a dictionary
	"""

	sParams = secondaryParams(car)

	# Error checking with more descriptive crash errors.
	if (not isinstance(loadCases, int)):
		raise TypeError("number of load cases must be of type int")


	elif (loadCases <= 0):
		raise ValueError("number of load cases must be greater than 0")

	# dictionary to store all of the calculations. Order is irrelevant, but
	# all keys must match the strings in columns array below.
	datadict = {          'r_theta':	[],	'XG':	 	[],	'YG':		[],
				'RF_Fz':	[],	'LF_Fz': 	[],     'RR_Fz':	[],
				'LR_Fz': 	[],	'LF_Mu_x':	[],	'RF_Mu_x':	[],
				'LR_Mu_x':	[],	'RR_Mu_x':	[],	'LF_Mu_y':	[],
				'RF_Mu_y':	[],	'LR_Mu_y':	[],	'RR_Mu_y':	[],
				'LF_Fx':	[],	'RF_Fx':	[],	'LR_Fx':	[],
				'RR_Fx':	[],	'Fx':		[],	'LoG':		[],
				'LF_Fy':	[],	'RF_Fy':	[],	'LR_Fy':	[],
				'RR_Fy':	[],	'Fy':		[],     'LaG':		[],
				'LF_c':		[],     'RF_c':		[],     'LR_c':		[],
				'RR_c':		[]}

	# all values of theta coefficient that calculations are run for [0, 1]
	theta_coef_all = []

	columns = ["r_theta", 	"XG", 		"YG",		"LF_Fz",	"RF_Fz",	"LR_Fz",
			"RR_Fz",	"LF_Mu_x", 	"RF_Mu_x", 	"LR_Mu_x", 	"RR_Mu_x",	"LF_Mu_y",
			"RF_Mu_y", 	"LR_Mu_y", 	"RR_Mu_y",	"LF_Fx", 	"RF_Fx", 	"LR_Fx",
			"RR_Fx", 	"Fx", 		"LoG",		"LF_Fy", 	"RF_Fy", 	"LR_Fy",
			"RR_Fy", 	"Fy", 		"LaG",		"LF_c", 	"RF_c", 	"LR_c",
			"RR_c"]

	# Load case 0 is always included
	theta_coef_all.append(float64(0))

	# Generate list of all theta coefficients
	for case in range(1, loadCases + 1):  # endpoint will be loadcases

		# dividing by loadcases ensures we're on range [0, 1];
		theta_coef = float64(case / loadCases)

		# quantize rounds it at the specified digit (10th place currently)
		theta_coef = float64(numpy.around(theta_coef, 10))
		if (theta_coef == float64(.5)):
			# Special case for theta coef .5 to avoid division by 0 error
			theta_coef_all.append(theta_coef - (theta_coef / 1000))
			theta_coef_all.append(theta_coef + (theta_coef / 1000))
			continue

		# Put the theta coefficient for this case into the array
		theta_coef_all.append(theta_coef)



	# run calculations for all values of theta
	for coef in theta_coef_all:
		calculateForCaseN(datadict, car, sParams, coef)


	df = DataFrame(data=datadict, index=theta_coef_all, columns=columns)

	return df


def secondaryParams(car):
	"""
	Generates the secondary set of constant parameters based on those read
	from the config file.
	:param params: params dictionary produced by ParamsFromConfig
	:return: tuple containing variables a, b, Fz_f, Fz_r (Max Long Accel,
			Max Lat Accel, Front Static Corner weight, Rear Static Corner
			weight)
	"""

	W_d = car.W_d
	M = car.M
	D = car.D
	A = car.A
	A_d = car.A_d

	# Friction values based on tire model from F27 Vehicle Dynamics Group
	e = float64(m.e)

	# Longitudinal Mu coeff.
	C1Long = float64(3.0343)
	C2Long = float64(-0.0017)

	# Lateral Mu coeff.
	C1Lat = float64(-.285)
	C2Lat = float64(3.6211)

	# Max Normal force for lateral mu before latdefault is used rather than equation
	maxFn = 224

	# In order for math-related operations to work, float64 cannot be
	# multiplied by a float. Separate float64s are kept around for pi

	Fz_f = float64((W_d * (M + D)) / 2)  # Front Static Corner weight
	Fz_r = float64(((1 - W_d) * (M + D)) / 2)  # Rear Static Corner weight

	Fr_A_R = float64(
		Fz_f + ((A * A_d) / 2))  # Front Right Normal Force with aero
	Fr_A_L = float64(
		Fz_f + ((A * A_d) / 2))  # Front Left Normal Force with aero
	Re_A_R = float64(
		Fz_r + ((A * (1 - A_d)) / 2))  # Rear Right Normal Force with aero
	Re_A_L = float64(
		Fz_r + ((A * (1 - A_d)) / 2))  # Rear Normal Force with aero

	Mux_f_R = C1Long * e ** (
		abs(Fr_A_R) * C2Long)  # Front Right Mu_x (longitudinal)
	Mux_f_L = C1Long * e ** (
		abs(Fr_A_L) * C2Long)  # Front Left	Mu_x (longitudinal)
	Mux_r_R = C1Long * e ** (
		abs(Re_A_R) * C2Long)  # Rear Right Mu_x (longitudinal)
	Mux_r_L = C1Long * e ** (
		abs(Re_A_L) * C2Long)  # Rear Left Mu_x (longitudinal)

	Muy_f_R = (
		C1Lat * float64(numpy.log(abs(Fr_A_R))) + C2Lat) # Front Right Mu_y (lateral)
	Muy_f_L = (
		C1Lat * float64(numpy.log(abs(Fr_A_L))) + C2Lat) # Rear Right Mu_y (lateral)
	Muy_r_R = (
		C1Lat * float64(numpy.log(abs(Re_A_R))) + C2Lat) # Front Left Mu_y (lateral)
	Muy_r_L = (
		C1Lat * float64(numpy.log(abs(Re_A_L))) + C2Lat) # Rear Left Mu_y (lateral)

	Fr_Fx = (Mux_f_R * Fr_A_R) + (
		Mux_f_L * Fr_A_L)  # Front Cornering Force (x) [left and right combined]
	Fr_Fy = (Muy_f_R * Fr_A_R) + (
		Muy_f_L * Fr_A_L)  # Front Cornering Force (y) [left and right combined]
	Re_Fx = (Mux_r_R * Re_A_R) + (
		Mux_r_L * Re_A_L)  # Rear Cornering Force (x) [left and right combined]
	Re_Fy = (Muy_r_R * Re_A_R) + (
		Muy_r_L * Re_A_L)  # Rear Cornering Force (y) [left and right combined]

	Total_x = Fr_Fx + Re_Fx  # Total X Cornering Force
	Total_y = Fr_Fy + Re_Fy  # Total Y Cornering Force

	a = Total_x / (M + D)  # Max Long Accel
	b = Total_y / (M + D)  # Max Lat Accel

	print("Maximum theoretical longitudinal acceleration is:", a)
	print("Maximum theoretical lateral acceleration is:", b)

	return a, b, Fz_f, Fz_r


def calculateForCaseN(datadict, car, sParams, n):
	"""
	Runs calculations for all values for the given theta-coefficient n. Uses
	default values for the Car as given by the car object, which should have read
	them from car_config.txt

	Some values require division by cos(n * pi). In the .5 case, this evaluates
	to zero. Such cases are substituted with a value extremely close to n.

	The passed datadict MUST contain all of the expected keys, or the code WILL
	crash. This function will add data directly to it, assuming that the keys
	exist. Workaround is pending.

	:param datadict: dictionary mapping the expected key set to float64 values
	:param car: Car object with car-related variables initialized
	:param n: current theta-coefficient, which corresponds to a load case.
	"""

	# float64 variants of all frequently used math library tools;
	# these should be subbed into the code where needed
	# instead of running float64 conversions every time.
	pi = float64(m.pi)
	cosNPi = float64(m.cos(n * pi))
	sinNPi = float64(m.sin(n * pi))


	# define variables for car constants to make code easier to read
	a = sParams[0]
	b = sParams[1]
	Fz_f = sParams[2]
	Fz_r = sParams[3]
	M = car.M
	D = car.D
	Long_WT = car.Long_WT
	Lat_WT = car.Lat_WT
	A = car.A
	A_d = car.A_d

	### More constants for the Mu... calculations ###
	e = float64(m.e)
	C1Long = float64(3.0343)
	C2Long = float64(-.0017)

	C1Lat = float64(-.285)
	C2Lat = float64(3.6211)

	# Calculation of contact patch forces using an ellipse shape to transition from pure longitudinal to pure lateral acceleration peaks and everywhere in between
	# X is longitudinal and Y is lateral

	# Maximum lateral and longitudinal values transcribed on an ellipse which are used later for generating a scaling value for mu values:

	YG_max = (a * b) / float64(
		m.sqrt((b * float64(m.cos(0.49 * m.pi))) ** 2 + \
				((a * float64(m.sin(0.49 * m.pi)))) ** 2)) * \
			 	float64(m.sin(0.49 * m.pi))

	XG_max = -((a * b) / float64(m.sqrt(b ** 2)))

	# The main calculations to calculate contact patch forces

	# Translastes max long and lat accelerations to an ellipse
	r_theta_n = (a * b) / float64(
		m.sqrt(((b * cosNPi) ** 2 + ((a * sinNPi)) ** 2))
	)

	# Obtains X and Y component of ellipse
	XG_n = -(r_theta_n * cosNPi)
	YG_n = r_theta_n * sinNPi

	# Calculates Normal Force on Each Tire using Static loading, load (weight) transfer (WT), and aero forces
	RF_Fz_n = Fz_f + (((M + D) * (-Long_WT * XG_n)) / 2) + (
		((M + D) * (-Lat_WT * YG_n)) / 2) + ((A * A_d) / 2)

	LF_Fz_n = Fz_f + (((M + D) * (-Long_WT * XG_n)) / 2) + (
		((M + D) * (Lat_WT * YG_n)) / 2) + ((A * A_d) / 2)

	RR_Fz_n = Fz_r + (((M + D) * (Long_WT * XG_n)) / 2) + (
		((M + D) * (-Lat_WT * YG_n)) / 2) + ((A * (1 - A_d)) / 2)

	LR_Fz_n = Fz_r + (((M + D) * (Long_WT * XG_n)) / 2) + (
		((M + D) * (Lat_WT * YG_n)) / 2) + ((A * (1 - A_d)) / 2)

	# Longitudinal Mu calculations
	LF_Mu_x_n = (C1Long * e ** (abs(LF_Fz_n) * C2Long)) * (XG_n / XG_max)
	RF_Mu_x_n = (C1Long * e ** (abs(RF_Fz_n) * C2Long)) * (XG_n / XG_max)
	LR_Mu_x_n = (C1Long * e ** (abs(LR_Fz_n) * C2Long)) * (XG_n / XG_max)
	RR_Mu_x_n = (C1Long * e ** (abs(RR_Fz_n) * C2Long)) * (XG_n / XG_max)

	# Lateral Mu calculations

	LF_Mu_y_n = (C1Lat * float64(numpy.log(abs(LF_Fz_n))) + C2Lat) * (YG_n / YG_max)
	RF_Mu_y_n = (C1Lat * float64(numpy.log(abs(RF_Fz_n))) + C2Lat) * (YG_n / YG_max)
	LR_Mu_y_n = (C1Lat * float64(numpy.log(abs(LR_Fz_n))) + C2Lat) * (YG_n / YG_max)
	RR_Mu_y_n = (C1Lat * float64(numpy.log(abs(RR_Fz_n))) + C2Lat) * (YG_n / YG_max)

	# Calculates Longitudinal force on each tire
	LFX_n = -LF_Mu_x_n * LF_Fz_n
	RFX_n = -RF_Mu_x_n * RF_Fz_n
	LRX_n = -LR_Mu_x_n * LR_Fz_n
	RRX_n = -RR_Mu_x_n * RR_Fz_n

	# Calculates total car longitudinal force
	Fx_n = LFX_n + RFX_n + LRX_n + RRX_n

	# Calculates total longitudinal G's
	LoG_n = Fx_n / (M + D)

	# Calculates Lateral force on each tire
	LFY_n = LF_Mu_y_n * LF_Fz_n
	RFY_n = RF_Mu_y_n * RF_Fz_n
	LRY_n = LR_Mu_y_n * LR_Fz_n
	RRY_n = RR_Mu_y_n * RR_Fz_n

	# Calculates total car lateral force
	Fy_n = LFY_n + RFY_n + LRY_n + RRY_n

	# Calculates total lateral G's
	LaG_n = Fy_n / (M + D)

	# Calculates resultant force on each corner
	LF_c_n = float64(m.sqrt(LF_Fz_n ** 2 + LFX_n ** 2 + LFY_n ** 2))
	RF_c_n = float64(m.sqrt(RF_Fz_n ** 2 + RFX_n ** 2 + RFY_n ** 2))
	LR_c_n = float64(m.sqrt(LR_Fz_n ** 2 + LRX_n ** 2 + LRY_n ** 2))
	RR_c_n = float64(m.sqrt(RR_Fz_n ** 2 + RRX_n ** 2 + RRY_n ** 2))

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
