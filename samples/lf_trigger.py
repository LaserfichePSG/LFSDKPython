import sys
import os

DEBUG = False
# Hack for running pdb under ipy. Local path not automatically added to sys
if 'pdb' in sys.modules:
    sys.path.insert(0, os.getcwd())
    DEBUG = True
#add parent folder to sys path - so that we can load the wrapper and environment variables
sys.path.insert(0, os.pardir)

from environment import Environment
from lf_wrapper import LFWrapper
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", type=str, required=True,
                        help="")
    parser.add_argument("-r", "--repo", type=str, required=True,
                        help="")
    parser.add_argument("-u", "--username", type=str, default=None,
                        help="")
    parser.add_argument("-p", "--password", type=str, default=None,
                        help="")
    parser.add_argument("-i", "--input", type=str,
                        help="Path to an input file for triggering.  The file should contain an entry id on each line.")

    return parser.parse_args()

def create_lf_connection(server, database, username, password):
    LF = LFWrapper(Environment())
    LF.LoadRA("10.0", "RepositoryAccess")
    
    if username == None:
        LF.Connect(server=server, database=database)
    else:
        LF.Connect(server=server, database=database, username=username, password=password)
    return LF

def trigger_entry(entryId, LF):
    print "Updating Entry {}".format(entryId)
    entry = LF.Entry.GetEntryInfo(entryId, LF._lf_session)
    entry.RenameTo("WF TRIGGER", LF.EntryNameOption.AutoRename)
    entry.Save()

def main():
    args = parse_args()
    input = args.input
    creds = (args.server, args.repo, args.username, args.password)

    LF = create_lf_connection(*creds)
    with (open(input) if input != None else sys.stdin) as fs:
        for line in [l.rstrip() for l in fs]:
            entryId = int(line)
            trigger_entry(entryId, LF)

if __name__ == "__main__":
    main()
