Forces_Parser.py

Authors: Arthur Heiles, Phillip Kelner, Ian Clare

### Introduction ###

Python program to automate the process of data entry and retrieval from
Mitchell's "Racing by the Numbers", running on the DOS emulator VDosPlus.
The program that stores a model of the racecar's suspension setup, and takes in
force component vectors acting on the wheels, outputting the individual forces
acting on each part of the suspension. Suspension models can be interchanged,
but modification of underlying python code will be necessary to ensure continued function,
as the project relies on relative position in a list to select the correct model.

The program makes use of a few less common python modules to simulate the typing
of data into fields within Mitchell's, and requires VDosPlus's ctrl+a hotkey, which
copies the information on screen directly into the system clipboard, to retrieve
data. The result of the copy-paste is parsed for the useful values, which are
then exported into an MS Excel table.

### Installation Instructions ###

The code was designed to run on a Windows OS and python 3.5.2; I make no guarantee
that it will work elsewhere.


Step 1: Install Python 3.5.2

At this time, the following link contains all downloads for this version:
https://www.python.org/downloads/release/python-352/

    - Download the version appropriate to your operating system (these instructions
    assume the executable installer)

Using other versions may fail due to some of the modules being out of date, or
changes in Python code that break this program; later versions are especially
bad for this.

    - Check the box to add Python to the PATH variable. This lets us find the
    python executable later down the line

    - Install Now (should include everything we need by default)

Step 2: Add python to your PATH environment variable

This was probably handled automatically, but let's check anyways

    - Search your computer for "Environment Variables"; you should come up
    with an option in settings to edit the Environment Variables

    - At the bottom of the window that pops up, click the Environment Variables button

    - One of them will be called "Path". Click on it, and click "Edit"

    - It will give you a list of file-paths; two of them should lead to the Python
    folder; one will end at Python\Python35, the other at Python\Python35\Scripts

    - If either of these do not exist, then click "New" and add them. It may be
    easiest to find the directory that the python executable is in, and copy the
    path to that point.

    - To test that it all works, open the windows command prompt and type "python",
    then press Enter. You should get a python interactive prompt, with each
    line beginning in ">>>". If you do, then everything is set up correctly so far.
    Close the command prompt.

Step 3: Install necessary python modules

    - Run install_modules.cmd from the same directory this file is in. It should
    automatically run the command line arguments to install the necessary modules
    through pip.

    - After it finishes, it will pause and wait for you to tell it to exit. Before
    pressing Enter, scroll up through its printed output looking for error messages.
    If the message says something along the lines of "could not find <module>",
    then you probably have the wrong version of python and that module does not
    exist for that version. If you get a message along the lines of "no access to <folder>"
    it's probably because you aren't an admin; that's my best guess.

    - Any other red text, see if you can understand the error message and
    if you can't, find someone who can. I can't imagine what else would come up,
    but I guarantee something will.

Step 4: Necessary path modifications

    - If you changed any of the project's directories up to this point, you may
    need to tell the program that you did so. Open path_config.txt and check
    that all of the filepaths there match up - especially the one to VDosPlus's
    executable. Many of the files may not be present yet, and will be generated
    during program runtime. This file will be discussed in greater detail later.


### Run Instructions ###

The program is run by executing Friction_Circle.py; this should be doable by
double clicking on it, or right clicking, Open With > Python. It will open
in a command prompt style window, and begin.

Enter the number of load cases. This is the number of angles that forces will
be calculated for, evenly distributed across the range (0, pi]. Estimated runtime
is ~50 seconds per load case.

***
Note: The 0 case is not included in this count and is added to the dataset
automatically; entering 5 will produce coefficients of pi 0, 0.2, 0.4, 0.6, 0.8, 1.0***

Note: The .5 case causes issues (division by cos( .5pi ) = 0). If this case is
encountered, values very close to it on either side are run instead; this produces
an additional load case. Entering 10 will produce 12 coefficients, with .1 between
each, except for the two center values which will receive very close to .5 values
***

The program will read filepaths from path_config.txt and any information about the
car's physical attributes from the car config file specified therein.

The car's physical attributes will then be used to calculate all of the required
forces, and a fair few more on top of that, for every load case. This data is
exported in its raw form to the dump excel file specified within path_config.txt,
and a formatted version of it with the forces used for Mitchell's is exported
to the formatted excel file specified within path_config.txt

You will then be prompted to to press Enter when ready.

VDosPlus will open automatically running Mitchell's "Racing by the Numbers".
Once it is open, do not attempt to change windows; the simulated keypresses
assume that VDosPlus is the active window and will continue to type on whatever
page is at the front of the screen. If this happens, the program will need to
restart; it cannot currently recover from having missed keypresses. I recommend
walking away from the computer for the expected duration (50 seconds / load case).

It is possible that something will go wrong, and the Mitchell's will crash within
VDosPlus, throwing a Runtime error. This is an extremely uncommon problem, and
is usually caused by a buffer overflow when copying the force values into Mitchell's
x, y, z fields because the keypress to enter the field did not register and the
program continued typing in it.

Under these circumstances, Friction Circle may finish executing properly,
or may throw an error. If it finishes execution, any data in the parsed-forces excel
file will likely be garbage; don't try to make sense of it.

When data entry is done, VDosPlus will be exited, and the output that was copied
from it will be parsed and exported to the Parsed Forces output file.