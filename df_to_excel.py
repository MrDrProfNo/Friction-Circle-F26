import os  # filepath related functions
import traceback

from pandas import ExcelWriter



# Row that data starts at for formatted dump
FORMAT_DATA_ROW_START = 5

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
	dataframe.to_excel(filename)

def formatted_dump(dirpath, filename, dataframes):
	### Separate out Max Contact Patch Forces ###
	df_MCPFx, df_MCPFy, df_MCPFz = dataframes
	# Set the filepath for the target file by appending to path to output
	# folder

	# Define the pandas ExcelWriter using xlsxwriter as the engine
	writer = ExcelWriter(filename, engine='xlsxwriter')

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



	# Strings labeling the start and end points of each coloring segment
	# for the formatting (by row). Names should be fairly self-evident.

	green_start_str = str(FORMAT_DATA_ROW_START)

	green_end_str = str(FORMAT_DATA_ROW_START + dataLength // 2 - 1)

	yellow_start_str = str(FORMAT_DATA_ROW_START + dataLength // 2)

	yellow_end_str = str(FORMAT_DATA_ROW_START + (dataLength + 1) // 2)

	red_start_str = str(FORMAT_DATA_ROW_START + 1 + (dataLength + 1) // 2)

	red_end_str = str(FORMAT_DATA_ROW_START + dataLength)


	# So... this works. Select cell range, tell it to look for text not
	# containing "t"; they're all numbers, so that will always evaluate true
	### Longitudinal Force Formatting ###
	ws.conditional_format('B' + green_start_str + ':E' + green_end_str,
						  {"type": "text", "criteria": "not containing",
						   "value": "t", "format": format_bg_red})
	ws.conditional_format('B' + yellow_start_str + ':E' + yellow_end_str,
						  {"type": "text", "criteria": "not containing",
						   "value": "t", "format": format_bg_yellow})
	ws.conditional_format('B' + red_start_str + ':E' + red_end_str,
						  {"type": "text", "criteria": "not containing",
						   "value": "t", "format": format_bg_green})
	### Lateral Force Formatting ###
	ws.conditional_format('G' + green_start_str + ':J' + green_end_str,
						  {"type": "text", "criteria": "not containing",
						   "value": "t", "format": format_bg_red})
	ws.conditional_format('G' + yellow_start_str + ':J' + yellow_end_str,
						  {"type": "text", "criteria": "not containing",
						   "value": "t", "format": format_bg_yellow})
	ws.conditional_format('G' + red_start_str + ':J' + red_end_str,
						  {"type": "text", "criteria": "not containing",
						   "value": "t", "format": format_bg_green})
	### Vertical Force Formatting ###
	ws.conditional_format('L' + green_start_str + ':O' + green_end_str,
						  {"type": "text", "criteria": "not containing",
						   "value": "t", "format": format_bg_red})
	ws.conditional_format('L' + yellow_start_str + ':O' + yellow_end_str,
						  {"type": "text", "criteria": "not containing",
						   "value": "t", "format": format_bg_yellow})
	ws.conditional_format('L' + red_start_str + ':O' + red_end_str,
						  {"type": "text", "criteria": "not containing",
						   "value": "t", "format": format_bg_green})

	writer.save()
