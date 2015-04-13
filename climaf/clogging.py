import logging

def log_l():
    global formatter
    logger = logging.getLogger('')
    # create formatter
    formatter = logging.Formatter('[%(funcName)-10.10s : %(filename)-10s, L. %(lineno)-4d] : %(levelname)-8s : %(message)s')
    return logger
    
clogger=log_l()

def clog(level=None) :
    """
    Sets the verbosity level for CliMAF log messages on stderr.

    Args:
     level : among logging.DEBUG, logging.INFO, logging.WARNING, logging.CRITICAL

    """
    if (level) : clogger.setLevel(transl(level)) 
    exist_stream_handler=False
    for h in clogger.handlers :
        if type(h) is logging.StreamHandler :
            #print "il existe deja un StreamHandler => on change le niveau d informations et on formatte le msg ", h
            #clogger.setLevel(arg) 
            h.setFormatter(formatter)
            exist_stream_handler=True    
            
    if not exist_stream_handler :
        #print "ajout d un StreamHandler"
        console = logging.StreamHandler()
        #console.setLevel(arg)
        console.setFormatter(formatter)
        clogger.addHandler(console)


def clog_file(level=None) :
    """
    Sets the verbosity level for CliMAF log messages on file climaf.log

   Args:
     level : among logging.DEBUG, logging.INFO, logging.WARNING, logging.CRITICAL
    """
    exist_file_handler=False
    for h in clogger.handlers :
        if type(h) is logging.FileHandler :
            #print "il existe deja un FileHandler => on change le niveau d informations", h
            if level : h.setLevel(transl(level))
            exist_file_handler=True    
            
    if exist_file_handler==False:
        #print "ajout d un FileHandler"
        fh = logging.FileHandler('climaf.log',mode='w') 
        if level : fh.setLevel(transl(level))
        fh.setFormatter(formatter)
        clogger.addHandler(fh)

def indent():
    """ 
    Forces log messages to be indented by one more TAB
    """
    global formatter
    form="\t"+getattr(formatter,'_fmt')
    formatter = logging.Formatter(form)
    clog()
    clog_file()

def dedent():
    """ 
    Forces log messages to be de-indented by one TAB
    """
    global formatter
    form=getattr(formatter,'_fmt').replace("\t","",1)
    formatter = logging.Formatter(form)
    clog()
    clog_file()

def transl(level) :
    if type(level) is str:
        if level.lower()=='debug': return logging.DEBUG
        elif level.lower()=='critical': return logging.CRITICAL
        elif level.lower()=='info': return logging.INFO
        elif level.lower()=='warning': return logging.WARNING
    else : return level
