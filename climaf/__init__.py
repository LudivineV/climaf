"""
Climaf is documented at ReadTheDocs : http://climaf.readthedocs.org/

"""

# Created : S.Senesi - 2014

__all__=[ "cache" , "classes", "clogging",   "dataloc" , "driver" , "netcdfbasics", "operators", "period",
          "site_settings"  , "standard_operators" , "projects" ]
import posixpath, os, sys

version="0.6.1"

already_inited=False

if not already_inited  : 
    already_inited=True
    #
    import atexit
    #
    import clogging, site_settings , cache, standard_operators, cmacros
    print "Climaf version = "+version
    #
    # Set default logging levels
    clogging.clog(os.getenv("CLIMAF_LOG_LEVEL","warning"))
    clogging.clog_file(os.getenv("CLIMAF_LOGFILE_LEVEL","info"))
    #
    # Read and execute user config file
    conf_file=os.path.expanduser("~/.climaf")
    if os.path.isfile(conf_file) :
        execfile(conf_file,sys.modules['__main__'].__dict__)
    #    
    # Decide for cache location
    if site_settings.onCiclad :
        default_cache="/data/"+os.getenv("USER")+"/climaf_cache"
    else: default_cache="~/tmp/climaf_cache"
    cache.setNewUniqueCache(os.getenv("CLIMAF_CACHE",default_cache))
    print "You may tune CliMAF cache location by setting $CLIMAF_CACHE before launch"
    #
    # Init dynamic CliMAF operators
    standard_operators.load_standard_operators()
    #
    # Load cache index
    cache.cload()
    #
    # Init and load macros
    cmacros.read()
    atexit.register(cmacros.write)
    #
    atexit.register(cache.csync)


