from time import sleep
from win32clipboard import OpenClipboard, CloseClipboard, GetClipboardData

import win32gui as wg
import keyboard
from decimal import Decimal


STANDARD_DELAY = .75

def macroMain(dim_force_dfs, paths):
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


	sleep(4)

	macroSetup(paths.front_axle_inst)

	macroRunAxle(dim_force_dfs, "F", "tmpF.txt")

	# The steps to quit, except say "no" when asked if finished with the program
	keyboard.send("q")
	keyboard.send("q")
	keyboard.send("n")
	keyboard.send("n")

	# Setup with the rear profile
	macroSetup(paths.rear_axle_inst)

	macroRunAxle(dim_force_dfs, "R", "tmpR.txt")

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
			sleep(STANDARD_DELAY)
			keyboard.write(xField.to_eng_string())
			sleep(STANDARD_DELAY)
			keyboard.send("enter")
			sleep(STANDARD_DELAY)

			# y

			keyboard.send("y")
			sleep(STANDARD_DELAY)
			keyboard.write(yField.to_eng_string())
			sleep(STANDARD_DELAY)
			keyboard.send("enter")
			sleep(STANDARD_DELAY)

			# z

			keyboard.send("z")
			sleep(STANDARD_DELAY)
			keyboard.write(zField.to_eng_string())
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


		sleep(1)
		# Run another case?
		keyboard.send("y")

		sleep(STANDARD_DELAY)
		print("Complete", wheel, "run", case + 1)

	# For the second half of the data set, all x values go into the A field instead
	for case in range(dataSize // 2, dataSize):
		for wheel in ["R" + axle, "L" + axle]: # Creates FR, FL, RR, RL as needed
			aField = df_MCPFx[wheel + "_Fx"][case]
			yField = df_MCPFy[wheel + "_Fy"][case]
			zField = df_MCPFz[wheel + "_Fz"][case]
			print("Running: " + wheel + "; Case: ", case + 1)

			if(yField < Decimal(.5) or yField > Decimal):
				yField = Decimal(0)

			print("a:", aField)
			print("y:", yField)
			print("z:", zField, "\n")


			### Enter dim data ###

			# a
			keyboard.send("a")
			sleep(STANDARD_DELAY)
			keyboard.write(aField.to_eng_string())
			sleep(STANDARD_DELAY)
			keyboard.send("enter")
			sleep(STANDARD_DELAY)

			# y

			keyboard.send("y")
			sleep(STANDARD_DELAY)
			keyboard.write(yField.to_eng_string())
			sleep(STANDARD_DELAY)
			keyboard.send("enter")
			sleep(STANDARD_DELAY)

			# z

			keyboard.send("z")
			sleep(STANDARD_DELAY)
			keyboard.write(zField.to_eng_string())
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

		sleep(1)
		# Run another case?
		keyboard.send("y")

		sleep(STANDARD_DELAY)
		print("Complete", wheel, "run", case + 1)

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