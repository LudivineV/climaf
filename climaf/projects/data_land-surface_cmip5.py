"""

Example for defining an 'landsurf_cmip5' dataset::

 >>> cdef('project', 'landsurf_cmip5')
 >>> cdef('root','/cnrm/est/USERS/seferian/em/NO_SAVE',project='landsurf_cmip5') 

 >>> snd = ds(group='SFX', simulation='trendyS1', variable='snd', period='1869')
 
"""

from climaf.site_settings import atCNRM

if atCNRM :
    
    from climaf.dataloc import dataloc
    from climaf.classes import cproject, calias, cfreqs,cdef

    cproject("landsurf_cmip5","root",("group","SFX"),separator="|")

    pathg="${root}/${group}/${simulation}/"
    pathL=pathg+"L/SURFDIAG_${simulation}_YYYY.nc"
    
    dataloc(project="landsurf_cmip5", organization="generic", url=pathL)
    
