__doc__="""
Example for CliMAF access to data organized according to CMIP5 DRS such as :
...../CMIP5/output1/CNRM-CERFACS/CNRM-CM5/1pctCO2/mon/atmos/Amon/r1i1p1/v20110701/clivi/clivi_Amon_CNRM-CM5_1pctCO2_r1i1p1_185001-189912.nc

This example will work as is on CNRM's Lustre and on Ciclad, and 
can be easily tuned to other local CMIP5 datasets

NOTE : Both the CMIP5 project definition and the CMIP5 data locations 
indicated here are actually already declared in standard CliMAF API 
setup (by ``import site_settings`` and ``import standard_projects``)
"""

# S.Senesi - feb 2015

from climaf.api import *

# Declare facets (i.e. dataset attributes) for projet CMIP5
# ACTUALLY, THIS IS BUILT-IN, AND NOT NEEDED - SEE NOTE AT FILE TOP
cproject("CMIP5" ,"model","experiment", ("frequency","monthly"), ("table","*"),
         ("realm","*"),("version","last"), ensemble=["model","simulation"])
cdef("simulation","r1i1p1",project="CMIP5")

# Define a list of root directories for CMIP5 data on IPLS's Ciclad file system
urls_CMIP5_Ciclad=["/prodigfs/esg"]

# Define a list of root directories for CNRM-CM CMIP5 data on CNRM's Lustre FS
urls_CMIP5_CNRM=["/cnrm/aster/data2/ESG/data1", "/cnrm/aster/data2/ESG/data2", 
                 "/cnrm/aster/data2/ESG/data5", "/cnrm/aster/data4/ESG/data6", 
                 "/cnrm/aster/data4/ESG/data7", "/cnrm/aster/data4/ESG/data8"]

# Declare locations for searching data for project CMIP5, experiment and
# frequencies, and that data located in dirs listed in urls_CMIP5_CNRM
# and urls_CMIP5_Ciclad is organized fter built-in scheme 'CMIP5_DRS'
dataloc(project="CMIP5", organization="CMIP5_DRS", 
        url=urls_CMIP5_CNRM+urls_CMIP5_Ciclad)

# Define default value for some dataset facets
cdef("frequency","monthly") ;  cdef("project","CMIP5")

# Define your dataset (a number of facets take default values)
tas1pc=ds(project='CMIP5', model="CNRM-CM5", experiment="1pctCO2", variable="tas", period="1860-1861")

# Display the basic filenames involved in the dataset (all filenames 
# in one single string). CliMAF will search them at the data location 
# which is the most specific among all declared data locations 
files=tas1pc.baseFiles()
print files

# Let CliMAF generate a file with the exact dataset in its disk cache 
# (select period and/or variables, aggregate files...) 
my_file=cfile(tas1pc)
print my_file

# Check file size and content
import os 
os.system("ls -al "+my_file)
#os.system("type ncdump && ncdump -h "+my_file)

if (my_file is None) : exit(1)

