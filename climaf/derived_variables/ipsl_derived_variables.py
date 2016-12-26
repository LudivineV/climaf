from climaf.api import derive

# -- LMDZ

# -- Radiative SW Total at TOA
derive('*','rstt','minus','rsdt','rsut')
# -- Radiative SW Total at surface
derive('*','rsts','minus','rsds','rsus')
# -- Radiative LW Total at surface
derive('*','rlts','minus','rlds','rlus')
# -- Radiative LW Total at surface - CS
derive('*','rltscs','minus','rldscs','rluscs')
# -- Radiative SW Total at surface - CS
derive('*','rstscs','minus','rsdscs','rsuscs')
# -- Radiative SW Total at TOA - CS
derive('*','rsttcs','minus','rsdt'  ,'rsutcs')

# -- Radiative Total at TOA
derive('*','rtt','minus','rstt','rlut')
# -- Radiative Total at surface
derive('*','rts','plus','rsts','rlts')


# -- Cloud radiative effect SW at surface
derive('*','cress','minus','rsds','rsdscs')
# -- Cloud radiative effect SW at surface
derive('*','crels','minus','rlds','rldscs')
# -- Cloud radiative effect Total at surface
derive('*','crets','plus','cress','crels')

# -- Cloud radiative effect SW at TOA
derive('*','crest','minus','rsutcs','rsut')
# -- Cloud radiative effect LW at TOA
derive('*','crelt','minus','rlutcs','rlut')
# -- Cloud radiative effect Total at TOA
derive('*','crett','plus','crest','crelt')

# -- Total Non-radiative Heat Fluxes at surface
derive('*','hfns','plus','hfls','hfss')
# -- Radiative budget at surface
derive('*','bil' ,'minus','rts','hfns')
derive('*','tsmtas','minus','ts','tas')

# -- Atm. LW Heat
derive('*','rlah','minus','rlut','rlts')
# -- Atm. LW Heat - CS (rlahcs)
derive('*','rtmp','plus','rldscs','rlutcs')
derive('*','rlahcs','minus','rlus','rtmp')
# -- Atm. LW Heat - CRE
derive('*','rlahcre','minus','rlah','rlahcs')
#
# -- Atm. SW Heat
derive('*','rsah','minus','rstt','rsts')
# -- Atm. SW Heat - CS (rlahcs)
derive('*','rsahcs','minus','rsttcs','rstscs')
# -- Atm. SW Heat - CRE
derive('*','rsahcre','minus','rsah','rsahcs')

# -- Atm. Total Heat
derive('*','rah','plus','rsah','rlah')
# -- Atm. Total Heat - CS (rlahcs)
derive('*','rahcs','plus','rsahcs','rlahcs')
# -- Atm. Total Heat - CRE
derive('*','rahcre','minus','rah','rahcs')

# -- Planetary albedo at TOA
derive('*','albt','divide','rsut','rsdt')
# -- Planetary albedo at surface
derive('*','albs','divide','rsus','rsds')


# -- Potential Temperature and salinity @ 200m, 1000m and 2000m in depth
derive('*','so200','ccdo','so',operator='intlevel,200 -selname,so')
derive('*','so1000','ccdo','so',operator='intlevel,1000 -selname,so')
derive('*','so2000','ccdo','so',operator='intlevel,2000 -selname,so')
derive('*','to200','ccdo','thetao',operator='intlevel,200 -selname,thetao')
derive('*','to1000','ccdo','thetao',operator='intlevel,1000 -selname,thetao')
derive('*','to2000','ccdo','thetao',operator='intlevel,2000 -selname,thetao')


