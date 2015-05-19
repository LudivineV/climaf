from climaf.api import *

# Define a dataset, using a built-in pre-defined datafile location
##################################################################
dg=ds(project="example", frequency="monthly", experiment="AMIPV6ALB2G", variable="tas", period="1980-1981")

# Average it over space
#########################################################
ta=space_average(dg)

cshow(timeplot(ta,title="AMIPV6"))
