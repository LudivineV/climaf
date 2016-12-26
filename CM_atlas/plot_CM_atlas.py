from climaf.api import *
from LMDZ_SE_atlas.lmdz_SE import *

StringFontHeight=0.019

from climaf.plot.ocean_plot_params import dict_plot_params as ocean_plot_params
ocean_variables=[]
for oceanvar in ocean_plot_params: ocean_variables.append(oceanvar)



def build_period_str(dat):
    ds_dat = ds(**dat)
    if 'clim_period' in dat:
        tmp_period = dat['clim_period']
    elif 'years' in dat:
        tmp_period = dat['years']
    else:
        tmp_period = str(ds_dat.period)
    return tmp_period

def build_plot_title(model,ref,add_product_in_title=True):
    if not ref: add_product_in_title=False
    ds_model = ds(**model)
    if 'customname' in model:
        title = model['customname']
    else:
        if 'model' in ds_model.kvp:
           title = ds_model.kvp['model']+' '+ds_model.kvp['simulation']
        else:
           title = '' #lv ('OBS' if model['project']=='LMDZ_OBS' else ds_model.kvp["product"])
    if add_product_in_title:
        ds_ref = ds(**ref)
        print 'ref = ',ref
        if 'model' in ds_ref.kvp:
            ref_in_title = (ref['customname'] if 'customname' in ref else ds_ref.kvp['model']+' '+ds_ref.kvp['simulation'])
        else:
            ref_in_title = '' #lv ('OBS' if ref['project']=='LMDZ_OBS' else ds_ref.kvp["product"])
        title = title+' (vs '+ref_in_title+')'
    return title

def safe_mode_cfile_plot(myplot,do_cfile=True,safe_mode=True):
    if not do_cfile:
       return myplot
       #
    else:
       # -- We try to 'cfile' the plot
       if not safe_mode:
          print '-- plot function is not in safe mode --'
          return cfile(myplot)
       else:
          try:
             plot_filename = cfile(myplot)
             print '--> Successfully plotted ',myplot
             return plot_filename
          except:
             # -- In case it didn't work, we try to see if it comes from the availability of the data
             print '!! Plotting failed ',myplot
             print "set clog('debug') and safe_mode=False to identify where the plotting failed"
             return ''







# -- 2D Maps
def plot_climato(var, dat, season, proj, domain={}, custom_plot_params={}, do_cfile=True, mpCenterLonF=None, remapping=False,
                 cdogrid='r360x180', safe_mode=True, ocean_variables=ocean_variables, spatial_anomalies=False):
    #
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    print 'var = ',var
    if isinstance(var, dict):
       wvar = var.copy()
       variable = wvar['variable']
       wvar.pop('variable')
       if 'season' in wvar:
           season = wvar['season']
           wvar.pop('season')
       if 'spatial_anomalies' in wvar:
           spatial_anomalies = wvar['spatial_anomalies']
           wvar.pop('spatial_anomalies')
       if 'cdogrid' in wvar:
           cdogrid = wvar['cdogrid']
           wvar.pop('cdogrid')
       if 'proj' in wvar:
           proj = wvar['proj']
           wvar.pop('proj')
       if 'domain' in wvar:
           domain = wvar['domain']
           wvar.pop('domain')
       if 'remapping' in wvar:
           remapping = wvar['remapping']
           wvar.pop('remapping')
    else:
       variable = var
    #
    # -- Add the variable and get the dataset
    wdat = dat.copy()
    wdat.update(dict(variable=variable))
    print wdat
    ds_dat = ds(**wdat)
    print 'ds_dat',ds_dat
    #
    # -- Compute the seasonal climatology
    climato_dat = clim_average(ds_dat,season)
    #
    # -- Computing the spatial anomalies if needed (notably for zos)
    if spatial_anomalies: climato_dat = fsub(climato_dat,str(cvalue(space_average(climato_dat))))
    #
    # -- If we are working on 3D atmospheric variable, compute the zonal mean
    if is3d(variable): climato_dat = zonmean(climato_dat)
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(dat)
    # 
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    title = build_plot_title(dat, None)
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    p = plot_params(variable,'full_field',custom_plot_params=custom_plot_params)
    #
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnLeftString   = tmp_period,
                  gsnCenterString = variable,
                  gsnRightString  = season))
    #
    # -- If the variable is 3d, add the plotting parameters that are specific to the
    # -- zonal mean fields
    if is3d(variable): p.update(dict(aux_options='cnLineThicknessF=2|cnLineLabelsOn=True'))
    #
    # -- If the variable is an ocean variable, set mpCenterLonF=200 (Pacific centered)
    if variable in ocean_variables:
       p.update(dict(mpCenterLonF=200))
       # -- The user can decide to regrid or not the dataset, unless domain is specified
       if domain: remapping=True
       if remapping: climato_dat = regridn(climato_dat,cdogrid=cdogrid)
    #
    # -- Add the projection
    p.update(dict(proj=proj))
    #
    # -- Select a lon/lat box and discard mpCenterLonF (or get it from var)
    if domain:
       climato_dat = llbox(climato_dat, **domain)
       if 'mpCenterLonF' in p: p.pop('mpCenterLonF')
       if proj=='GLOB': p.pop('proj')
    else:
       p.update(dict(options='gsnAddCyclic=True'))
    #
    # -- Update p (the plotting parameters) with the dictionary of var
    if isinstance(var, dict):
       # -- If the user wants to pass the isolines with min, max, delta, we remove colors
       if 'delta' in var and 'colors' in p:
          p.pop('colors')
       p.update(wvar)
    #
    # -- Call the climaf plot function
    myplot = plot(climato_dat,
                  title = title,
                  gsnStringFontHeightF = StringFontHeight,
                  **p)
    #
    # -- If the user doesn't want to do the cfile within plot_climato, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)
#


def plot_diff(var, model, ref, season='ANM', proj='GLOB', domain={}, add_product_in_title=True,
              ocean_variables=ocean_variables, cdogrid='r360x180', remapping=True, add_climato_contours=True,
              safe_mode=True, custom_plot_params={}, do_cfile=True, spatial_anomalies=False):
    #
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    print 'var = ',var
    if isinstance(var, dict):
       wvar = var.copy()
       variable = wvar['variable']
       wvar.pop('variable')
       if 'season' in wvar:
           season = wvar['season']
           wvar.pop('season')
       if 'spatial_anomalies' in wvar:
           spatial_anomalies = wvar['spatial_anomalies']
           wvar.pop('spatial_anomalies')
       if 'cdogrid' in wvar:
           cdogrid = wvar['cdogrid']
           wvar.pop('cdogrid')
       if 'proj' in wvar:
           proj = wvar['proj']
           wvar.pop('proj')
       if 'domain' in wvar:
           domain = wvar['domain']
           wvar.pop('domain')
       if 'remapping' in wvar:
           remapping = wvar['remapping']
           wvar.pop('remapping')
    else:
       variable = var
    #
    # -- Get the datasets of the model and the ref
    wmodel = model.copy() ; wmodel.update(dict(variable=variable))
    wref = ref.copy() ; wref.update(dict(variable=variable))
    ds_model = ds(**wmodel)
    ds_ref   = ds(**wref)
    #
    # -- Compute the seasonal climatology of the reference
    climato_ref = clim_average(ds_ref  ,season)
    #
    # -- Here we treat two cases:
    #       -> the 3D variables: need to compute the zonal means, 
    #          and potentially interpolate on pressure levels with ml2pl
    #       -> the 2D variables:
    #            * only compute the seasonal average for the atmospheric field and regrid the model on the ref (using diff_regrid)
    #            * for ocean variables, regrid on a 1deg lon/lat grid and compute the difference (using diff_regridn)
    #            * Option: we remove the spatial mean if spatial_anomalies=True (notably for SSH)
    # 
    if is3d(variable):
       # -- First case: 3D variable -------------------------------------------- #
       # -- Vertical interpolation (only if needed)
       if 'press_levels' in model:
           # -- To do this the user has to specify 'press_levels' in the dictionary of the dataset, and 'press_var'
           #    if the variable is not 'pres'
           fixed_fields('ml2pl',('press_levels.txt',model['press_levels']))
           ds_pres = ds(variable=(model['press_var'] if 'press_var' in model else 'pres'), **model)
           nds_model = ccdo(ds_model,operator='mulc,1')
           nds_pres = ccdo(ds_pres,operator='mulc,1')
           ds_model = ml2pl(nds_model,nds_pres)
       # -- After the vertical interpolation, compute the climatology
       climato_sim = clim_average(ds_model,season)
       # -- Eventually, compute the zonal mean difference
       try:
          bias = diff_zonmean(climato_sim,climato_ref)
       except:
          print 'No data found for zonal mean for ',climato_ref,climato_sim
          return ''
    else:
       # -- Alternative: 2D variable ------------------------------------------- #
       climato_sim = clim_average(ds_model,season)
       # -- Particular case of SSH: we compute the spatial anomalies
       if spatial_anomalies:
          try:
             climato_sim = fsub(climato_sim,str(cvalue(space_average(climato_sim))))
             climato_ref = fsub(climato_ref,str(cvalue(space_average(climato_ref))))
          except:
             print '==> Error when trying to compute spatial anomalies for ',climato_ref,climato_sim
             print '==> Check data availability'
             return ''
       # -- By default, we regrid the ocean variables on a cdogrid;
       #    If the reference is on the same grid as the model, switch off remapping with remapping=False
       if domain: remapping=True
       if remapping:
          # -- If we work on ocean variables, we regrid both the model and the ref on a 1deg grid
          # -- If not, we regrid the model on the ref
          if variable in ocean_variables:
             bias = diff_regridn(climato_sim,climato_ref,cdogrid=cdogrid)
          else:
             bias = diff_regrid(climato_sim,climato_ref)
       else:
          bias = minus(climato_sim,climato_ref)
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    print 'add_product_title_in_title in plot_diff = ',str(add_product_in_title)
    title = build_plot_title(wmodel,wref,add_product_in_title)
    #
    # -- Check whether the ref is a model or an obs to set the appropriate context
    context = ('model_model' if 'model' in ds_ref.kvp else 'bias')
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    p = plot_params(variable,context,custom_plot_params=custom_plot_params)
    #
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnLeftString   = tmp_period,
                  gsnCenterString = variable,
                  gsnRightString  = season))
    #
    # -- If the variable is 3d, add the plotting parameters that are specific to the
    # -- zonal mean fields
    if is3d(variable): p.update(dict(aux_options='cnLineThicknessF=2|cnLineLabelsOn=True'))
    #
    # -- If the variable is an ocean variable, set mpCenterLonF=200 (Pacific centered)
    if variable in ocean_variables: p.update(dict(mpCenterLonF=200,focus='ocean'))
    #
    # -- Add the projection
    p.update(dict(proj=proj))
    #
    # -- Select a lon/lat box and discard mpCenterLonF (or get it from var)
    if domain:
       bias        = llbox(bias, **domain)
       climato_ref = llbox(climato_ref, **domain)
       if 'mpCenterLonF' in p: p.pop('mpCenterLonF')
       if proj=='GLOB': p.pop('proj')
    else:
       p.update(dict(options='gsnAddCyclic=True'))
    #
    # -- Update p (the plotting parameters) with the dictionary of var
    if isinstance(var, dict):
       if 'delta' in var and 'colors' in p:
          p.pop('colors')
       p.update(wvar)
    #
    # -- Get the corresponding plot parameters for the auxillary field (the climatology of the reference)
    ref_aux_params = plot_params(variable,'full_field',custom_plot_params=custom_plot_params)
    # -- ... and update the dictionary 'p'
    if 'colors' in ref_aux_params:
       p.update(dict(contours=ref_aux_params['colors']))
       # -- We apply the scale and offset with 'offset_aux' and 'scale_aux' to plot the auxillary field
       if 'offset' in ref_aux_params: p.update({'offset_aux':ref_aux_params['offset']})
       if 'scale' in ref_aux_params: p.update({'scale_aux':ref_aux_params['scale']})
       #
       # -- Call the climaf plot function
       myplot = plot(bias,climato_ref,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    else:
       # -- Call the climaf plot function
       myplot = plot(bias,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    #
    # -- If the user doesn't want to do the cfile within plot_diff, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)



