from decimal import Decimal
import decimal
from path_reader import PathCollection
from numpy import float64
import math

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

		# setting determines whether Mitchell's uses Force at Axle or X Axis Force
		# for first half of rear axle input. If True, uses X Axis Force
		# Setting is based on user input during program startup by request.
		self.use_outboard_breaks = None

		print("Parsed car data from config: ", cfg)

	@staticmethod
	def ParamsFromConfig(cfg):
		"""
		Draws initial car parameters from a config file, whose path is given
		by cfg. Any additional parameters will need to be hardcoded in here
		:param cfg: string path to config file
		:return: 4-tuple of values produced in this function
		"""
		params = {}
		for line in open(cfg):
			if line.startswith("#") or line == "\n":
				continue  # Skip comments and empty lines
			param, value = map(str.strip, line.split("="))
			params[param] = float64(value)
		CG = params["CG"]
		WB = params["WB"]
		TW = params["TW"]
		params["Long_WT"] = float64(CG / WB)
		params["Lat_WT"] = float64(CG / TW)
		return params

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

def init(pathConfigFile):
	"""
	Initializes the PathCollection and Car objects, and sets up the context
	variable for the decimal library to use the correct precision and rounding
	rules (global)
	:param configFile: filepath to the config file storing all of the filepaths
	:return: 2-tuple, with the Car object as the first element, and the PathCollection
	as the second element.
	"""

	# # Get the decimal library's context object
	# decimal_context = decimal.getcontext()
	#
	# # Set the decimal library's precision to 20 places
	# decimal_context.prec = 15
	#
	# # set rounding to work like most people use it
	# decimal_context.rounding = decimal.ROUND_HALF_UP

	# load the PathCollection object with filepaths to use.
	paths = PathCollection(pathConfigFile)

	# Grab the car config file from the paths and use it to create a new Car
	car = Car(paths.car_config_path)

	return car, paths