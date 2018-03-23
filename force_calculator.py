
from decimal import Decimal
from pandas import DataFrame

import math as m

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