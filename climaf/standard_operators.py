"""
Management of CliMAF standard operators

"""
import os

from climaf import __path__ as cpath
from climaf.operators import cscript
from climaf.clogging import clogger

scriptpath=cpath[0]+"/../scripts/" 

def load_standard_operators():
    """ 
    Load CliMAF standard operators. Invoked by standard CliMAF setup

    The operators list also show in variable 'cscripts'
    They are documented elsewhere
    """
    #
    # Compute scripts
    #
    
    cscript('select' ,scriptpath+'mcdo.sh "${operator}" "${out}" "${var}" "${period_iso}" "${domain}" "${alias}" "${units}" "${missing}" ${ins} ',
            commuteWithTimeConcatenation=True, commuteWithSpaceConcatenation=True)
    #
    cscript('ccdo',
            scriptpath+'mcdo.sh ${operator} "${out}" "${var}" "${period_iso}" "${domain}" "${alias}" "${units}" "${missing}" ${ins}')
    #
    cscript('minus', 'cdo sub ${in_1} ${in_2} ${out}',
            commuteWithTimeConcatenation=True, commuteWithSpaceConcatenation=True)
    #
    cscript('space_average',
            scriptpath+'mcdo.sh fldmean "${out}" "${var}" "${period_iso}" "${domain}" "${alias}" "${units}" "${missing}" ${ins}', 
            commuteWithTimeConcatenation=True)
    #
    cscript('time_average' ,
            scriptpath+'mcdo.sh timmean  "${out}" "${var}" "${period_iso}" "${domain}" "${alias}" "${units}" "${missing}" ${ins}' ,
            commuteWithSpaceConcatenation=True)
    #
    cscript('llbox' ,
            scriptpath+'mcdo.sh ""  "${out}" "${var}" "${period_iso}" "${latmin},${latmax},${lonmin},${lonmax}" "${alias}" "${units}" "${missing}" ${ins}',
            commuteWithTimeConcatenation=True, commuteWithSpaceConcatenation=True)
    #
    cscript('regrid' ,
            scriptpath+'regrid.sh ${in} ${in_2} ${out} ${option}',
            commuteWithTimeConcatenation=True, commuteWithSpaceConcatenation=True)
    #
    cscript('regridn' ,
            scriptpath+'regrid.sh ${in} ${cdogrid} ${out} ${option}',
            commuteWithTimeConcatenation=True, commuteWithSpaceConcatenation=True)
    #
    cscript('rescale' ,
            'cdo expr,\"${var}=${scale}*${var}+${offset};\" ${in} ${out}',
            commuteWithTimeConcatenation=True, commuteWithSpaceConcatenation=True)
    #
    cscript('mean_and_std',
            scriptpath+'mean_and_std.sh ${in} ${var} ${out} ${out_sdev}', 
            # This tells CliMAF how to name output 'sdev' using input variable name
            sdev_var="std(%s)" , 
            commuteWithTimeConcatenation=True)
    #
    # Declare plot scripts
    cscript('ncview'    ,'ncview ${in} 1>/dev/null 2>&1&' )
    #
    cscript('timeplot', 'ncl '+scriptpath+'timeplot.ncl infile=\'\"${in}\"\' outfile=\'\"${out}\"\' '
            'var=\'\"${var}\"\' title=\'\"${title}\"\'',format="png")
    #
    cscript('plot'     , '(ncl -Q '+ scriptpath +'gplot.ncl infile=\'\"${in}\"\' '
            'plotname=\'\"${out}\"\' cmap=\'\"${color}\"\' vmin=${min} vmax=${max} vdelta=${delta} '
            'var=\'\"${var}\"\' title=\'\"${title}\"\' scale=${scale} offset=${offset} units=\'\"${units}\"\' '
            'linp=${linp} levels=\'\"${levels}\"\' proj=\'\"${proj}\"\' contours=${contours} focus=\'\"${focus}\"\' && '
            'convert ${out} -trim ${out}) ', format="png")        
    #
    cscript('lines'     , '(ncl -Q '+ scriptpath +'lineplot.ncl infile=\'\"${mmin}\"\' '
            'plotname=\'\"${out}\"\' var=\'\"${var}\"\' title=\'\"${title}\"\' '
            'linp=${linp} labels=\'\"${labels}\"\'  colors=\'\"${colors}\"\'  thickness=${thickness}'
            'T_axis=\'\"${T_axis}\"\' fmt=\'\"${fmt}\"\'  && '
            'convert ${out} -trim ${out}) ', format="png")

    if (os.system("type cdfmean >/dev/null 2>&1")== 0 ) :
        load_cdftools_operators()
    else :
        clogger.warning("No Cdftool available")

    

def load_cdftools_operators():
    #
    # CDFTools operators 
    #
    # cdfmean
    #
    cscript('ccdfmean',
            'cdfmean ${in} ${var} ${pos_grid} ${imin} ${imax} ${jmin} ${jmax} ${kmin} ${kmax} ${opt}; ncks -O -x -v mean_${var} cdfmean.nc ${out}; rm -f cdfmean.nc cdfmean.txt')
    #
    cscript('ccdfmean_profile',
            'cdfmean ${in} ${var} ${pos_grid} ${imin} ${imax} ${jmin} ${jmax} ${kmin} ${kmax} ${opt}; ncks -O -x -v mean_3D${var} cdfmean.nc ${out}; rm -f cdfmean.nc cdfmean.txt')
    #    
    cscript('ccdfvar',
            'cdfmean ${in} ${var} ${pos_grid} ${imin} ${imax} ${jmin} ${jmax} ${kmin} ${kmax} -var ${opt}; ncks -O -x -v mean_${var},mean_3D${var},var_${var} cdfmean.nc ${out}; rm -f cdfmean.nc cdfmean.txt cdfvar.txt')
    #    
    cscript('ccdfvar_profile',
            'cdfmean ${in} ${var} ${pos_grid} ${imin} ${imax} ${jmin} ${jmax} ${kmin} ${kmax} -var ${opt}; ncks -O -x -v mean_${var},mean_3D${var},var_3D${var} cdfmean.nc ${out}; rm -f cdfmean.nc cdfmean.txt cdfvar.txt')
    
    #
    # cdftransport : case where VT file must be given 
    #
    cscript('ccdftransport',
            scriptpath+'cdftransport.sh ${in_1} ${in_2} ${in_3} ${in_4} ${in_5} ${in_6} ${imin} ${imax} ${jmin} ${jmax} "${opt1}" "${opt2}" ${out} ${out_htrp} ${out_strp}')
    
    #
    # cdfheatc 
    #
    cscript('ccdfheatc',
            'echo ""; tmp_file=`echo $(mktemp /tmp/tmp_file.XXXXXX)`; cdo merge ${in_1} ${in_2} $tmp_file; cdfheatc $tmp_file ${imin} ${imax} ${jmin} ${jmax} ${kmin} ${kmax} ${opt}; rm -f $tmp_file')
   
    # 
    # cdfsections 
    #
    cscript('ccdfsections',
            scriptpath+'cdfsections.sh ${in_1} ${in_2} ${in_3} ${in_4} ${in_5} ${larf} ${lorf} ${Nsec} ${lat1} ${lon1} ${lat2} ${lon2} ${n1} "${more_points}" ${out} ${out_Utang} ${out_so} ${out_thetao} ${out_sig0} ${out_sig1} ${out_sig2} ${out_sig4}') 
    #
    # cdfmxlheatc
    #
    cscript('ccdfmxlheatc',
            'echo ""; tmp_file=`echo $(mktemp /tmp/tmp_file.XXXXXX)`; cdo merge ${in_1} ${in_2} $tmp_file; cdfmxlheatc $tmp_file ${opt}; mv mxlheatc.nc ${out}; rm -f mxlheatc.nc $tmp_file')

    #
    # cdfstd
    #
    cscript('ccdfstd',
            'cdfstd ${opt} ${ins}; mv cdfstd.nc ${out}; rm -f cdfstd.nc')
    #
    cscript('ccdfstdmoy',
            'cdfstd -save ${opt} ${ins}; mv cdfstd.nc ${out}; mv cdfmoy.nc ${out_moy} ; rm -f cdfstd.nc cdfmoy.nc')
    
    #
    # cdfvT
    #
    cscript('ccdfvT', 'cdfvT ${in_1} ${in_2} ${in_3} ${in_4}; mv vt.nc ${out}; rm -f vt.nc')
    #
