A quick summary of what I understand about this folderset.

Autohotkey: A macro software that has a text-based scripting, using a fairly simplistic language.
You will need to download and install Autohotkey to use it. When you run it, it will open up and hide in your
system taskbar, and will wait for its expected keypress to begin. 

The one we've been provided with is what Jake quickly wrote up; it automates a 4-step loop for only a piece of the software.


VDosPlus: Open it by going into the folder and running vDosPlus.exe (not start.exe). It currently defaults to automatically
open Racing by the Numbers; this is configurable through autoexec.txt. Go there and change the filepath after USE to match 
the path to the directory you've stored this in (should only involve changing the beginning part).


Mitchel Tutorial.pptx: A basic tutorial on using Mitchell. I found it somewhat useful. Note that values are listed for the
F21 (I think), and aren't to be trusted.



Python code: A python program written by Phil to parse the output from the copy-paste that the autohotkey script does.
Haven't touched it yet, but it looks like it's basic "read from .txt" code.


Ultimate goal: Assemble the automation process to read data from the Excel spreadsheet, preferably incorporating all of it
into the base python program (multiple files is absolutely fine). If we can do this all with a keypress, wonderful.
