"""
Standard site settings for working with CliMAF.

"""

import os

atCNRM=False
onCiclad=False
atTGCC=False

if os.path.exists('/ccc'):
    atTGCC=True
if os.path.exists('/cnrm'):
    atCNRM=True
elif os.path.exists('/prodigfs') :
    onCiclad=True

