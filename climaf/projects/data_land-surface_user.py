"""

Example for defining an 'landsurf_user' dataset::

 >>> cdef('project', 'landsurf_user')
 >>> cdef('root','/cnrm/est/USERS/seferian/em/NO_SAVE',project='landsurf_user') 

 >>> runoff = ds(group='SFX', simulation='BoundLess8', variable='mrros', period='198101')
 
"""

from climaf.site_settings import atCNRM

if atCNRM :
    
    from climaf.dataloc import dataloc
    from climaf.classes import cproject, calias, cfreqs,cdef

    cproject("landsurf_user","root",("group","SFX"),separator="|")

    pathg="${root}/${group}/${simulation}/"
    path1=pathg+"L/${simulation}_TRIP_DIAG_YYYYMM.nc"  
    path2=pathg+"L/${simulation}_TRIP_DIAG_YYYYMM_YYYYMM.nc"
    path3=pathg+"L/${simulation}_TRIP_DIAG_RUN_YYYYMM.nc"
    path4=pathg+"L/${simulation}_TRIP_DIAG_RUN_YYYYMM_YYYYMM.nc"
    path5=pathg+"L/SURFDIAG_${simulation}_YYYY.nc"

    dataloc(project="landsurf_user", organization="generic", url=[path1,path2,path3,path4,path5])
   
    calias("landsurf_user", 'mrros', 'RUNOFF') # scale=1./86400. , units="kg m-2 s-1", filenameVar='Z500')

