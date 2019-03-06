"""
Python Script for Run Order of Python Files, Using Daily EMS Data *.csv Files
Last updated on 2/14/2019
Notes: This script directs the order and if OverdosePython.pyw and the day-behind file
should be run.
"""

# Import libraries
import arcpy
import os
import sys
import datetime
from pathlib2 import Path
import subprocess

# Todays date
yesterday=str(datetime.date.today()-datetime.timedelta(2))
todays_date = str(datetime.date.today())

# Execute Python File Order - depending on what data we've received
fileExists = os.path.isfile("O:/Production/Daily Narcan Data/Daily Naloxone Data "+yesterday+".xlsx")

if fileExists:
              subprocess.call(['python', "O:/Production/OverdosePython.pyw"],shell=False)

else:
    subprocess.call(['python', "O:/Production/OverdosePython_DayBehind.pyw"],shell=False)
    subprocess.call(['python', "O:/Production/Overdose.pyw"],shell=False)  

"""
END OF SCRIPT
"""
