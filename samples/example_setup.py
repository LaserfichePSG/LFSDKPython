import sys
import os
import argparse
from random import random

DEFAULT_PATH = "Demo #3 Documents"
ERROR_RATE = .33
DEBUG = False

# Hack for running pdb under ipy. Local path not automatically added to sys
if 'pdb' in sys.modules:
    sys.path.insert(0, os.getcwd())
    DEBUG = True
#add parent folder to sys path - so that we can load the wrapper and environment variables
sys.path.insert(0, os.pardir)

from lf_wrapper import LFWrapper
from environment import Environment

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", type=str, required=True,
                        help="File path for the error log.")
    parser.add_argument("-c", "--count", type=int, default=10,
                        help="The number of samples to generate")
    parser.add_argument("-s", "--server", type=str, required=True,
                         help="The LF server you wish to connect to.")
    parser.add_argument("-r", "--repository", type=str, required=True,
                        help="The LF repository you wish to connect to.")
    parser.add_argument("-u", "--username", type=str, default=None,
                        help="The user you wish to connect with. For Windows Authentication omit this flag.")
    parser.add_argument("-p", "--password", type=str, default=None,
                        help="For Windows Authentication omit this flag.")
    
    #parse the command line args and return 
    return parser.parse_args()

def create_lf_connection(server, repo, username, password):
    lf = LFWrapper(Environment())
    lf.LoadRA("10.0", "RepositoryAccess")
    if username is None:
        lf.Connect(server=server, database=repo)
    else:
        lf.Connect(server=server, database=repo, username=username, password=password)
    return lf

def create_documents(lf, count, error_rate):
    outputs = []
    sess = lf._lf_session
    parent = None

    #create the parent folder if necessary
    try:
        parent = lf.Folder.GetFolderInfo(DEFAULT_PATH, sess)
    except:
        root = lf.Folder.GetRootFolder(sess)
        tocid = lf.Folder.Create(root, DEFAULT_PATH, lf.EntryNameOption.AutoRename, sess)
        parent = lf.Folder.GetFolderInfo(DEFAULT_PATH, sess)
   
    for i in range(0, count):
        is_error = random() < error_rate
        doc_name = ("Error Doc {}".format(i)) if is_error else ("Test Doc {}".format(i))
        entryId = lf.Document.Create(parent, doc_name, lf.EntryNameOption.AutoRename, sess).Unbox()

        outputs.append(
            "ERROR - Something went wrong! TOCID={}".format(entryId) if is_error else "SUCCESS - Everything's all good in the hood!"
        )
    return outputs

#Generate a set of sample test documents with some random error rate
#and log errors to the specified log file.
def main():
    args = parse_args()
    creds = (args.server, args.repository, args.username, args.password)
    lf = create_lf_connection(*creds)
    outputs = create_documents(lf, args.count, ERROR_RATE)

    with open(args.log, "w") as fs:
        map(lambda o: fs.write(o + '\n'), outputs) 

    print "Output Written!"

if __name__ == "__main__":
    main()
