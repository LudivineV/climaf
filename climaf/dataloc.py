""" CliMAF datasets location handling and data access module

Handles a database of attributes for describing organization and location of datasets
"""

# Created : S.Senesi - 2014

import os, re,logging, string, glob
from climaf.period import init_period
from climaf.netcdfbasics import fileHasVar

locs=[]

class dataloc():
    def __init__(self,project="*",model="*", experiment="*",
                 frequency="*", rip="*",organization=None, url=None):
        """
        Create an entry in the data locations dictionnary for an ensemble of datasets.

        Args:
          project (str,optional): project name
          model (str,optional): model name
          experiment (str,optional): exepriment name
          frequency (str,optional): frequency
          organization (str): name of the organization type, among 
           those handled by :py:func:`~climaf.dataloc.selectLocalFiles`
          url (list of strings): list of URLS for the data root directories

        Each entry in the dictionnary allows to store :
        
         - a list of path or URLS, which are root paths for
           finding some sets of datafiles which share a file organization scheme
         - the name for the corresponding data files organization scheme. The current set of known
           schemes is :

           - CMIP5_DRS : any datafile organized after the CMIP5 data reference syntax, such as on IPSL's Ciclad and CNRM's Lustre
           - OCMIP5_Ciclad : OCMIP5 data on Ciclad
           - OBS4MIPS_CNRM : Obs4MIPS data managed by VDR on CNRM's Lustre
           - OBS_CAMI : Reference observation set managed by VDR and ASTER on CNRM's Lustre
           - EM : (not yet working) CNRM-CM post-processed outputs as organized using EM
           - example : the data included in CliMAF package

           Please ask the CliMAF dev team for implementing further organizations. It is quite quick for data
           which are on the filesystem. Organizations considered for future implementations are :

           - NetCDF model outputs as available during an ECLIS or ligIGCM simulation
           - generic data organization described by the user using patterns
           - ESGF
           
         - the set of attributes which define the experiments which data are 
           stored at that URLS and with that organization

        For the sake of brievity, each attribute can have the '*'
        wildcard value; when using the dictionnary, the most specific
        entries will be used (whic means : the entry (or entries) with the lowest number of wildcards)

        Example :

         - Declaring that all IPSLCM-Z-HR data for project PRE_CMIP6 are stored under a single root path and folllows organization named CMIP6_DRS::
            
            >>> cdataloc(project='PRE_CMIP6', model='IPSLCM-Z-HR', organization='CMIP6_DRS', url=['/prodigfs/esg/'])
            
         - and declaring an exception for one experiment (here, both location and organization are supposed to be different)::
            
            >>> cdataloc(project='PRE_CMIP6', model='IPSLCM-Z-HR', experiment='my_exp', organization='EM', url=['~/tmp/my_exp_data'])

                
        """
        self.project=project
        self.model=model
        self.experiment=experiment
        self.frequency=frequency
        self.organization=organization
        if (isinstance(url,list)) : self.urls=url
        else :
            if re.findall("^esgf://.*",url) : self.organization="ESGF"
            self.urls=[url]
        # Register new dataloc only if not already registered
        if not (any([ l == self for l in locs])) : locs.append(self)
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)        
    def __str__(self):
        return self.model+self.project+self.experiment+self.frequency+self.organization+`self.urls`
    def pr(self):
        print "For model "+self.model+" of project "+ self.project +\
              " for experiment "+self.experiment+" and freq "+self.frequency +\
              " locations are : " + `self.urls` + " and org is :" + self.organization

 
def getlocs(project="*",model="*",experiment="*",frequency="*"):
    """ Returns the list of org,freq,url triples which may match the 
    list of given attributes values (allowing for wildcards '*') and which have 
    the lowest number of wildcards (*) in attributes 

    """
    rep=[]
    for loc in locs :
        stars=0
        # loc.pr()
        if ( loc.project == "*" or project==loc.project ) :
            if ( loc.project == "*" or project=="*" ) : stars+=1
            if ( loc.model == "*" or model==loc.model ) :
                if ( loc.model == "*" or model=="*" ) : stars+=1
                if ( loc.experiment == "*" or experiment==loc.experiment ) :
                    if ( loc.experiment == "*" or experiment=="*" ) : stars+=1
                    if ( loc.frequency == "*" or frequency==loc.frequency ) :
                        if ( loc.frequency == "*" or frequency=="*" ) : stars+=1
                        rep.append((loc.organization,loc.frequency,loc.urls,stars))
                        # print("appended")
    # Must mimimize the number of '*' ? (allows wildcards in dir names, avoid too generic cases)
    # When multiple answers with wildcards, return the ones with the lowest number
    filtered=[]
    mini=100
    for org,freq,url,stars in rep :
        if (stars < mini) : mini=stars
    for org,freq,url,stars in rep :
        if (stars==mini) : filtered.append((org,freq,url))
    # Should we further filter ?
    return(filtered)


def oneVarPerFile(project="*",model="*",experiment="*",frequency="*"):
    org,freq,llocs=getlocs(project,model,experiment,frequency)
    if len(llocs) > 1 :
        logging.warning("dataloc.oneVarPerFile : cannot yet handle case of multiple locs "+\
                         " for experiment "+experiment+", model "+model+" , and project "+project)
        return(False)
    else :
        org=llocs[0][0]
        if org=="EM"          : return False
        if org=="example"     : return False
        if org=="ESGF"        : return True
        if org=="CMIP5_DRS"   : return True
        if (org == "OCMIP5_Ciclad") : return True
        if (org == "OBS4MIPS_CNRM") : return True
        if (org == "OBS_CAMI")      : return True
        logging.warning("dataloc.oneVarPerFile : cannot yet handle organization "+
                        m.organization+ " for experiment "+experiment+
                        ", model "+model+" , and project "+project)
        return False
        

def isLocal(project, model, experiment, frequency) :
    ofu=getlocs(project=project, model=model, experiment=experiment, frequency=frequency) 
    if (len(ofu) == 0 ) : return False
    rep=True
    for org,freq,llocs in ofu :
        for l in llocs :
            if re.findall(".*:.*",l) : rep=False
    return rep

def selectLocalFiles(project, model, experiment, frequency, variable, period, rip="r1i1p1", version="last"):
    """
    Returns the shortest list of (local) files which include the data for the dataset
    
    Method : depending on the data organization, select the relevant files for the
    requested period and variable, using datalocations indexed by :py:func:`dataloc`, and based
    on the datafiles organization for the corresponding datasets; each organization has a
    corresponding filename search function sur as :py:func:selectCmip5DrsFiles

    Known organizations as of today: EM, CMIP5_DRS, OCMIP5_Ciclad, OBS4MIPS_CNRM, OBS_CAMI
    
    """
    rep=[]
    ofu=getlocs(project=project, model=model, experiment=experiment, frequency=frequency)
    logging.debug("dataloc.selectLocalFiles : locs="+ `ofu`)
    if ( len(ofu) == 0 ) :
        logging.warning("dataloc.selectLocalFiles : no datalocation found for %s %s %s %s "%(project, model, experiment, frequency))
    for org,freq,urls in ofu :
        if (org == "EM") :
            rep.extend(selectEmFiles(experiment, frequency, variable, period))
        elif (org == "example") :
            rep.extend(selectExampleFiles(experiment, frequency, variable, period, urls))
        elif (org == "CMIP5_DRS") :
            rep.extend(selectCmip5DrsFiles(project, model, experiment, frequency, variable, period, rip, version, urls))
        elif (org == "OCMIP5_Ciclad") :
            rep.extend(selectOcmip5CicladFiles(project, model, experiment, frequency, variable, period, urls))
        elif (org == "OBS4MIPS_CNRM") :
            rep.extend(selectObs4mipsCnrmFiles(model, frequency, variable, period, urls))
        elif (org == "OBS_CAMI") :
            rep.extend(selectCamiObsFiles(model, frequency, variable, period, urls))
        else :
            logging.error("dataloc.selectLocalFiles : cannot process organization "+org+ \
                             " for experiment "+experiment+" and model "+model+\
                             " of project "+project)
    if (not ofu) :
        return None
    else :
        if (len(rep) == 0 ) :
            logging.warning("dataloc.selectLocalFiles : no file found for variable : %s, period : %s, and rip : %s , at these data locations %s , for model : %s, experiment : %s frequency : %s "%(variable, `period`, rip,  `urls`,model,experiment,frequency))
            return None
    # Discard duplicates (assumes that sorting is harmless for later processing)
    rep.sort()
    last=None
    for f in rep :
        if f == last : rep.remove(last)
        last=f
    # Assemble filenames in one single string
    return(string.join(rep))

def selectEmFiles(experiment, frequency, variable, period) :
    #POur A et L : mon, day1, day2, 6hLev, 6hPlev, 3h
    freqs={ "monthly" : "mon" }
    f=frequency
    if f in freqs : f=freqs[f]
    rep=[]
    # Must look for all realms, here identified by a single letter
    for realm in ["A", "L", "O", "I" ] :
        # Use external function em_get_archive_location for finding data dir
        try :
            ex = subprocess.Popen(["em_get_archive_location", experiment, realm, f], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except :
            logging.debug("dataloc.selectEmFiles: Issue with "
                          "em_get_archive_location on "+experiment+" for realm "+realm)
            break
        if ex.wait()==0 :
            dir=ex.stdout.read().split(" ")[0]
            if os.path.exists(dir) :
                logging.debug("dataloc.selectEmFiles : Looking at dir "+dir)
                lfiles= os.listdir(dir)
                for fil in lfiles :
                    logging.debug("dataloc.selectEmFiles: Looking at file "+fil)
                    fileperiod=periodOfEmFile(fil,realm,f)
                    if fileperiod and period.intersects(fileperiod) :
                        if fileHasVar(fil,variable) :
                            rep.append(dir+"/"+fil)
    return rep

def periodOfEmFile(filename,realm,freq):
    """
    Return the period covered by a file handled by EM, based on filename
    rules for EM
    """
    if (realm == 'A' or realm == 'L' ) :
        if freq=='mon':
            year=re.sub(r'^.*([0-9]{4}).nc',r'\1',filename)
            if year.isdigit(): 
                speriod="%s-%d"%(year,int(year)+1)
                return init_period(speriod)
        else:
            logging.error("dataloc.periodOfEmFile : can yet handle only "
                          "monthly frequency for realms A and L - TBD")
    elif (realm == 'O' or realm == 'I' ) :
        logging.error("dataloc.periodOfEmFile : cannot yet handle realms O and I - TBD - please complain !")
    else: logging.error("dataloc.periodOfEmFile : unexpected realm "+realm)


                        
def selectExampleFiles(experiment, frequency, variable, period, urls) :
    rep=[]
    if (frequency == "monthly") :
        for l in urls :
            for realm in ["A","L"] :
                #dir=l+"/"+realm+"/Origin/Monthly/"+experiment
                dir=l+"/"+realm
                logging.debug("dataloc.selectExampleFiles : Looking at dir "+dir)
                if os.path.exists(dir) :
                    lfiles= os.listdir(dir)
                    for f in lfiles :
                        logging.debug("dataloc.selectExampleFiles: Looking at file "+f)
                        fileperiod=periodOfEmFile(f,realm,'mon')
                        if fileperiod and fileperiod.intersects(period) :
                            if fileHasVar(dir+"/"+f,variable) :
                                rep.append(dir+"/"+f)
                            #else: print "No var ",variable," in file", dir+"/"+f
    return rep
                        

def selectCmip5DrsFiles(project, model, experiment, frequency, variable, period, rip, version, urls) :
    # example for path : CMIP5/output1/CNRM-CERFACS/CNRM-CM5/1pctCO2/mon/atmos/
    #      Amon/r1i1p1/v20110701/clivi/clivi_Amon_CNRM-CM5_1pctCO2_r1i1p1_185001-189912.nc
    # We use wildcards for : lab, realm and MIP_table
    # second path segment can be any string (allows for : output,output1, merge...), but if 'merge' exists, it is 
    # used alone
    # If version is 'last', tries provide version from directory 'last' if available, otherwise those of last dir
    rep=[]
    frequency2drs=dict({'monthly':'mon'})
    freqd=frequency
    if frequency in frequency2drs : freqd=frequency2drs[frequency]
    for l in urls :
        pattern1=l+"/"+project+"/merge"
        if not os.path.exists(pattern1) : pattern1=l+"/"+project+"/*"
        patternv=pattern1+"/*/"+model+"/"+experiment+"/"+freqd+"/*/*/"+rip
        # Get version directories list
        ldirs=glob.glob(patternv)
        #print "looking at "+patternv+ " gives:" +`ldirs`
        for repert in ldirs :
            lversions=os.listdir(repert)
            lversions.sort()
            #print "lversions="+`lversions`+ "while version="+version
            cversion=version
            if (version == "last") :
                if (len(lversions)== 1) : cversion=lversions[0]
                elif (len(lversions)> 1) :
                    if "last" in lversions : lversions=["last"]
                    else : version=lversions[-1] # Assume that order provided by sort() is OK
            #print "checkinv version "+`lversions`+" against"+cversion
            if cversion in lversions :
                lfiles=glob.glob(repert+"/"+cversion+"/"+variable+"/*.nc")
                #print "listing "+repert+"/"+cversion+"/"+variable+"/*.nc"
                for f in lfiles :
                    logging.debug("dataloc.selectCmip5DrsFiles : checking period for "+ f)
                    regex=r'^.*([0-9]{4}[0-9]{2}-[0-9]{4}[0-9]{2}).nc$'
                    fileperiod=init_period(re.sub(regex,r'\1',f))
                    if fileperiod is not None : 
                        if (period.start <= fileperiod.end and period.end >= fileperiod.start) :
                            rep.append(f) 
    return rep

def selectOcmip5CicladFiles(project, model, experiment, frequency, variable, period, urls):
    rep=[]
    # [/prodigfs]/OCMIP5/OUTPUT/IPSL/IPSL-CM4/CTL/mon/CACO3/CACO3_IPSL_IPSL-CM4_CTL_1860-1869.nc
    frequency2drs=dict({'monthly':'mon', 'yearly':'yr','year':'yr'})
    freqd=frequency
    if frequency in frequency2drs : freqd=frequency2drs[frequency]
    for l in urls :
        patternv="/"+project+"/OUTPUT/*/"+model+"/"+experiment+"/"+freqd
        ldirs=glob.glob(l+patternv)
        for repert in ldirs :
            lfiles=glob.glob(repert+"/"+variable+"/"+variable+"*.nc")
            for f in lfiles :
                logging.debug("dataloc.selectOcmip5CicladFiles : checking period for "+ f)
                regex=r'^.*_([0-9]*-[0-9]*).nc$'
                fileperiod=init_period(re.sub(regex,r'\1',f))
                if fileperiod is not None : 
                    if (period.start <= fileperiod.end and period.end >= fileperiod.start) :
                        rep.append(f)
    return rep


def selectObs4mipsCnrmFiles(instrument, frequency, variable, period, urls):
    rep=[]
    # [/cnrm/vdr/DATA/Obs4MIPs/netcdf/]monthly_mean/clt_MODIS_L3_C5_200003-201109.nc
    frequency2drs=dict({'monthly':'monthly_mean'})
    freqd=frequency
    if frequency in frequency2drs : freqd=frequency2drs[frequency]
    for l in urls :
        pattern=l+"/"+freqd+"/"+variable+"_"+instrument+"*nc"
        logging.debug("dataloc.selectObs4mipsCnrmFiles : looking at loc "+ l+" for "+pattern)
        lfiles=glob.glob(pattern)
        for f in lfiles :
            logging.debug("dataloc.selectObs4mipsCnrmFiles : checking period for "+ f)
            regex=r'^.*_([0-9]*-[0-9]*).nc$'
            fileperiod=init_period(re.sub(regex,r'\1',f))
            if fileperiod is not None : 
                if (period.start <= fileperiod.end and period.end >= fileperiod.start) :
                    rep.append(f)
    return rep

def selectCamiObsFiles(instrument, frequency, variable, period, urls):
    rep=[]
    # /cnrm/aster/data1/UTILS/cami/V1.7/climlinks/CAYAN/hfls_1m_194601_199803_CAYAN.nc
    frequency2drs=dict({'monthly':'1m'})
    freqd=frequency
    if frequency in frequency2drs : freqd=frequency2drs[frequency]
    for l in urls :
        pattern=l+"/"+instrument+"/"+variable+"_"+freqd+"_"+"*.nc"
        logging.debug("dataloc.selectCamiObsFiles : looking at loc "+ l+" for "+pattern)
        lfiles=glob.glob(pattern)
        for f in lfiles :
            logging.debug("dataloc.selectCamiObsFiles : checking period for "+ f)
            regex=r'^.*_([0-9]*_[0-9]*)_'+instrument+'.nc$'
            fileperiod=init_period(re.sub(regex,r'\1',f))
            if fileperiod is not None : 
                if (period.start <= fileperiod.end and period.end >= fileperiod.start) :
                    rep.append(f)
    return rep


def cliproc_listfiles(loc,variable,period):
    rep=[]
    if (loc.frequency == "monthly") :
        for l in loc.urls :
            for realm in ["A","L"] :
                dir=l+"/"+loc.experiment+"/"+realm
                if os.path.exists(dir) :
                    lfiles= os.listdir(dir)
                    for f in lfiles :
                        year=re.sub(r'^.*([0-9]{4}).nc',r'\1',f)
                        if year.isdigit() and period.hasFullYear(year) : rep.append(dir+"/"+f)
    else :
        logging.error("dataloc.cliproc_listFiles : cannot yet process frequency "+loc.frequency+ \
                         " ( for experiment "+experiment+", model "+model+" , and project "+project+")")
    return(rep)


def test2() :
    dataloc(experiment="SPE",organization="CLIPROC",frequency="*",url="/cnrm/aster/data1/simulations/AR5")
    l=getlocs(experiment="SPE", frequency="monthly")
    #print l
    l=selectLocalFiles(None,None,"SPE","monthly",None,"1800-1800")
    return(l)


if __name__ == "__main__":
    test2()


