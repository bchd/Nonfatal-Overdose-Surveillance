"""
Python Script for Non-Fatal Overdose Surveillance Project, Using Daily EMS Data Excel *.xlsx Files
Last Updated on 2/14/2019
Notes:
ArcGIS uses Python 2 (not 3). The code was initially developed in ModelBuilder and then exported and added to this Python script.
This script still requires the arcpy Python library.  Optional, spatial joins for Baltimore geographies are contained
in an ArcGIS toolbox that was created in ModelBuilder.
Notes: Check overwrite geoprocessing checkbox results in ArcGIS
"""

# Overview
# Part I: High Level Data Cleaning of *.csv file received.
# Part II: Geocodes daily EMS data in *.csv and adds Geoographic Coordinates, in case they are needed. Adds string Date Field. (R Date format problems)
# Part IIb: Data management -adds in geographic coordinates in addiion to State Plane
# Part III: OPTIONAL: Performs Spatial Joins on Multiple Boundary Types (Zipcode,etc).
# Part IV: Appends Data to Master Geodatabase

# Inputs and Outputs
# You'll need a daily CSV of non-fatal overdose, an address locator (offline to protect privacy), and optional boundary files to join geographic boundary attributes to point data.
# You must install Python PANDAS library.  To make sure you use the right version, check numpy version in ArcGIS, then install a compatible version.
# Type: import numpy, and then numpy.version.full_version

# Imports arcpy library (Python for ArcGIS) and other libraries required
import arcpy
import os
import sys
import datetime
import win32com.client
from win32com.client import Dispatch
import csv
import pandas as pd
import numpy as np
from tempfile import NamedTemporaryFile
import logging
#import string

# Logging/Optional
# Reference: https://www.digitalocean.com/community/tutorials/how-to-use-logging-in-python-3
# log_file="Z:/Daily Narcan Data/AutoData/"+str(datetime.date.today())+".log"
# logging.basicConfig(filename=log_file, level=logging.DEBUG)

# Conditional Language to Initiate Automation
# If needed, add here.
"""
# Logging
"""
date_string=str(datetime.date.today()-datetime.timedelta(2))
logging.basicConfig(filename='O:/Production/Logs/'+date_string+'.log',level=logging.DEBUG)
"""
End of logging setup
"""

"""
Part I:  Downloads Excel Spreadsheet from Outlook
"""
# Reference: https://stackoverflow.com/questions/22399835/how-to-save-attachment-from-outlook-using-win32com-client-in-python
outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
inbox = outlook.GetDefaultFolder("6")
all_inbox = inbox.Items
#messages= msg.Attachments
#val_date = datetime.date.today()

sub_today = 'Daily Naloxone Data '+date_string
att_today = 'Daily Naloxone Data '+date_string+'.xlsx'

# Loop through messages and stop at message with today's subject and attachment.
for msg in all_inbox:
    if msg.Subject:
        new=msg.Subject
        if new.find('Naloxone') !=-1 & new.find(date_string) !=-1:
            #print("Step 1")
            break

for att in msg.Attachments:
    if att.FileName:
        #print("Step 2")
        break

# Change Directory and Save Attachment  
os.chdir('O:/Production/Daily Narcan Data')
att.SaveAsFile(os.getcwd()+ '\\'+att_today)
logging.info('Finished Attachment Download')

"""
Part II: Open Password-Protected Excel Workbook Using Python.
"""
# Add your filename and password below.
xlApp=win32com.client.Dispatch("Excel.Application")
print "Excel library version:", xlApp.Version
todays_file=os.getcwd()+ '//'+att_today
filename,password=todays_file,'YOUR PASSWORD'
xlwb=xlApp.Workbooks.Open(filename,0, True, None,Password=password)

# Code to resave *.xlsx as *.csv without password.
# Reference: https://stackoverflow.com/questions/36850716/from-password-protected-excel-file-to-python-object
# Create an accessible temporary file, and then delete it.
f = NamedTemporaryFile(delete=False, suffix='.csv')  
f.close()

# Not deleting will result in a "File already exists" warning
os.unlink(f.name)  

# CSV file format, from enum XlFileFormat
xlCSVWindows = 0x17
xlwb.SaveAs(Filename=f.name, FileFormat=xlCSVWindows)

# Read into Pandas Datafram
df = pd.read_csv(f.name)  # Read that CSV from Pandas
#print df
logging.info('Finished Converting Attachment to CSV')

"""
Creates VARIABLES for time-dependent file pathnames.
"""

# Creates variable system date for today's date and filepath that changes each day when script is run by Windows Task Scheduler.

# Creates date and string date variables for auotmation.
SYS_DATE=(datetime.date.today()-datetime.timedelta(1))
SYS_MONTH=str(datetime.date.today().strftime("%m"))
SYS_DAY=str(datetime.date.today().strftime("%d"))
SYS_YEAR=str(datetime.date.today().strftime("%Y"))
NON_HYPHEN_DATE=SYS_YEAR+"_"+SYS_MONTH+"_"+SYS_DAY
SYSTEM_DATE=str(datetime.date.today())

# Add your *.csv Directory Here. Our Daily *.csvs are named Daily-Naloxone-Date_YYYY-MM-DD.
CSV_DIRECTORY="O:/Production/Daily Narcan Data/"
DAILY_CSV=CSV_DIRECTORY+"Daily Naloxone Data "+date_string+".csv"
CLEAN_CSV=CSV_DIRECTORY+"Daily-Naloxone-Data_"+date_string+"_clean"+".csv"
CLEAN_NAME="Daily_Naloxone_Data_"+date_string+"_clean"
GEOCODED="Daily_Naloxone_Data_"+date_string+"_clean_geo"

# Location for a Workspace/Geodatabase that will be created and deleted daily. All daily files generated will be located in this geodatabase.
# At the end of the script, the daily EMS files are appended to a Master Geodatabase
GEO_DB="O:/Opioid_Clusters/Geodatabase/Overdose.gdb/"

# Intermediates
INTER_NAME1=GEO_DB+CLEAN_NAME
INTER_NAME1=INTER_NAME1.replace("-", "_")
INTER_NAME2=GEO_DB+GEOCODED
INTER_NAME2=INTER_NAME2.replace("-", "_")
#INTER_NAME3=INTER_NAME1+"_3_"
logging.info('Finished Generating Python Variables')

"""
Part I: Cleans data for high-level errors in *.csv files.  Saves a clean *.csv file. May create a separate folder for clean files-particularly if we use file added automation.
"""
# High Level Data Cleaning
# 1) Fixes *.csv files with characters in the Incident Number.
# 2) Removes "BLK"(Block) in Incident Address
# 3) Replaces "/" in intersections with two street names with "&" connector
#inputcsv=pd.read_csv(DAILY_CSV)
inputdata=df

"""
Maps ELITE Variable Names to Old EMS Data Variable Names (12/5/2018).
"""

# Drop extraneous variables. Later on keep Lat and Long (missing right now).
inputdata=inputdata.drop(['CAD Scene Incident GPS Latitude (eScene.11)','Scene GPS Latitude (eScene.11)','Scene GPS Latitude Encoded (eScene.11)','Scene GPS Longitude (eScene.11)','Scene GPS Longitude Encoded (eScene.11)'],axis=1)
inputdata=inputdata.drop(['Disposition Destination GPS Latitude (eDisposition.09)','Disposition GPS Latitude Encoded (eDisposition.09)','Injury ACN Incident GPS Latitude (eInjury.15)'],axis=1)
inputdata=inputdata.drop(['Patient Home Street Address Latitude (ePatient)','Response Dispatch GPS Latitude (eResponse.17)'],axis=1)
inputdata=inputdata.drop(['Response Vehicle Dispatch Latitude (eResponse.17)','Response Vehicle Dispatch Location Latitude (eResponse.17)','CAD Scene Incident GPS Longitude (eScene.11)'],axis=1)
inputdata=inputdata.drop(['Disposition Destination GPS Longitude (eDisposition.09)','Disposition GPS Longitude Encoded (eDisposition.09)','Injury ACN Incident GPS Longitude (eInjury.15)'],axis=1)        
inputdata=inputdata.drop(['Patient Home Street Address Longitude (ePatient)','Response Dispatch GPS Longitude (eResponse.17)','Response Vehicle Dispatch Location Longitude (eResponse.17)'],axis=1)
inputdata=inputdata.drop(['Response Vehicle Dispatch Longitude (eResponse.17)', 'Incident Agency Location Longitude (dLocation.04)', 'Incident Agency Location Latitude (dLocation.04)'],axis=1)         
#inputdata

# Ensure columns are in the correct order
#neworder1 = ['CAD Unit Arrived On Scene Date Time (eTimes.06)','Incident Number (eResponse.03)', 'Patient Age In Years (ePatient.15)','Patient Gender (ePatient.13)', 'Patient Race List (ePatient.14)','Scene Incident Street Address (eScene.15)','Situation Provider Primary Impression Description Only (eSituation.11)','Disposition Destination Code Delivered Transferred To (eDisposition.02)','Medication Given Description (eMedications.03)','Medication Response (eMedications.07)','Medication Dosage (eMedications.05)','Disposition Incident Patient Disposition (eDisposition.12)']
neworder1 = ['Incident Date Time','Incident Number (eResponse.03)', 'Patient Age (ePatient.15)','Patient Gender (ePatient.13)', 'Patient Race List (ePatient.14)','Scene Incident Street Address (eScene.15)','Situation Provider Primary Impression Description Only (eSituation.11)','Disposition Destination Code Delivered Transferred To (eDisposition.02)','Medication Given Description (eMedications.03)','Medication Response (eMedications.07)','Medication Dosage (eMedications.05)','Disposition Incident Patient Disposition (eDisposition.12)']
inputdata=inputdata.reindex(columns=neworder1)

# Rename column names
inputdata.columns=['Incident Date', 'Incident Number', 'Patient Age','Patient Gender','Patient Race (E6.12)','Incident Address','Primary Impression','Destination Code (E20.2)','Medication Administered (E18.3)','Medication Response - to Med (E18.7)','Medication Dosage (E18.5)','Destination Patient Disposition (E20.10)']

# Create Time variable for time only based on Incident Date Field. 
# Then reformat both fields to be date only and time only, respectively.
#inputdata['Times : Arrived on Scene']=inputdata['Incident Date']

# Fixes Incident Date Field
inputdata['Incident Date']=inputdata['Incident Date'].astype('str')

# Detects if "/" are present and replaces with dashes "-"
inputdata['DataType']=inputdata['Incident Date'].str.contains('/')

# Receive: MM/DD/YYYY (Can shorten this half later)
if inputdata['DataType'].iloc[0]:
    inputdata['Incident Date']=inputdata['Incident Date'].str.replace("/",'-',)
    
    # Split datatime field
    inputdata['Incident Date'], inputdata['Times : Arrived on Scene Time'] = inputdata['Incident Date'].str.split(' ', 1).str
    
    # Manages Date (MM/DD/YYYY)
    inputdata['Month'], inputdata['Day'],inputdata['Year'] = inputdata['Incident Date'].str.split('-', 2).str
    inputdata['Newdate']=inputdata['Month']+"/"+inputdata['Day']+"/"+inputdata['Year']
    inputdata['Incident Date']=inputdata['Newdate']
    inputdata=inputdata.drop(['Incident Date'],axis=1)
    inputdata['Incident Date']=inputdata['Newdate']
    inputdata=inputdata.drop(['Year','Month','Day','Newdate','DataType'],axis=1)
    inputdata.columns=['Incident Number', 'Patient Age','Patient Gender','Patient Race (E6.12)','Incident Address','Primary Impression','Destination Code (E20.2)','Medication Administered (E18.3)','Medication Response - to Med (E18.7)','Medication Dosage (E18.5)','Destination Patient Disposition (E20.10)','Times : Arrived on Scene Time','Incident Date']

else:
    # Split datatime field
    inputdata['Incident Date'], inputdata['Times : Arrived on Scene Time'] = inputdata['Incident Date'].str.split(' ', 1).str
    
    # Manages Date
    inputdata['Year'], inputdata['Month'],inputdata['Day'] = inputdata['Incident Date'].str.split('-', 2).str
    inputdata['Newdate']=inputdata['Month']+"/"+inputdata['Day']+"/"+inputdata['Year']
    inputdata['Incident Date']=inputdata['Newdate']
    inputdata=inputdata.drop(['Incident Date'],axis=1)
    inputdata['Incident Date']=inputdata['Newdate']
    inputdata=inputdata.drop(['Year','Month','Day','Newdate'],axis=1)
    inputdata.columns=['Incident Number', 'Patient Age','Patient Gender','Patient Race (E6.12)','Incident Address','Primary Impression','Destination Code (E20.2)','Medication Administered (E18.3)','Medication Response - to Med (E18.7)','Medication Dosage (E18.5)','Destination Patient Disposition (E20.10)','Times : Arrived on Scene Time','Incident Date']

#inputdata['Incident Date']=pd.to_datetime(inputdata['Newdate'],format='%m/%d/%Y')

#inputdata['Incident Date']=inputdata['Incident Date'].dt.strftime('%m/%d/%Y')
#inputdata['Incident Date'] = pd.to_datetime(inputdata['Incident Date'],format='%Y%m%d')
#inputdata['Times : Arrived on Scene Time'] = pd.to_datetime(inputdata['Times : Arrived on Scene Time'])
#inputdata

# Temporarily Create Lat Long Fields - will be changed later--e.g. dropped column above step renamed and kept.
inputdata['Incident Location Latitude']=float(9.99)
inputdata['Incident Location Longitude']=float(9.99)

# Fixes any Medication dosage fields with commas(invalid dosage)
#inputdata['Medication Dosage (E18.5)']=inputdata['Medication Dosage (E18.5)'].str.replace("1,640",'1640',)
inputdata['Medication Dosage (E18.5)']= inputdata['Medication Dosage (E18.5)'].astype(float)
                                    
# inputdata.dtypes

# Reorder
neworder2 = ['Incident Date','Incident Number', 'Patient Age','Patient Gender', 'Patient Race (E6.12)','Incident Address','Primary Impression','Incident Location Latitude','Incident Location Longitude','Times : Arrived on Scene Time','Destination Code (E20.2)','Medication Administered (E18.3)','Medication Response - to Med (E18.7)','Medication Dosage (E18.5)','Destination Patient Disposition (E20.10)']
inputdata2=inputdata.reindex(columns=neworder2)                  
"""
END of ELITE transition
"""

# Incident Number fixes
inputdata2['Incident Number']=inputdata2['Incident Number'].astype('str')
inputdata2['Incident Number']=inputdata2['Incident Number'].str.replace("[^\d]",'',)
inputdata2['Incident Number']=np.where(inputdata2['Incident Number']=='', '999998',inputdata2['Incident Number'])
inputdata2['Incident Number']=inputdata2['Incident Number'].astype('int64')

# Incident Address fixes
inputdata2['Incident Address']=inputdata2['Incident Address'].str.replace(" BLK",'',)
inputdata2['Incident Address']=inputdata2['Incident Address'].str.replace("-BLK",'',)
inputdata2['Incident Address']=inputdata2['Incident Address'].str.replace(" blk",'',)
inputdata2['Incident Address']=inputdata2['Incident Address'].str.replace("-blk",'',)
inputdata2['Incident Address']=inputdata2['Incident Address'].str.replace("-BL ",'',)
inputdata2['Incident Address']=inputdata2['Incident Address'].str.replace("/",' & ',)

# Rename columns again
inputdata2.columns=['Incident_Date','Incident_Number', 'Patient_Age','Patient_Gender', 'Patient_Race__E6_12_','Incident_Address','Primary_Impression','Incident_Location_Latitude','Incident_Location_Longitude','Times___Arrived_on_Scene_Time','Destination_Code__E20_2_','Medication_Administered__E18_3_','Medication_Response___to_Med__E18_7_','Medication_Dosage__E18_5_','Destination_Patient_Disposition__E20_10_']
          
# Save cleaned *.csv
inputdata2.to_csv(CLEAN_CSV,index=False)
logging.info('Finished High Level Data Cleaning')

"""
Part II: Imports EMS data into a geodatabase. Then Geocodes it - Maryland State Plane Coordinates, Feet
# Projection: NAD_1983_StatePlane_Maryland_FIPS_1900_Feet
"""
# Creates Geodatabase and Imports *.csv data.  Creates DAILY_EMS variable from Cleaned CSV for geoprocessing.  
GIS_Workflow = "O:/Opioid_Clusters/Geodatabase/"
Overdose_gdb = "O:/Opioid_Clusters/Geodatabase/Overdose.gdb"

#Process: Create File GDB
arcpy.CreateFileGDB_management(GIS_Workflow, "Overdose", "10.0")

#Process: Table to Geodatabase (multiple)
arcpy.TableToGeodatabase_conversion(CLEAN_CSV, Overdose_gdb)

# Script arguments
#GEOCODED = arcpy.GetParameterAsText(0)
#if GEOCODED == '#' or not GEOCODED:
 #   GEOCODED = GEO_DB+GEOCODED # provide a default value if unspecified

# Local variables:
EGISCompositeLocator__2_ = "O:/Production/Locator/v101/EGISCompositeLocator"

# Process: Geocode Addresses
arcpy.GeocodeAddresses_geocoding(INTER_NAME1, EGISCompositeLocator__2_, "SingleLine Incident_Address VISIBLE NONE", INTER_NAME2, "STATIC")
logging.info('Finished Geocoding')
             
"""
Part IIb: Adds in fields for Geographic Coordinates(WGS 84), in case they are needed. 
"""
arcpy.AddGeometryAttributes_management(INTER_NAME2, "POINT_X_Y_Z_M", "", "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
logging.info('Finished Adding Geographic Coordinates')

"""
Part III: OPTIONAL: Performs Multiple Spatial Joins on Multiple Boundary Files specific to Baltimore(Zipcodes, CSAs,etc.). Uses ArcGIS Toolbox
"""
tbx=arcpy.AddToolbox(r"O:/Production/Locator/Overdose.tbx")
inFC=INTER_NAME2
tbx.SpatialJoin(inFC)
logging.info('Finished Spatial Joins')
             
# Deletes misc. variables. Resulting file for multiple spatial joins is CallsZip and contains attribute data on multiple geographies.
CallsZip = "O:/Opioid_Clusters/Geodatabase/Overdose.gdb/CallsZip"

# Process: Delete Field
arcpy.DeleteField_management(CallsZip, "Join_Count;TARGET_FID")


"""
Part IV: Appends to Master Geodatabase + Deletes Daily Workspace Geodatabase.  Can also export table to *.csv using newer versions of ArcGIS.
"""

# Adds String Date (just in case. R-ArcGIS bridge had trouble with some dates.)
arcpy.AddField_management(CallsZip, "Date", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(CallsZip, "Date", "[Incident_Date]", "VB", "")
#arcpy.CalculateField_management(CallsZip, "Date", "!Incident_Date!", "PYTHON", "")

# Master Nonfatal Overdose Database
Nonfatal = "O:/Opioid_Clusters/Geodatabase/Master.gdb/Nonfatal"

# Process: Append
arcpy.Append_management("'O:/Opioid_Clusters/Geodatabase/Overdose.gdb/CallsZip'", Nonfatal, "NO_TEST", "", "")

# Deletes Overdose (Daily Workspace)
arcpy.Delete_management("O:/Opioid_Clusters/Geodatabase/Overdose.gdb", "Workspace")
logging.info('Finished Appending')

"""
END OF SCRIPT
FOR INTERNAL USE ONLY
"""

