from time import sleep
from win32clipboard import OpenClipboard, CloseClipboard, GetClipboardData

import win32gui as wg
import keyboard
import os

from decimal import Decimal


STANDARD_DELAY = .75

def macroMain(dim_force_dfs, paths, car):
	"""
	Runs the macro for Racing by the Numbers, inputting data drawn from the
	partial dataframes. dim_force_dfs must be a 3-tuple of Dataframes, otherwise
	there will be problems.

	The steps to reach the config files is hardcoded below. Directional instructions
	followed by "enter" will select a file; just give the directions needed to
	reach the correct file.

	:param dim_force_dfs:
	:param paths
	:return:
	"""



	# these files get appended to. If they are not deleted, old data will be used before new data. And that'll just be a mess.
	try:
		os.remove(paths.temp_front)
	except: #yes, this is bad practice, but I don't know what error it throws and don't care.
		pass

	try:
		os.remove(paths.temp_rear)
	except:
		pass



	df_MCPFx, df_MCPFy, df_MCPFz = dim_force_dfs
	dataSize = df_MCPFx.shape[0] # use values relative to this to select indices within the dim_force dataframes

	sleep(4)

	macroSetup(paths.front_axle_inst)

	### macroRunAxle usage ###
	# First, pass in the 3D dimensional force dataframes. Then tell it an axle
	# - "F" or "R" for Front and Rear respectively. Then give it an output file.
	# The next 2 arguments are the start and stop indices within the dataframes
	# which are to be used. 0 is the first element, dataSize is the last (range
	# used will ignore the final index, so passing 0 and dataSize will grab data
	# from index 0 to index dataSize - 1)
	# For example, to give the halfway point, use:
	#   dataSize // 2
	# where // is the integer division operator.
	# The final argument is True or False - whether or not to use the 'a' button
	# when entering the X dimension forces.
	# This is a copy of the docstrings for the method, the most up-to-date
	# instructions will be available there.

	macroRunAxle(dim_force_dfs, "F", paths.temp_front, 0, dataSize // 2, False)
	macroRunAxle(dim_force_dfs, "F", paths.temp_front, dataSize // 2, dataSize, True)

	# The steps to quit, except say "no" when asked if finished with the program
	keyboard.send("q")
	keyboard.send("q")
	keyboard.send("n")
	keyboard.send("n")

	# Setup with the rear profile
	macroSetup(paths.rear_axle_inst)
	if car.use_outboard_breaks:
		macroRunAxle(dim_force_dfs, "R", paths.temp_rear, 0, dataSize // 2, False)
	else:
		macroRunAxle(dim_force_dfs, "R", paths.temp_rear, 0, dataSize // 2, True)

	macroRunAxle(dim_force_dfs, "R", paths.temp_rear, dataSize // 2, dataSize, True)

	macroQuit()



def macroSetup(configSteps):
	"""
	Assumes that VDosPlus is open with Mitchell's on its start screen.

	Pulls VDosPlus to the front of the screen, making it the active window, and
	runs through the commands required to select a config from the menu

	:param configSteps: Array of Strings, the steps to select the desired profile
						using the arrow keys
	"""
	# Should be "vdosplus", may change when testing
	wg.EnumWindows(pullToFront, "vdosplus")
	sleep(1)
	keyboard.send("enter")
	sleep(STANDARD_DELAY)
	for step in configSteps:
		if step == "":
			continue
		keyboard.send(step)
		sleep(STANDARD_DELAY)
	sleep(STANDARD_DELAY)
	keyboard.send("enter")
	sleep(STANDARD_DELAY)
	keyboard.send("enter")
	sleep(STANDARD_DELAY)
	keyboard.send("x")
	sleep(STANDARD_DELAY)
	keyboard.send("f")
	sleep(3)

def macroRunAxle(dim_force_dfs, axle, outputFile, dataRangeStart, dataRangeEnd, useAxleForce):
	"""
	Run the macro for the front or rear axle of the car (requires different
	configs in Mitchell). Takes the passed 3-tuple of dataframes, which contain
	the x, y, z values respectively for each wheel (so Front-rightx, front-leftx
	rear-rightx, rear-leftx) and inputs them into mitchell, appending the output to
	a file.

	The dataRange____ arguments are the start and stop indices within the dataframes
	which are to be used. 0 is the first element, dataSize is the last (range
	used will ignore the final index, so passing 0 and dataSize will grab data
	from index 0 to index dataSize - 1)
	For example, to give the halfway point, use:
		dataSize // 2
	where // is the integer division operator.
	The final argument is True or False - whether or not to use the 'a' button
	when entering the X dimension forces.
	This is a copy of the docstrings for the method, the most up-to-date
	instructions will be available there.

	:param dim_force_dfs: 3-tuple of DFs containing the x, y, z forces acting on
						the wheels, as specified above.
	:param axle: "F" or "R" for front or rear respectively
	:param outputFile: Filepath to send front output file to
	:param dataRangeStart: integer to begin running data at within the dim_force_dfs
	:param dataRangeEnd: integer to stop running data before within the dim_force_dfs
		(value is used in a range object, which is not end inclusive.
	:return:
	"""


	df_MCPFx, df_MCPFy, df_MCPFz = dim_force_dfs
	file = open(outputFile, "a")

	for case in range(dataRangeStart, dataRangeEnd):
		for wheel in ["R" + axle, "L" + axle]: # Creates FR, FL RR, RL as needed

			# simple using <dataframe>[index1][index2] causes it to try and
			# use the case number (position) as the dataframe index (associated label)
			# which results in the second case (position 1) using the values for
			# the last case (associated label "1")
			xField = df_MCPFx[wheel + "_Fx"].iloc[case]
			yField = df_MCPFy[wheel + "_Fy"].iloc[case]
			zField = df_MCPFz[wheel + "_Fz"].iloc[case]
			print("Running: " + wheel + "; Case: ", case + 1)

			if(yField < Decimal(.5) and yField > Decimal(-.5)):
				yField = Decimal(0)

			if useAxleForce:
				print("a:", xField)
			else:
				print("x:", xField)
			print("y:", yField)
			print("z:", zField)


			### Enter dim data ###

			# x
			if(useAxleForce): # instructed to use X at Axle field instead of X field
				keyboard.send("a")
			else:
				keyboard.send("x")

			sleep(STANDARD_DELAY)
			keyboard.write(str(xField))
			sleep(STANDARD_DELAY)
			keyboard.send("enter")
			sleep(STANDARD_DELAY)

			# y

			keyboard.send("y")
			sleep(STANDARD_DELAY)
			keyboard.write(str(yField))
			sleep(STANDARD_DELAY)
			keyboard.send("enter")
			sleep(STANDARD_DELAY)

			# z

			keyboard.send("z")
			sleep(STANDARD_DELAY)
			keyboard.write(str(zField))
			sleep(STANDARD_DELAY)
			keyboard.send("enter")
			sleep(STANDARD_DELAY)

			for i in range(4):
				keyboard.send("c")
				sleep(STANDARD_DELAY)
				keyboard.send("f")
				sleep(1)
				keyboard.send("ctrl+a")
				sleep(STANDARD_DELAY)
				OpenClipboard()
				data = GetClipboardData()

				# removes the \r char, which writelines adds again
				data = data.split("\r")
				CloseClipboard()

				# Produces chinese characters at the end of clipboard; truncate at 24
				file.writelines(data[:24])
				file.write("\n")
				keyboard.send("enter")
				sleep(STANDARD_DELAY)

			keyboard.send("c")
			print("Complete", wheel, "run", case + 1, "\n")

		sleep(1)
		# Run another case?
		keyboard.send("y")

		sleep(STANDARD_DELAY)



	file.close()

def macroQuit():
	"""
	Assumes that VDosPlus is running, and the active window, and that Mitchell
	is on the blue screen asking if the user wants to enter more information

	Executes the combination of keypresses required to quit the program from
	this position (includes closing vDosPlus)
	:return:
	"""
	sleep(STANDARD_DELAY)
	keyboard.send("q")
	sleep(STANDARD_DELAY)
	keyboard.send("q")
	sleep(STANDARD_DELAY)
	keyboard.send("n")
	sleep(STANDARD_DELAY)
	keyboard.send("y")
	sleep(STANDARD_DELAY)
	keyboard.write("exit")
	sleep(STANDARD_DELAY)
	keyboard.send("enter")


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
		windowText = wg.GetWindowText(handle)
		window = wg.FindWindow(None, windowText)
		if (windowName in windowText.lower()):
			# Sends an alt keypress. For some reason, SetForegroundWindow throws an error
			# with message 'no error message is available' unless alt is pressed right before
			# it. I don't understand, I don't need to understand. Just leave it be.
			keyboard.send('alt')
			wg.SetForegroundWindow(window)
	elif (windowName in handle[1].lower()):
		# Sends an alt keypress. For some reason, SetForegroundWindow throws an error
		# with text 'no error message is available' unless alt is pressed right before
		# it. I don't understand, I don't need to understand. Just leave it be.
		keyboard.send('alt')
		wg.SetForegroundWindow(handle)