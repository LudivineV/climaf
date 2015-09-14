# Examples for some cdftools operators (muti-variable datasets):
#
# - cdfheatc (computes the heat content in the specified area)
#
# - cdfmxlheatc (computed the heat content in the mixed layer)
#
# - cdfsections (computes temperature, salinity, sig0, sig1, sig2, sig4, Uorth, Utang
#                 along a section made of Nsec linear segments)

#export CLIMAF_FIX_NEMO_TIME='on'  # can be useful at CNRM
from climaf.api import *

if not atCNRM: exit

# Declare "NEMO" project for Nemo raw outputs 
#
cproject('NEMO')

# For 'standard' Nemo output files (actually, they are better accessible using project "EM")
root1="/cnrm/aster/data3/aster/senesi/NO_SAVE/expes/PRE6/${simulation}/O/"
suffix="${simulation}_1m_YYYYMMDD_YYYYMMDD_${variable}.nc"
url_nemo_standard=root1+suffix  
#
dataloc(project='NEMO', organization='generic', url=[url_nemo_standard])
# 
# Declare how variables are scattered/groupes among files
# (and with mixed variable names conventions - CNRM and  MONITORING)
calias("NEMO","uo",filenameVar="grid_U_table2.3")
calias("NEMO","vo",filenameVar="grid_V_table2.3")

# Declare variables grouped in a file
calias("NEMO","so,thetao",filenameVar="grid_T_table2.2")
calias("NEMO","thetao,omlmax",filenameVar="grid_T_table2.2")
calias("NEMO","so,thetao,omlmax",filenameVar="grid_T_table2.2")

# Define defaults facets for datasets 
cdef("project","NEMO")
cdef("frequency","monthly")
cdef("simulation","PRE6CPLCr2alb")
cdef("period","199807")

# How to get fixed files for all cdftools binaries
tpath='/cnrm/aster/data3/aster/chevalli/Monitoring/MONITORING_v3.1/config/'
#can also use placeholders as in '/cnrm/aster/data3/aster/vignonl/${project}/'
fixed_fields(['ccdfheatc1','ccdfmxlheatc1'],
             ('mask.nc',tpath+'ORCA1_mesh_mask.nc'),
             ('mesh_hgr.nc',tpath+'ORCA1_mesh_hgr.nc'),
             ('mesh_zgr.nc',tpath+'ORCA1_mesh_zgr.nc'))

#-----------
# cdfheatc   
#-----------
#
# CDFtools usage :
# cdfheatc  T-file ...
#     ... [imin imax jmin jmax kmin kmax] [-full] 
#
# CliMAF usage (ccdfheatc) :
#

# Define multi-variable dataset with salinity and temperature 
dT1=ds(simulation="PRE6CPLCr2alb", variable="so,thetao", period="199807", realm="O")

# Compute the heat content in the specified area
my_cdfheatc=ccdfheatc1(dT1,imin=100,imax=102,jmin=117,jmax=118,kmin=1,kmax=2)
cfile(my_cdfheatc)

#----------------
#  cdfmxlheatc
#----------------
#
# CDFtools usage :
# cdfmxlheatc T-file [-full]
#
# CliMAF usage (ccdfmxlheatc) :
#

# Define multi-variable dataset with mld 
dT2=ds(simulation="PRE6CPLCr2alb", variable="thetao,omlmax", period="199807", realm="O")

# Compute the heat content in the mixed layer
my_cdfmxlheatc=ccdfmxlheatc1(dT2)
cfile(my_cdfmxlheatc)

#----------------
#  cdfsections 
#----------------
#
# CDFtools usage :
# cdfsections  Ufile Vfile Tfile larf lorf Nsec lat1 lon1 lat2 lon2 n1
#               [ lat3 lon3 n2 ] [ lat4 lon4 n3 ] ....
#
# CliMAF usage (ccdfsections) :
#

# Define datasets with salinity,  temperature, mld, sea water x and y velocity (uo/vo)
dT3=ds(simulation="PRE6CPLCr2alb", variable="so,thetao,omlmax", period="199807", realm="O")      
duo=ds(simulation="PRE6CPLCr2alb", variable="uo", period="199807", realm="O")      
dvo=ds(simulation="PRE6CPLCr2alb", variable="vo", period="199807", realm="O")

# Compute temperature, salinity, sig0, sig1, sig2, sig4, Uorth, Utang 
# along a section made of Nsec linear segments
my_cdfsections=ccdfsections1(duo,dvo,dT3,larf=48.0,lorf=125.0,Nsec=1,lat1=50.0,lon1=127.0,lat2=50.5,lon2=157.5,n1=20)
cfile(my_cdfsections)
cfile(my_cdfsections.Utang)
cfile(my_cdfsections.so)
cfile(my_cdfsections.thetao)
cfile(my_cdfsections.sig0)
cfile(my_cdfsections.sig1)
cfile(my_cdfsections.sig2)
cfile(my_cdfsections.sig4)

my_cdfsections2=ccdfsections1(duo,dvo,dT3,larf=48.0,lorf=305.0,Nsec=2,lat1=49.0,lon1=307.0,lat2=50.5,lon2=337.5,n1=20,more_points='40.3 305.1 50')
cfile(my_cdfsections2)

