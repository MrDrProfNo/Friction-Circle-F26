import os
## Constants (all defaults)
OUTPUT_FOLDER_PATH = "./Friction_Circle_F26_Output/"
CAR_CONFIG_FILE = "car_config.txt"

MITCHELL_COPY_OUTPUT_F = "tmpF.txt"
MITCHELL_COPY_OUTPUT_R = "tmpR.txt"

PARSED_OUTPUT_F = "FOutput.txt"
PARSED_OUTPUT_R = "ROutput.txt"

DUMP_EXCEL_OUTPUT = "dump.xlsx"
FORMAT_EXCEL_OUTPUT = "formatting.xlsx"
PARSED_EXCEL_OUTPUT = "Parsed_Forces.xlsx"

VDOSPLUS_PATH = '.\Suspension Project\vDosPlus\vDosPlus.exe'


## Constants (attribute names)
OUTPUT_FOLDER_ATTR = "output_folder"
CAR_CONFIG_PATH_ATTR = "car_config_path"
DUMP_EXCEL_PATH_ATTR = "dump_excel_path"
FORMAT_EXCEL_PATH_ATTR = "format_excel_path"
PARSED_EXCEL_ATTR = "parsed_excel_path"
TEMP_FRONT_ATTR = "temp_front"
TEMP_REAR_ATTR = "temp_rear"
FRONT_PARSED_ATTR = "front_parsed"
REAR_PARSED_ATTR = "rear_parsed"
VDOSPLUS_PATH_ATTR = "VDosPlus_path"

FRONT_AXLE_INST_ATTR = "front_axle_instructions"
REAR_AXLE_INST_ATTR = "rear_axle_instructions"

class PathCollection:

	def __init__(self, configFile):
		"""
		The constructor for PathCollection has extensive responsibilities;
		all of the individual filepaths are constructed here. If the filepath is
		missing a path, the user will be given the option to use defaults.

		:param configFile: filepath to config file that all other paths will be read
		from
		"""
		expectedAttr = [OUTPUT_FOLDER_ATTR, CAR_CONFIG_PATH_ATTR, DUMP_EXCEL_PATH_ATTR,
						FORMAT_EXCEL_PATH_ATTR, PARSED_EXCEL_ATTR, TEMP_FRONT_ATTR,
						TEMP_REAR_ATTR, FRONT_PARSED_ATTR, REAR_PARSED_ATTR,
						VDOSPLUS_PATH_ATTR, FRONT_AXLE_INST_ATTR, REAR_AXLE_INST_ATTR]

		# declare empty dictionary for the path
		pathDict = {}

		# initialize all elements to their defaults

		missedAttr = self.parseFile(configFile, pathDict, expectedAttr)

		# if any attributes are missing
		if( len(missedAttr) > 0 ):

			print("The following filepaths were not provided: ")
			for attr in missedAttr:
				print(attr)

			while(True):
				useDefaults = input(
					"Do you want to use the defaults for any missing"
					" fields (Y/N). N will quit the program.")

				if(useDefaults.lower() == "n" or # n or no answered
							useDefaults.lower() == "no"):

					raise ValueError(" Failed to find values for some attributes,",
								   "Quit requested by user")

				elif(not (useDefaults.lower() == "y" or # not y or yes
							  useDefaults.lower() == "yes") ):
					print("Unrecognized answer. Try again?\n")
					continue
				else: # y or yes answered
					for attr in missedAttr:
						pathDict[attr] = self.defaultValue(attr)
					break # exit the input request loop and set values

		self.output_folder = pathDict[OUTPUT_FOLDER_ATTR]

		self.output_folder = self.output_folder.strip(r"\/.")

		if( not os.path.exists(self.output_folder) ):
			try:
				os.makedirs(self.output_folder)
			except OSError:
				print("Error in makedirs(", self.output_folder, ")", sep="")
				raise


		self.car_config_path = pathDict[CAR_CONFIG_PATH_ATTR]

		self.dump_excel_path = pathDict[DUMP_EXCEL_PATH_ATTR]

		self.format_excel_path = pathDict[FORMAT_EXCEL_PATH_ATTR]

		self.parsed_excel_path = pathDict[PARSED_EXCEL_ATTR]

		self.temp_front = pathDict[TEMP_FRONT_ATTR]

		self.temp_rear = pathDict[TEMP_REAR_ATTR]

		self.front_parsed = pathDict[FRONT_PARSED_ATTR]

		self.rear_parsed = pathDict[REAR_PARSED_ATTR]

		self.VDosPlus_path = pathDict[VDOSPLUS_PATH_ATTR]

		self.front_axle_inst = pathDict[FRONT_AXLE_INST_ATTR].replace(" ", "").split(",")

		self.rear_axle_inst = pathDict[REAR_AXLE_INST_ATTR].replace(" ", "").split(",")

		print("Successfully parsed filepaths from file:", configFile)



	def parseFile(self, configFile, pathDict, expectedAttr):
		"""
		Reads the contents of configFile, assuming they are of the correct format,
		and puts them into the dictionary, mapping the attribute to the value

		If the attribute does not match one of the values in expectedInputs, a
		warning is printed to the console, but no action is taken.

		:param configFile: File to read path attributes from
		:param pathDict: dictionary to store the paths in
		:param expectedAttr: list of expected attribute inputs
		:return:
		"""

		foundAttr = []

		with open(configFile, "r+") as file:
			for line in file:

				if(line == "\n"):
					continue
				elif(line[0] == '#'):
					continue
				else:

					line = line.strip().split("=")
					if(not line[0] in expectedAttr):
						print("Encountered unexpected path attribute in",
							  "path_config.txt:", line[0], "; this attribute may",
							  "not be used")
					else:
						pathDict[ line[0] ] = line[1]
						foundAttr.append(line[0])

		missedAttr = []
		for attr in expectedAttr:
			if(not attr in foundAttr):
				missedAttr.append(attr)

		return missedAttr

	def defaultValue(self, key):
		"""
		Given one of the attribute keys, returns the default value associated
		with it
		:param key: pathdict key connected to a default value
		:return: the default value associated with key
		"""
		key = str(key).replace("\'", "")

		if(key == OUTPUT_FOLDER_ATTR):
			return OUTPUT_FOLDER_PATH
		elif(key == CAR_CONFIG_PATH_ATTR):
			return CAR_CONFIG_FILE
		elif(key == DUMP_EXCEL_PATH_ATTR):
			return DUMP_EXCEL_OUTPUT
		elif(key == FORMAT_EXCEL_PATH_ATTR):
			return FORMAT_EXCEL_OUTPUT
		elif(key == PARSED_EXCEL_ATTR):
			return PARSED_EXCEL_OUTPUT
		elif(key == TEMP_FRONT_ATTR):
			return MITCHELL_COPY_OUTPUT_F
		elif(key == TEMP_REAR_ATTR):
			return MITCHELL_COPY_OUTPUT_R
		elif(key == FRONT_PARSED_ATTR):
			return PARSED_OUTPUT_F
		elif(key == REAR_PARSED_ATTR):
			return PARSED_OUTPUT_R
		elif(key == VDOSPLUS_PATH_ATTR):
			return VDOSPLUS_PATH
		elif(key == FRONT_AXLE_INST_ATTR):
			raise ValueError("Unable to provide a default value for attribute:",
							 FRONT_AXLE_INST_ATTR)
		elif(key == FRONT_AXLE_INST_ATTR):
			raise ValueError("Unable to provide a default value for attribute:",
							 REAR_AXLE_INST_ATTR)
		else:
			raise ValueError("Unrecognized attribute passed to PathCollection.defaultValue()")