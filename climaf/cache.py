"""

CliMAF cache module : stores and retrieves CliMAF objects from their CRS expression.



"""
# Created : S.Senesi - 2014

import sys, os, os.path, re, time
from climaf.classes import compare_trees, cobject, ctree, cdataset

from clogging import clogger

directoryNameLength=2
DynamicIsOn=False
currentCache=None
cachedirs=None

def setNewUniqueCache(path) :
    """ Define PATH as the sole cache to use from now. And clear it 

    """
    global currentCache
    global cachedirs
    
    cachedirs=[ path ] # The list of cache directories
    crs2filename=dict()  # The index associating filenames to CRS expressions
    cacheIndexFileName = cachedirs[0]+"/index"  # The place to write the index
    currentCache=cachedirs[0]
    craz(hideError=True)
    print "Cache set to "+currentCache

#def generateUniqueFileName(expression, operator=climaf.classes.firstGenericDataSet):
def generateUniqueFileName(expression, operator=None, format="nc"):
    """ Generate a filename path from string EXPRESSION and FILEFORMAT, unique for the
    expression and the set of cache directories currently listed in cache.cachedirs 
    OPERATOR may be a function that provides a prefix, using EXPRESSION

    This uses hashlib.sha224, which are truncated to 3 (or more) characters. 
    More characters are used if a shorter name is already in use for another
    expression in one of the known cache directories 

    Generated names drive a structure where each directory name 1 or 2
    characters and file names have no more characters

    Exits if uniqueness is unachievable (quite unexpectable !) """
    #
    import hashlib
    #
    if format==None : return ""
    prefix=""
    if operator is not None :
        prefix2=operator(expression)
        if prefix2 is not None : prefix=prefix2+"/"
    full=hashlib.sha224(expression).hexdigest()
    number=4
    guess=full[0 : number - 1 ]
    existing=searchFile(prefix+stringToPath(guess, directoryNameLength )+"."+format)
    if existing : 
        readCRS=getCRS(existing)
        # Update index if needed
        if readCRS not in crs2filename :
            clogger.warning("existing data %s in file %s was not yet registered in cache index"%\
                                (readCRS,existing))
            crs2filename[readCRS]=existing
    while ( ( existing is not None ) and ( readCRS != expression )) :
        clogger.debug("must skip %s which CRS is %s"%\
                      (existing, getCRS(existing) ))
        number += 2
        if (number >= len(full) ) :
            clogger.critical("Critical issue in cache : "+len(full)+" digits is not enough for "+expression)
            exit
        guess=full[0 : number - 1 ]
        existing=searchFile(prefix+stringToPath(guess, directoryNameLength )+"."+format)
        if existing : readCRS=getCRS(existing)
    rep=currentCache+"/"+prefix+stringToPath(full[0 : number - 1 ], directoryNameLength )+"."+format
    rep=os.path.expanduser(rep)
    # Create the relevant directory, so that user scripts don't have to care
    dirn=os.path.dirname(rep)
    if not os.path.exists(dirn) : os.makedirs(dirn)
    clogger.debug("returning %s"%rep)
    return(rep)

def stringToPath(name, length) :
    """ Breaks NAME to a path with LENGTH characters-long directory names , for avoiding crowded directories"""
    l=len(name)
    rep=""
    i=0
    while (i + length < l) : 
        rep = rep+name[i:i+length]+"/"
        i   += length
    rep += name[i:l]
    return rep

def searchFile(path):
    """ Search for first occurrence of PATH as a path in all directories listed in CACHEDIRS"""
    for cdir in cachedirs :
        candidate=os.path.expanduser(cdir+"/"+path)        
        if os.path.exists(candidate): return candidate

def register(filename,crs):
    """ Adds in FILE a metadata named CRS_def and with value CRS. Records this FILE in dict crs2filename

    Silently skip non-existing files
    """
    # First read index from file if it is yet empty
    if len(crs2filename.keys()) == 0 : cload()
    # It appears that we have to allow the file system some time for updating its inode tables
    waited=0
    while waited < 10 and not os.path.exists(filename) :
        time.sleep(0.5)
        waited += 1
    time.sleep(0.5)
    if os.path.exists(filename) :
        #while time.time() < os.path.getmtime(filename) + 0.2 : time.sleep(0.2)
        if re.findall(".nc$",filename) : 
            command="ncatted -h -a CRS_def,global,o,c,\"%s\" %s"%(crs,filename)
        if re.findall(".png$",filename) :
            command="convert -set \"CRS_def\" \"%s\" %s %s.png && mv -f %s.png %s"%\
                (crs,filename,filename,filename,filename)
        clogger.debug("trying stamping by %s"%command)
        if ( os.system(command) == 0 ) :
            crs2filename[crs]=filename
            clogger.info("%s registered as %s"%(crs,filename))
            return True
        else : 
            clogger.critical("cannot stamp by %s"%command)
            return None
    else :
        clogger.error("file %s does not exist (for crs %s)"%(filename,crs))

def getCRS(filename) :
    """ Returns the CRS expression found in FILENAME's meta-data"""
    import subprocess
    if re.findall(".nc$",filename) : 
        form='ncdump -h %s | grep -E "CRS_def *=" | '+\
            'sed -r -e "s/.*:CRS_def *= *\\\"(.*)\\\" *;$/\\1/" '
    elif re.findall(".png$",filename) :
        form='identify -verbose %s | grep -E " *CRS_def: " | sed -r -e "s/.*CRS_def: *//"'
    else :
        clogger.critical("unknown filetype for %s"%filename)
        return None
    command=form%filename
    try:
        rep=subprocess.check_output(command, shell=True).replace('\n','')
        if (rep == "" ) : 
            clogger.error("file %s is not well formed (no CRS)"%filename)
        if re.findall(".nc$",filename) : rep=rep.replace(r"\'",r"'")
    except:
        rep="failed"
    clogger.debug("CRS expression read in %s is %s"%(filename,rep))
    return rep

def rename(filename,crs) :
    """ Rename FILENAME to match CRS. Also updates crs in file and
    crs2filename """
    newfile=generateUniqueFileName(crs, format="nc")
    if newfile :
        l=[ c for c in crs2filename if crs2filename[c] == filename ]
        for c in l : del(crs2filename[c]) 
        os.rename(filename,newfile)
        register(newfile,crs)
        return(newfile)
    

def hasMatchingObject(cobject,ds_func) : 

    """ if the cache holds a file which represents an object with the
    same nodes as COBJECT and which leaves/datasets, when paired with
    those of COBJECT and applying ds_func, returns an identical not
    None value for all pairs, then returns its filename, its CRS and
    this value (for the first one in dict crs2filename

    Can be applied for finding same object with included or including
    time-period
    """
    # First read index from file if it is yet empty
    if len(crs2filename.keys()) == 0 : cload()
    def op_squeezes_time(operator):
        import operators
        return not operators.scripts[operator].flags.commuteWithTimeConcatenation 
    #
    for crs in crs2filename :
        co=eval(crs, sys.modules['__main__'].__dict__)
        altperiod=compare_trees(co,cobject, ds_func,op_squeezes_time)
        if altperiod : return co,altperiod
    return None,None

def hasIncludingObject(cobject) :
    def ds_period_difference(includer,included):
        if includer.buildcrs("") == included.buildcrs("") :
            return includer.period.includes(included.period)
    clogger.debug("search for including object for "+`cobject`)
    return hasMatchingObject(cobject,ds_period_difference)

def hasBeginObject(cobject) :
    def ds_period_begins(begin,longer):
        if longer.buildcrs("") == begin.buildcrs("") :
            return longer.period.start_with(begin.period)
    return hasMatchingObject(cobject,ds_period_begins)

def hasExactObject(cobject) :
    # First read index from file if it is yet empty
    if len(crs2filename.keys()) == 0 : cload()
    if cobject.crs in crs2filename :
        return (crs2filename[cobject.crs])

                
def complement(crsb, crse, crs) :
    """ Extends time period of file object of CRSB (B for 'begin')
    with file object of CRSE (E for 'end') for creating file object of
    CRS. Assumes that everything is OK with args compatibility and
    file contents
    """
    fileb=crs2filename[crsb]
    filee=crs2filename[crse]
    filet=generateUniqueFileName(crs)
    command="ncrcat -O %s %s %s"%(fileb,filee,filet)
    if ( os.system(command) != 0 ) :
        clogger.error("Issue when merging %s and %s in %s (using command:%s)"%\
                          (crsb,crse,crs,command))
        return None
    else :
        cdrop(crsb) ; cdrop(crse)
        register(filet,crs)
        return filet

def cdrop(obj, rm=True) :
    """
    Deletes the cached file for a CliMAF object, if it exists

    Args :
     obj (cobject or string) : object to delete, or its string representation (CRS)
     rm (bool) : for advanced use only; should we actually delete (rm) the file, or just forget it in CliMAF cache index
    
    Returns : None if object does not exists, False if failing to delete, True if OK

    Example ::

    >>> dg=ds(project='example', experiment='AMIPV6ALB2G', variable='tas', period='1980-1981')
    >>> f=cfile(dg)
    >>> os.system('ls -al '+f)
    >>> cdrop(dg)
    
    """
    if (type(obj) is ctree ) :
        crs=cobject.crs
        if (type(obj) is cdataset ) :
            crs="select("+crs+")"
    elif type(obj) is str : crs=obj
    else :
        clogger.error("%s is not a CliMAF object"%`obj`)
        return
    if crs in crs2filename :
        clogger.info("discarding cached value for "+crs)
        try :
            if rm : os.remove(crs2filename[crs])
            crs2filename.pop(crs)
            return True
        except:
            return False
    else :
        clogger.error("%s is not cached"%crs)
        return None

def csync() :
    """
    Writes in-memory cache dictionnary to disk ; should be called before exit

    """
    import pickle
    cacheIndexFile=file(os.path.expanduser(cacheIndexFileName), "w")
    pickle.dump(crs2filename,cacheIndexFile)  
    cacheIndexFile.close()

def cload() :
    import pickle
    global crs2filename
    if len(crs2filename) != 0 :
        clogger.critical("attempt to reset file index - would lead to inconsistency !")
        return 
    try :
        cacheIndexFile=file(os.path.expanduser(cacheIndexFileName), "r")
        crs2filename=pickle.load(cacheIndexFile)
        cacheIndexFile.close()
    except:
        pass
        #clogger.debug("no index file yet")

def craz(hideError=False) :
    """
    Clear CliMAF cache : erase existing files content, reset in-memory index

    Args:
      hideError (bool): if True, will not warn for non existing cache

    """
    global crs2filename
    cc=os.path.expanduser(currentCache)
    if (os.path.exists(currentCache) or hideError is False) :
        os.system("rm -fR "+cc+"/*")
        os.system("ls  "+cc)
    #for f in crs2filename : os.remove(crs2filename[f])
    #if os.path.exists(cacheIndexFileName) : os.remove(cacheIndexFileName)
    crs2filename=dict()

def cdump():
    """
    Dumps the in-memory content of CliMAF cache index
    
    """
    for crs in crs2filename :
        #print "%s : %s"%(crs2filename[crs][-30:],crs)
        print "%s : %s"%(crs2filename[crs],crs)


if __name__ == "__main__":
    cachedirs=[ "~/tmp/climaf_cache" ]
    e=getCRS("~/tmp/climaf_cache/test_expressionOf")
    searchFile("test_expressionOf") 
    stringToPath("aerzed",4)    
    print generateUniqueFileName("azertyuiop")


# Todo :

# a function for restoring the index from directory content, in case it has not been written on disk at the end of a session, or it is broken n some other way
