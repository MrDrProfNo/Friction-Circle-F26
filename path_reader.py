
## Constants (all defaults)
OUTPUT_FOLDER_PATH = "./Friction_Circle_F26_Output/"
CAR_CONFIG_FILE = "car_config.txt"
PATH_CONFIG_FILE = "path_config.txt"

MITCHELL_COPY_OUTPUT_F = "tmpF.txt"
MITCHELL_COPY_OUTPUT_R = "tmpR.txt"

PARSED_OUTPUT_F = "FOutput.txt"
PARSED_OUTPUT_R = "ROutput.txt"

DUMP_EXCEL_OUTPUT = "dump.xlsx"
FORMAT_EXCEL_OUTPUT = "formatting.xlsx"
PARSED_EXCEL_OUTPUT = "Parsed_Forces.xlsx"

VDOSPLUS_PATH = '.\Suspension Project\vDosPlus\vDosPlus.exe'

class PathCollection:

	def __init__(self, configFile):

		expectedAttr = ["output_folder", "car_config_path", "dump_excel_path",
						"format_excel_path", "parsed_excel_path", "temp_front",
						"temp_rear", "front_parsed", "rear_parsed",
						"VDosPlus_path"]

		# declare empty dictionary for the path
		pathDict = {}

		# initialize all elements to their defaults

		for attr in expectedAttr:
			pathDict[attr] = self.defaultValue(attr)

		missedAttr = self.parseFile(configFile, pathDict, expectedAttr)

		# if any attributes are missing
		if( len(missedAttr) > 0 ):
			while(True):
				useDefaults = input(
					"Do you want to use the defaults for any missing"
					" fields (Y/N). N will quit the program.")

				if (useDefaults.lower() == "n" or # n or no answered
							useDefaults.lower() == "no"):

					raise ValueError(" Failed to find values for some attributes,",
								   "Quit requested by user")

				elif (not (useDefaults.lower() == "y" or # not y or yes
							  useDefaults.lower() == "yes") ):
					print("Unrecognized answer. Try again?\n")
					continue
				else: # y or yes answered
					break # exit the input request loop and set values

		self.output_folder = pathDict["output_folder"]
		self.car_config_path = pathDict["car_config_path"]
		self.dump_excel_path = pathDict["dump_excel_path"]
		self.format_excel_path = pathDict["format_excel_path"]
		self.parsed_excel_path = pathDict["parsed_excel_path"]
		self.temp_front = pathDict["temp_front"]
		self.temp_rear = pathDict["temp_rear"]
		self.front_parsed = pathDict["front_parsed"]
		self.rear_parsed = pathDict["rear_parsed"]
		self.VDosPlus_path = pathDict["VDosPlus_path"]

		print("Parsed filepaths from file:", configFile)



	def parseFile(self, configFile, pathDict, expectedInputs):
		"""
		Reads the contents of configFile, assuming they are of the correct format,
		and puts them into the dictionary, mapping the attribute to the value

		If the attribute does not match one of the values in expectedInputs, a
		warning is printed to the console, but no action is taken.

		:param configFile: File to read path attributes from
		:param pathDict: dictionary to store the paths in
		:param expectedInputs: list of expected attribute inputs
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
					if( not line[0] in expectedInputs ):
						print("Encountered unexpected path attribute in",
							  "path_config.txt:", line[0], "; this attribute may",
							  "not be used")
					else:
						pathDict[ line[0] ] = line[1]
						foundAttr.append(line[0])

		missedAttr = []
		for attr in expectedInputs:
			if(not attr in foundAttr):
				missedAttr.append(attr)

		return missedAttr

	def defaultValue(self, key):
		key = str(key).replace("\'", "")

		if(key == "output_folder"):
			return OUTPUT_FOLDER_PATH
		elif(key == "car_config_path"):
			return CAR_CONFIG_FILE
		elif(key == "dump_excel_path"):
			return DUMP_EXCEL_OUTPUT
		elif(key == "format_excel_path"):
			return FORMAT_EXCEL_OUTPUT
		elif(key == "parsed_excel_path"):
			return PARSED_EXCEL_OUTPUT
		elif(key == "temp_front"):
			return MITCHELL_COPY_OUTPUT_F
		elif(key == "temp_rear"):
			return MITCHELL_COPY_OUTPUT_R
		elif(key == "front_parsed"):
			return PARSED_OUTPUT_F
		elif(key == "rear_parsed"):
			return PARSED_OUTPUT_R
		elif(key == "VDosPlus_path"):
			return VDOSPLUS_PATH
		else:
			raise ValueError("Unrecognized attribute passed to PathCollection.defaultValue()")