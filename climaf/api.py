"""
CliMAF module ``api`` defines functions for basic CliMAF use : a kind of Application Programm Interface for scripting in Python with CliMAF for easy climate model output processing.

It also imports a few functions from other modules, and declares a number of 'CliMAF standard operators'

Main functions are :

- for data definition and access :

 - ``cproject``: declare a project and its non-standard attributes/facets

 - ``dataloc`` : set data locations for a series of simulations

 - ``cdef``    : define some default values for datasets attributes

 - ``ds``      : define a dataset object (actually a front-end for ``cdataset``)

 - ``eds``     : define an ensemble dataset object (actually a front-end for ``cens``)

 - ``derive``  : define a variable as computed from other variables

 - `` calias`` : describe how a variable is derived form another, single, one, and which
   variable name should be used in deriving data filename for this variable

- for processing the data 

 - ``cscript`` : define a new CliMAF operator (this also defines a new Python function)

 - ``cMA``     : get the Masked Array value of a CliMAF object (compute it)

 - ``cvalue``  : get the value of a CliMAF object which actually is a scalar

 - ``cens``    : define an ensemble of objects 

- for managing/viewing results :

 - ``cfile``   : get the file value of a CliMAF object (compute it)
 
 - ``efile``   : create a single file for an ensemble of CliMAF objects

 - ``cshow``   : display a result of type 'figure'

 - ``cpage``   : create an array of figures

 - ``cdump``   : tell what's in cache

 - ``cdrop``   : delete the cached file for an object

 - ``craz``    : reset cache

 - ``csync``   : save cache index to disk


- utility functions :

 - ``clog``    : tune verbosity

 - ``clog_file``    : tune verbosity for log file

"""
# Created : S.Senesi - 2014


import os, os.path
#
import climaf

# Declare standard projects and standard data locations
from projects import *

#####################################################################################################################
# All CliMAF functions we want to provide as top-level functions when this module is loaded as "from ... import *"
#####################################################################################################################
#
from classes   import cdef,cdataset,ds,cproject,cprojects,aliases,cpage,cfreqs,cens,eds,fds
from cmacro    import macro,cmacros
from driver    import ceval, varOf, cfile, cshow, cMA, cvalue, cimport, cexport,calias, efile
from dataloc   import dataloc 
from operators import cscript, scripts as cscripts,operators, fixed_fields, derive
from cache     import craz, csync, cdump, cdrop,  clist, cls, crm, cdu, cwc
from clogging  import clogger, clog, clog_file
from site_settings import atCNRM, onCiclad, atTGCC
from usual_functions import *

#: Path for the CliMAF package. From here, can write e.g. ``cpath+"../scripts"``. The value shown in the doc is not meaningful for your own CliMAF install
cpath=os.path.abspath(climaf.__path__[0]) 

