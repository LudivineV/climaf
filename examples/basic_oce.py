"""
Example for CliMAF use with ORCA data

This example will work as is on CNRM's Lustre or Ciclad
"""

# S.Senesi - march 2015

# Load Climaf functions
from climaf.api import *

# Load default settings for IPSL and CNRM. This sets logcial flags 'onCiclad' and 'atCNRM'
from climaf.site_settings import *

# Define default value for some dataset facets
cdef("frequency","monthly") ;  cdef("project","CMIP5")

# Choose a model and define your dataset 
if onCiclad : cdef ("model","IPSL-CM5-LR")
else :
    if atCNRM : cdef ("model","CNRM-CM5")
    else :
        print("I do not know how to find CMIP5 data on this machine")
        exit(0)
tos=ds( experiment="historical", variable="tos", period="186001-186002")

# Display the basic filenames involved in the dataset (all filenames in one single string)
# CliMAF will search them at the data location which is the most specific among all declared data locations 
files=tos.selectFiles()
print files

# Let CliMAF provide the filename for the exact dataset in its disk
# cache (select period and/or variables, aggregate files...) 
my_file=cfile(tos)
print my_file

# Check file size and content
import os
os.system("ls -al "+my_file)
#os.system("type ncdump && ncdump -h "+my_file)

# Plot first time step
fig=plotmap(tos,min=270, max=300, delta=3)
cshow(fig)

# Select a latlon box and plot it
tos_box=llbox(tos,latmin=40, lonmin=-30, lonmax=5, latmax=66)
cshow(ncview(tos_box))


# Compute a time average on 50 years - this takes  ~10s on my PC
tos=ds( experiment="historical", variable="tos", period="1860-1910")
tosavg=time_average(tos)
cshow(ncview(tosavg))

# Compute annual cycle over 50 years, using swiss knife operator 'ccdo', and look at it
anncycle=ccdo(tos,operator='ymonavg')
cshow(ncview(anncycle))

# Define the average annual cycle over the NINO34 box
nino34=dict(lonmin=-170, lonmax=-120, latmin=-5, latmax=5)
extract=llbox(anncycle,**nino34)
space_average=ccdo(extract,operator='fldavg')
cshow(ncview(space_average))

# Regrid the 2D annual cycle to a latlon grid, using CDO grid names
anncycle_4deg=regridn(anncycle, cdogrid="r90x45")
cshow(ncview(anncycle_4deg))
