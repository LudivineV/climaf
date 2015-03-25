import subprocess, sys
import glob
import argparse
from argparse import RawTextHelpFormatter

description="""

Iteration of a set of python scripts, explicit or implicit

"""

#creation d un objet ArgumentParser
parser = argparse.ArgumentParser(description=description, formatter_class=RawTextHelpFormatter,
                                 usage='python %(prog)s [options] \n i.e.  python %(prog)s [-f list_of_file(s)] [-v]')

#declaration des arguments
parser.add_argument("-v", "--verbosity", help="increase output verbosity", action="store_true")
parser.add_argument("-f", "--file", nargs='+', dest='infile',
                    help="list of example filenames we want to test (by default, all examples"
                    " of directory 'climaf/examples' are launched)")

args = parser.parse_args()

#print args
if args.verbosity:
    print "verbosity turned on"

if args.infile:
    vfiles=args.infile
else:
    vfiles = glob.glob('*.py')
    selfs=sys.argv[0]
    if selfs in vfiles : vfiles.remove(sys.argv[0])

#tmp
vfiles.remove('ocmip_ciclad.py')    
#print vfiles, args.infile

for file in vfiles:

    if args.verbosity:
        print "'%s'..." %file,

    ex = subprocess.Popen(["python", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if ex.wait()==0 : #code retour
        if args.verbosity:
            print "Success" 
    else:
        if args.verbosity:
            print ex.stdout.read()
            print ex.stderr.read()
        print "Failure" 
        sys.exit(1)
         
if not args.verbosity:
    print "Success"
