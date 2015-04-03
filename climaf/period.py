"""  Basic types and syntax for managing time periods in CLIMAF 

"""

# S.Senesi 08/2014 : created

import re, datetime
from clogging import clogger

class cperiod():
    """
    A class for handling a pair of datetime objects defining a period.

    Period is defined as [ date1, date2 ]. Resolution for date2 is 1 minute
    Attribute 'pattern' usually provides a more condensed form

    """
    def __init__(self,start,end,pattern=None) :
        if not isinstance(start,datetime.datetime) or not isinstance(end,datetime.datetime) : 
            clogger.error("issue with start or end")
            return(None)
        self.start=start ; self.end=end ;
        #if pattern is None :
        self.pattern=self.__repr__()
        #else:
        self.pattern=pattern
        
    #
    def __repr__(self):
        return "%04d%02d%02d-%04d%02d%02d"%(
              self.start.year,self.start.month,self.start.day,
              self.end.year,self.end.month,self.end.day)
    #
    def iso(self):
        """ Return isoformat(start)-isoformat(end), (with inclusive end, and 1 minute accuracy)
        e.g. : 1980-01-01T00:00:00,1980-12-31T23:59:00
        """
        endproxy = self.end - datetime.timedelta(0,60)  # substract 1 minute
        return "%s,%s"%(self.start.isoformat(),endproxy.isoformat())
    #
    def pr(self) :
        return("%04d%02d%02d%02d%02d-%04d%02d%02d%02d%02d"%(\
              self.start.year,self.start.month,self.start.day,self.start.hour,self.start.minute,
              self.end.year,self.end.month,self.end.day,self.end.hour,self.end.minute))
    #
    def hasFullYear(self,year):
        return( int(year) >= self.start.year and int(year) < self.end.year) 
    #
    def start_with(self,begin) :
        """ If period BEGIN actually begins period SELF, returns the 
        complement of BEGIN in SELF; otherwise returns None """
        if self.start==begin.start and self.end >= begin.end : 
            return cperiod(begin.end,self.end)
    #
    def includes(self,included) :
        """ if period self does include period 'included', returns a pair of
        periods which represents the difference """
        if self.start <= included.start and included.end <= self.end :
            return cperiod(self.start,included.start), 
        cperiod(included.end,self.end)
    #
    def intersects(self,other) :
        """ 
        Returns the intersection of period self and period 'other' if any
        """
        if other :
            start=self.start
            if (other.start > start) : start=other.start
            end=self.end
            if (other.end < end) : end=other.end
            if (start < end) : return cperiod(start,end)

def init_period(dates) :
    """
    Init a CliMAF 'period' object

    Args:
      dates (str): must match YYYY[MM[DD[HH[MM]]]][(-\|_)YYYY[MM[DD[HH[MM]]]]]

    Returns:
      the corresponding CliMAF 'period' object

    Examples :
    
    -  a one-year long period : '1980', or '1980-1980'
    -  a decade : '1980-1989'
    -  one month : '198005'
    -  two months : '198003-198004'
    -  one day : '17890714'
    -  the same single day, in a more complicated way : '17890714-17890714'

    CliMAF internally handles date-time values with a 1 minute accurracy; it can provide date
    information to external scripts in two forms; see keywords 'period' and 'period_iso' in
    :py:func:`~climaf.operators.cscript`
      
    """
    
    start=re.sub(r'^([0-9]{4,12}).*',r'\1',dates)
    # TBD : check that start actually matches a date
    syear  =int(start[0:4])
    smonth =int(start[4:6])  if len(start) > 5  else 1
    sday   =int(start[6:8])  if len(start) > 7  else 1
    shour  =int(start[8:10]) if len(start) > 9  else 0
    sminute=int(start[10:12])if len(start) > 11 else 0
    try :
        s=datetime.datetime(year=syear,month=smonth,day=sday,hour=shour,minute=sminute)
    except :
        clogger.debug("period start string %s is not a date"%start)
        return(NOne)
    #
    end=re.sub(r'.*[-_]([0-9]{4,12})$',r'\1',dates)
    clogger.debug("For dates=%s, start= %s, end=%s"%(dates,start,end))
    done=False
    if (end==dates) :
        # No string found for end of period
        if (len(start)==4 ) : eyear=syear+1 ; emonth=1 ; eday=1 ; ehour=0 
        elif (len(start)==6 ) :
            eyear=syear ; emonth=smonth+1 ;
            if (emonth > 12) :
                emonth=1
                eyear=eyear+1
            eday=1 ; ehour=0 
        elif (len(start)==8 ) :
            eyear=syear ; emonth=smonth ; eday=sday ; ehour=0 
            if (sday > 27) :
                # Must use datetime for handling month length
                e=s+datetime.timedelta(1)
                done=True
            else : eday=sday+1
        elif (len(start)==10 ) :
            eyear=syear ; emonth=smonth ; eday=sday ; ehour=shour+1
            if (ehour > 23) :
                ehour=0
                eday=eday+1
            eday=1 ; ehour=0 
        eminute = 0
    else:
        if len(start) != len(end) :
            clogger.error("Must have same numer of digits for start and end dates")
            return None
        if (len(end)<12)  :
            eminute = 0
        else :
            eminute=int(end[10:12])
        if (len(end)==4 ) : eyear=int(end[0:4])+1 ; emonth=1 ; eday=1 ; ehour=0 
        elif (len(end)==6 ) :
            eyear=int(end[0:4]) ; emonth=int(end[4:6]) ; eday=1 ; ehour=0
            if (emonth > 12) :
                emonth=1
                eyear=eyear+1
        elif (len(end)==8 ) :
            eyear=int(end[0:4]) ; emonth=int(end[4:6]) ; eday=int(end[6:8])  ; ehour=0 
            if (eday > 27) :
                try :
                    #print "trying %d %d %d %d %d"%(eyear,emonth,eday,ehour,eminute)
                    e=datetime.datetime(year=eyear,month=emonth,day=eday,hour=ehour,minute=eminute)
                except:
                    clogger.error("period end string %s is not a date"%end)
                    return None
                e=e+datetime.timedelta(1)
                done=True
            else:
                eday=eday+1
        elif (len(end)==10 ) :
            eyear=int(end[0:4]) ; emonth=int(end[4:6]) ; eday=int(end[6:8])  ; ehour=int(end[8:10])+1 
            if (ehour > 23) :
                ehour=0
                eday=eday+1
    #
    if not done :
        try :
            e=datetime.datetime(year=eyear,month=emonth,day=eday,hour=ehour,minute=eminute)
        except:
            clogger.error("period end string %s is not a date"%end)
            return None
    # yearstart=False
    # if len(end) < 6 :
    #     eyear+=1
    #     yearstart=True
    # if len(end) < 8 and (not yearstart) : emonth+=1
    # if (emonth > 12) :
    #     emonth=1
    #     eyear+=1
    #
    if s < e :
        return cperiod(s,e,None)
    else :
        clogger.error("Must have start before (or equals to) end "+`s`+`e`)

