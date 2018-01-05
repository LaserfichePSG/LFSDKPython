import sys
import os
import clr
import argparse
clr.AddReference("System")
clr.AddReference("System.Reflection")
from System import *
from System.Reflection import *

#add parent folder to sys path - so that we can load the wrapper and environment variables
sys.path.insert(0, os.pardir)

from environment import Environment
from lf_wrapper import *

LF = LFWrapper(Environment())
LF.LoadRA('10.0', 'RepositoryAccess')

#retrieve the Laserfiche user with the provided ID
def GetUser (LF, id):
    LF.Connect()
    groups = ''
    output = LF.Account.GetInfo(id, LF._lf_session)
    for x in output.Groups.Unbox():
        groups += (x + ";")
    groups = groups[:-1]
    print {"id": output.Id.Unbox(), "name": output.Name.Unbox(), "groups": groups, "featureRights": output.FeatureRights.Unbox(), "privileges": output.Privileges.Unbox()}
    LF.Disconnect()

#retrieve all Laserfiche users
def GetUsers (LF):
    LF.Connect()
    result = []
    output = LF.Account.EnumUsers(LF._lf_session)
    while output.Read().Unbox() == True:
        result.append({"id": output.Item.Id.Unbox(), "name": output.Item.Name.Unbox()})
    print result
    LF.Disconnect()

#create a Laserfiche user with the provided data
def CreateUser (LF, data):
    LF.Connect()
    shell = LF.UserInfo()
    shell.Session = LF._lf_session
    shell.Name = data["name"]
    shell.Password = data["password"]
    shell.FeatureRights = data["featureRights"]
    shell.Privileges = data["privileges"]
    for x in data["groups"]:
        try:
            shell.JoinGroup(x)
        except Exception as e:
            pass
    shell = LF.Account.Create(shell, True, LF._lf_session)
    print {"id": shell.Id.Unbox(), "name": shell.Name.Unbox(), "groups": data["groups"], "featureRights": shell.FeatureRights.Unbox(), "privileges": shell.Privileges.Unbox()}
    LF.Disconnect()
    
#delete the Laserfiche user with the provided ID
def DeleteUser(LF, id):
    LF.Connect()
    target = LF.Account.GetInfo(id, LF._lf_session)
    target.Delete()
    target.Save()
    print 'Account Deleted!'
    LF.Disconnect()

#parse arguments from the command line
def parse_args():
    parser = argparse.ArgumentParser(description='Perform repository user maintenance...')
    parser.add_argument('--method', '-m', type=str,
                        help='Method to execute. Options are: GetUser, GetUsers, CreateUser, DeleteUser')
    parser.add_argument('--id', '-i', type=int,
                        help='ID specifying a user account. Required for GetUser, DeleteUser')
    parser.add_argument('--name', '-n', type=str,
                        help='Name of user account. Required for CreateUser')
    parser.add_argument('--password', '-pw', type=str,
                        help='Password of user account. Required for CreateUser')
    parser.add_argument('--featrights', '-f', type=int,
                        help='Feature rights of user account. Required for CreateUser')
    parser.add_argument('--privs', '-pr', type=int,
                        help='Privileges of user account. Required for CreateUser')
    parser.add_argument('--groups', '-g', type=str,
                        help='Comma-separated list of groups for user account. Required for CreateUser')
  
    return parser.parse_args()


#main execution
def main ():
    try:
        args = parse_args()
        method = args.method
        if method == "GetUser":
            id = args.id
            return GetUser(LF, id)
        elif method == "GetUsers":
            return GetUsers(LF)
        elif method == "CreateUser":
            name = args.name
            password = args.password
            feats = args.featrights
            privs = args.privs
            gs = args.groups.split(',')
            data = {"name": name, "password": password, "featureRights": feats, "privileges": privs, "groups": gs}
            return CreateUser(LF, data)
        elif method == "DeleteUser":
            id = args.id
            return DeleteUser(LF, id)
        else:
            raise Exception("Provided method not supported! Valid methods are: GetUser, GetUsers, CreateUser, DeleteUser. Use --method or -m to specify.")
    except Exception as e:
        print e
    
#entry point
if __name__ == "__main__":
    main()