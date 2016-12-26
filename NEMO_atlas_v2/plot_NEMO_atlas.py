from climaf.api import *
from CM_atlas.plot_CM_atlas import *
StringFontHeight=0.019



# -- Sea Ice Plots
def plot_sic_climato_with_ref(variable,model,ref,season,proj, add_product_in_title=True,
                              safe_mode=True, custom_plot_params={},do_cfile=True):
    # -- Get the datasets of the model and the ref
    wmodel = model.copy() ; wmodel.update(dict(variable=variable))
    wref = ref.copy()     ; wref.update(dict(variable=variable))
    if wmodel['project']=='CMIP5': wmodel.update(dict(table='OImon'))
    if wref['project']=='CMIP5': wref.update(dict(table='OImon'))
    #
    # -- Get the datasets of the model and the ref
    if wmodel['frequency'] in ['yearly','1Y']: wmodel.update(dict(frequency='monthly'))
    ds_model = ds(**wmodel)
    ds_ref   = ds(**wref)
    #
    # -- Compute the seasonal climatology
    climato_sim = regridn(clim_average(ds_model,season),cdogrid='r360x180')
    climato_ref = clim_average(ds_ref  ,season)
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    title = build_plot_title(model,ref,add_product_in_title)
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    p = plot_params(variable,'full_field',custom_plot_params=custom_plot_params)
    #
    # -- Add the contour of the ref (sic = 15)
    p.update(dict(contours=15))
    #
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnLeftString   = tmp_period,
                  gsnCenterString = variable,
                  gsnRightString  = season))
    # -- Do the plot 
    myplot = plot(climato_sim,climato_ref,
                     title = title,
                     proj=proj,
                     gsnStringFontHeightF = StringFontHeight,
                     options='gsnAddCyclic=True',
                     aux_options='cnLineThicknessF=10',
                     **p)
    #
    # -- If the user doesn't want to do the cfile within plot_diff, set do_cfile=False
    #
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(myplot,do_cfile,safe_mode)




def plot_SIV(models, pole, safe_mode=True, do_cfile=True, maxvalNH=4*1e4, maxvalSH=1.4*1e4, minvalNH=0, minvalSH=0):
   #
   siv_ens_dict = {}
   # -- We loop on the simulations to build an 'ensemble climaf object'
   # -- that will be passed to 'curves'
   for model in models:
       wmodel = model.copy() ; wmodel.update({'table':'OImon'})
       if wmodel['frequency'] in ['yearly','1Y']: wmodel.update(dict(frequency='monthly'))
       # -- Dealing with the area of the grid cells
       model4area = model.copy() ; model4area.update({'period':'fx'})
       areavar = 'areacello'
       if 'gridfile' in wmodel:
           if 'varname_area' in wmodel:
               areavar = wmodel['varname_area']
           area = fds(wmodel['gridfile'],variable=areavar,period='fx')
       else:
           area = ds(variable=areavar, **model4area)
       # -- Get the sea ice concentration (sic) and sea ice thickness (sit)
       sic  = ds(variable='sic', **wmodel)
       sit  = ds(variable='sit', **wmodel)
       # -- Multiply sit by sic (after changing sic from % to ratio [0,1])
       tmp_siv = multiply(sit,ccdo(sic,operator='divc,100'))
       # -- Compute the annuel cycle, and multiply by the area of the grid cells
       siv = multiply(annual_cycle(tmp_siv),area)
       # -- Extract the hemispheres and compute the sum
       if pole=='NH': region = dict(lonmin=0,lonmax=360,latmin=30,latmax=90)
       if pole=='SH': region = dict(lonmin=0,lonmax=360,latmin=-90,latmax=-30)
       
       scyc_siv = ccdo(llbox(siv,**region),operator='fldsum')
       #
       # -- In case you specify a 'customname' for your simulation, it will be used in the plot
       # -- Otherwise we will use the name of the simulation
       if 'customname' in wmodel:
          name_in_plot = wmodel['customname']
       else:
          name_in_plot = wmodel['simulation']
       # -- Build the ensemble (update the python dictionnaries that will be given to cens)
       try:
          cfile(scyc_siv)
          siv_ens_dict.update({name_in_plot:scyc_siv})
       except:
          print 'No data to compute SIV for ',model
   #
   # -- We check if we have found the data to compute SIV for at least one model
   if not siv_ens_dict:
      print 'No data for any model to compute SIV'
      return ''
   else:
      # -- Build the climaf ensembles
      siv_ensemble = cens(siv_ens_dict)
      #cfile(siv_ensemble)
      # -- First, some options used for both hemispheres
      plot_options = 'vpXF=0|'+\
                  'vpWidthF=0.66|'+\
                  'vpHeightF=0.43|'+\
                  'tmXBLabelFontHeightF=0.016|'+\
                  'tmYLLabelFontHeightF=0.014|'+\
                  'lgLabelFontHeightF=0.016|'+\
                  'tmXMajorGrid=True|'+\
                  'tmYMajorGrid=True|'+\
                  'tmXMajorGridLineDashPattern=2|'+\
                  'tmYMajorGridLineDashPattern=2|'+\
                  'xyLineThicknessF=12|'+\
                  'tiYAxisString=Sea Ice Volume|'+\
                  'gsnStringFontHeightF=0.017'
      print 'Plot the Sea Ice Volume for ',models
      # -- And then, do the plots with 'curves'
      if pole == 'NH':
         title = 'Sea Ice Volume Northern Hemisphere'
         minval = minvalNH
         maxval = maxvalNH
      if pole == 'SH':
         title = 'Sea Ice Volume Southern Hemisphere'
         minval = minvalSH
         maxval = maxvalSH
      plot_siv = curves(siv_ensemble, title = title, options=plot_options,scale=1/1e9,scale_aux=1/1e9,
                        X_axis='aligned',min = minval, max=maxval)
   #
   # -- If the user doesn't want to do the cfile within plot_diff, set do_cfile=False
   # -- Otherwise we check if the plot has been done successfully.
   # -- If not, the user can set safe_mode=False and clog('debug') to debug.
   return safe_mode_cfile_plot(plot_siv,do_cfile,safe_mode)




