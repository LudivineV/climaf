"""
This module declares project example and its data location for the standard CliMAF distro

Only one additionnal attribute : frequency (but data sample actually includes only frequency= 'monthly')

Example of an 'example' dataset definition ::

 >>> dg=ds(project='example', experiment='AMIPV6ALB2G', variable='tas', period='1980-1981', frequency='monthly')


"""

import os

from climaf.dataloc import dataloc
from climaf.classes import cproject, calias, cfreqs

from climaf import __path__ as cpath
cpath=os.path.abspath(cpath[0]) 

cproject("example" , "frequency" )
cfreqs('example',{'monthly':'mon' })

data_pattern_L=cpath+"/../examples/data/${experiment}/L/${experiment}SFXYYYY.nc"
data_pattern_A=cpath+"/../examples/data/${experiment}/A/${experiment}PLYYYY.nc"
dataloc(project="example",organization="generic",url=[data_pattern_A,data_pattern_L])