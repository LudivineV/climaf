"""

This module declares project EM , which data organization is built-in

EM (Experiment Manager) is a tool used at CNRM for moving simulation post-processed data
from the HPSS to the local filesystem, and to organize it in a file hierarchy governed by a few
configuration files

Simulation names (or 'EXPIDs') are assumed to be unique in the namespace defined by the user's configuration
file, which may include shared simulation

Example for defining an EM dataset::

 >>> tas=ds(project='EM', simulation='GSAGNS1', variable='tas', period='1975', frequency='monthly', realm='L')

 A number of Seaice fields are duly described with 1.e+20 as missing value (which is ill described in data files); see code for details

"""

from climaf.site_settings import atCNRM

if atCNRM :

    from climaf.dataloc import dataloc
    from climaf.classes import cproject, calias, cfreqs
    
    cproject('EM' , ('frequency','monthly'), ('realm','*') )
    cfreqs('EM',{'monthly':'mon' , 'daily':'day1' })
    dataloc(project='EM', organization='EM', url=['dummy'])

    # Ideally, one should be able to write :
    #cmissing('EM',1.e+20, realm='I')
    calias('EM',[ 'sic', 'sit', 'sim', 'snd', 'ialb', 'tsice', 'mpalb', 'snomlet',
                  'tmelt', 'bmelt', 'snc','sic1','sic2', 'sic3', 'sic4', 'ssi', 'ageice'],
           missing=1.e+20)

