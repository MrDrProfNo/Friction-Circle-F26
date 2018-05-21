from decimal import Decimal # special import because I hate writing decimal.Decimal
import decimal				# But want to keep the decimal reference for readability
from path_reader import PathCollection


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

		print("Parsed car data from config: ", cfg)

	@staticmethod
	def ParamsFromConfig(cfg):
		"""
		Draws initial car parameters from a config file, whose path is given
		by cfg. Any additional parameters will need to be hardcoded in here
		:param cfg: string path to config file
		:return:
		"""
		params = {}
		for line in open(cfg):
			if line.startswith("#") or line == "\n":
				continue  # Skip comments and empty lines
			param, value = map(str.strip, line.split("="))
			params[param] = Decimal(value)
		CG = params["CG"]
		WB = params["WB"]
		TW = params["TW"]
		params["Long_WT"] = Decimal(CG / WB)
		params["Lat_WT"] = Decimal(CG / TW)
		return params

	@staticmethod
	def secondaryParams(params):
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

def init(pathConfigFile):
	"""
	Initializes the PathCollection and Car objects, and sets up the context
	variable for the decimal library to use the correct precision and rounding
	rules (global)
	:param configFile: filepath to the config file storing all of the filepaths
	:return: 2-tuple, with the Car object as the first element, and the PathCollection
	as the second element.
	"""

	# Get the decimal library's context object
	decimal_context = decimal.getcontext()

	# Set the decimal library's precision to 20 places
	decimal_context.prec = 15

	# set rounding to work like most people use it
	decimal_context.rounding = decimal.ROUND_HALF_UP

	# load the PathCollection object with filepaths to use.
	paths = PathCollection(pathConfigFile)

	# Grab the car config file from the paths and use it to create a new Car
	car = Car(paths.car_config_path)

	return car, paths