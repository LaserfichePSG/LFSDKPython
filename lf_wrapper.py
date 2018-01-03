import sys
import os
import functools

#Define global vars
LF = None
DEBUG = False
# Hack for running pdb under ipy. Local path not automatically added to sys
if 'pdb' in sys.modules:
    sys.path.insert(0, os.getcwd())
    DEBUG = True

# import CLR and environment paths
import clr
clr.AddReference("System")
clr.AddReference("System.Reflection")
from System import *
from System.Reflection import *
from environment import Environment

#TODO:
    #add support for static props/methods in LFModuleWrapper

class LFModuleInstanceWrapper:
    #accepts an instance of an object
    #sets a property capturing the properties of that object instance
    def __init__(self, instance):
        self._instance = instance
        self._calling_method = None
        
        #this is to handle the possibility of void being passed to the constructor
        try:
            self._objProps = self._instance.GetType().GetProperties()
        except:
            pass
        
    #overload to output the object instance and not the wrapper
    def __repr__ (self):
        return self._instance.__repr__()
    
    #overload the attribute getter
    #check the internal object properties first, and return a wrapped instance of the result if it is found
    #otherwise, assume we are calling one of the object's methods, so invoke a helper function to handle that
    def __getattr__ (self, attr):
        for x in range(self._objProps.Length):
            if self._objProps[x].Name == attr:
                return LFModuleInstanceWrapper(self._objProps[x].GetValue(self._instance))
        self._calling_method = attr
        return self._Call
    
    #overload the attribute setter such it properly handles assigning to .NET properties vs. Python properties
    def __setattr__(self, name, value):
        if "_" in name:
            self.__dict__[name] = value
        else:
            for x in range(self._objProps.Length):
                if self._objProps[x].Name == name:
                    if hasattr(value, '_instance'):
                        self._objProps[x].SetValue(self._instance, value._instance)
                    else:
                        self._objProps[x].SetValue(self._instance, value)
    
    #this method facilitates the conversion of basic .NET objects back to Python objects
    def Unbox (self):
        return self._instance
    
    #method to call the appropriate overload of the internal object's methods given the provided arguments
    def _Call (self, *argv):
        if self._calling_method is None:
            raise KeyError("No method has been specified to be called!")
        elif self._calling_method == 'Unbox':
            return self._instance
        method_name = self._calling_method
        types = []
        true_args = []
        for x in argv:
            if hasattr(x, '_instance'):
                types.append(x._instance.GetType())
                true_args.append(x._instance)
            else:
                types.append(type(x))
                true_args.append(x)
        try:
            check = self._instance.GetType().GetMethod(method_name, Array[Type](types)) if len(types) > 0 else self._instance.GetType().GetMethod(method_name, Type.EmptyTypes)
            if check is None:
                raise KeyError("No overload of the provided method exists given the provided argument types!")
            else:
                #return the retrieved method
                return LFModuleInstanceWrapper(check.Invoke(self._instance, Array[Object](true_args)))
        except Exception as e:
            print e.InnerException
            raise e
                
class LFModuleWrapper:
    #accepts a namespace or class
    def __init__(self, module):
        self._module = module
    
    #method to invoke the proper constructor of the given class given the arguments
    #returns LFModuleInstanceWrapper object that is constructed with output object instance of the called constructor
    def _construct (self, argv):
        if self._module is None:
            raise KeyError("No class has been provided!")
        module = self._module
        inpt = clr.GetClrType(module)
        types = []
        true_args = []
        for x in argv:
            if hasattr(x, '_instance'):
                types.append(x._instance.GetType())
                true_args.append(x._instance)
            else:
                types.append(type(x))
                true_args.append(x)
        try:
            check = inpt.GetConstructor(Array[Type](types)) if len(types) > 0 else inpt.GetConstructor(Type.EmptyTypes)
            if check is None:
                raise KeyError("No overload of the provided class constructor exists given the provided argument types!")
            else:
                #return the retrieved method as an instance of LFModuleInstanceWrapper
                 return LFModuleInstanceWrapper(check.Invoke(Array[Object](true_args)))
        except Exception as e:
            print e.InnerException
            raise e
        return self
            
    #overload to output the module and not the wrapper
    def __repr__ (self):
        return self._module.__repr__()
    
    #overload the __get__ to handle static properties and methods
    def __getattr__ (self, attr):
        self._calling_method = attr
        return self._Call
        
    #overload the __call__ to invoke our wrapper constructor (unless no args are provided, in which case just output the module)
    def __call__(self, *argv):
        if argv is None:
            return self._module
        return self._construct(argv)
    
    #method to call the appropriate overload of the static's methods given the provided arguments
    def _Call (self, *argv):
        if self._calling_method is None:
            raise KeyError("No method has been specified to be called!")
        method_name = self._calling_method
        types = []
        true_args = []
        for x in argv:
            if hasattr(x, '_instance'):
                types.append(x._instance.GetType())
                true_args.append(x._instance)
            else:
                types.append(type(x))
                true_args.append(x)
        try:
            check = clr.GetClrType(self._module).GetMethod(method_name, Array[Type](types)) if len(types) > 0 else clr.GetClrType(self._module).GetMethod(method_name, Type.EmptyTypes)
            if check is None:
                raise KeyError("No overload of the provided method exists given the provided argument types!")
            else:
                #return the retrieved method
                return LFModuleInstanceWrapper(check.Invoke(self._module, Array[Object](true_args))) #NEED TO PASS 'null' as first argument to this function
        except Exception as e:
            print e.InnerException
            raise e

# Define an instance of the LF ClR. Valid Args are:
# target = <SDK Target>.  Valid options are:
#       
class LFWrapper:
    def __init__(self, argv):
        '''
        args:
           RepositoryAccess - An object which maps version to a dll on the local disk
           LFSOPaths: An object that maps version numbers to a dll on the local disk
        '''
        def initialize_module_store(paths, val = None):
            output = { }
            for key in paths:
                output[key] = val 
            return output

        self._args = argv
        self._lf_credentials = self._args.LaserficheConnection
        self._loaded_modules = { 
            'LFSO': initialize_module_store(self._args.LFSO_Paths, { }),
            'DocumentProcessor': initialize_module_store(self._args.DocumentProcessor_Paths, { }),
            'RepositoryAccess': initialize_module_store(self._args.RepositoryAccess_Paths, { })
        }
        self._sdk = None
        self._lf_session = None
        self._db = None

    def __repr__(self):
        return 'LF SDK Wrapper'

    # try to pull a target attribute from RA. Search order is DocumentService, RepositoryAccess, SecurityTokenService
    def _get_fromRA(self, module, attr):
        namespaces = dir(module)
        for ns_str in namespaces:
            namespace = module[ns_str] 
            cmds = dir(namespace)
            if attr in cmds:
                target = getattr(namespace, attr) 
                return LFModuleWrapper(target)

        #if no match is found raise an exception
        raise KeyError('Command not found')

    # LFSOd does not have namespacing infront of the methods.  We can check the module dir directly and return
    def _get_fromCOM(self, module, attr):
        for mod in module.keys():
            namespaces = dir(module[mod])
            if attr in namespaces:
                return LFModuleWrapper(getattr(module[mod], attr))
        raise KeyError('Command not found')

    # this is used to overload the property operator for the LFWrapper object
    # it will allow short cut access to SDK objects through the wrapper without having to go through
    # the namespaces or import specific functions from the module.
    def __getattr__(self, attr):
        if self._sdk == None:
            raise Exception('SDK is not loaded')
        else:
            type = self._sdk['type']
            module = self._sdk['module']
            return self._get_fromRA(module, attr) if type == 'RA' else self._get_fromCOM(module, attr)
    
    def Connect(self, **kwargs):
        #helper functions to connect to either LFSO or RA
        def ConnectRA(server, database, username, password):
            if self._lf_session == None:
                if username == '':
                    credentials = (server, database)
                else:
                    credentials = (server, database, username, password)
            else:
                raise Exception('Please load a version of the SDK')
            
            self._lf_session = self.Session.Create(*credentials)
            return self._lf_session
        
        def ConnectLfso(server, database, username, password):
            if self._db == None:
                credentials = (database, server, username, password)
                app = self.LFApplicationClass()
                self._db = app.ConnectToDatabase(*credentials)
            return self._db
        
        def GetDefaultCred(key, arg_list):
            try:
                return arg_list[key]
            except KeyError:
                return self._lf_credentials[key]
            
        #Function Logic Starts here
        #if args are not given pull from environment.py
        server = GetDefaultCred('server', kwargs)
        database = GetDefaultCred('database', kwargs)
        username = GetDefaultCred('username', kwargs) if not 'server' in kwargs or 'username' in kwargs else ''
        password = GetDefaultCred('password', kwargs) if not 'server' in kwargs or 'password' in kwargs else ''
        creds = (server, database, username, password)

        sdk_loaded = self._sdk != None
        if sdk_loaded:
            type = self._sdk['type']
            return ConnectRA(*creds) if type == 'RA' else ConnectLfso(*creds)
        else:
            raise Exception('Please load a version of the SDK')

    def Disconnect(self):
        def DisconnectLfso():
            try:
                self._db.CurrentConnection.Terminate()
            except:
                print 'Could not close LFSO connection. Please ensure that you have opened one!'

        def DisconnectRA():
            try:
                self._lf_session.Close()
            except Exception as e:
                print e
                print 'Could not close RA session. Please ensure that you have opened one!'

        sdk_loaded = self._sdk != None
        if sdk_loaded:
            type = self._sdk['type']
            return DisconnectRA() if type == 'RA' else DisconnectLfso()
        else:
            raise Exception('Please load a version of the SDK')


    def LoadCom(self, version, module_name):
        if module_name == "LFSO":
            self.LoadLfso(version)
        elif module_name == "DocumentProcessor":
            self.LoadDocumentProcessor(version)
        else:
            raise Exception('Unsupported COM SDK module')
    
    def LoadLfso(self, version):
        lfso_modules = self._loaded_modules['LFSO']
        module = None
        lib_name = None
        
        if version in lfso_modules.keys() and lfso_modules[version] != {} : 
            module = lfso_modules[version]
        else:
            try:
                #get the dll path and library name
                dll_path = self._args.LFSO_Paths[version]
                lib_name = 'LFSO{}Lib'.format(version.translate(None, '.'))

                #loads the LFSO reference and add it to the loaded modules list
                #tries to load from GAC first
                try:
                    clr.AddReference("Interop." + lib_name)
                    module = __import__(lib_name)
                    lfso_modules[version] = module
                except:
                    clr.AddReferenceToFileAndPath(dll_path)
                    module = __import__(lib_name) 
                    lfso_modules[version] = module
            except Exception:
                print 'Laserfiche Server Object v{} could not be found. Please check your environment.py file'.format(version)
                
        #if a module was found set it as the new default
        if module != None:
            if self._sdk is None:
                self._sdk = {'type': 'LFSO', 'module': { 'LFSO': module }} 
            else:
               	self._sdk['module']['LFSO'] = module
        return module
    
    def LoadDocumentProcessor(self, version):
        doc_modules = self._loaded_modules['DocumentProcessor']
        module = None
        
        if version in doc_modules.keys() and doc_modules[version] != {} : 
            module = doc_modules[version]
        else:
            try:
                #get the dll path and library name
                dll_path = self._args.DocumentProcessor_Paths[version]
                lib_name = 'DocumentProcessor'+version.translate(None, '.')

                #loads the DocumentProcessor reference and add it to the loaded modules list
                #tries to load from GAC first
                try:
                    clr.AddReference("Interop." + lib_name)
                    module = __import__(lib_name)
                    doc_modules[version] = module
                except:
                    clr.AddReferenceToFileAndPath(dll_path)
                    module = __import__(lib_name) 
                    doc_modules[version] = module
            except Exception:
                print 'DocumentProcessor v{} could not be found. Please check your environment.py file'.format(version)

        #if a module was found set it as the new default
        if module != None:
            if self._sdk is None:
                self._sdk = { type: 'LFSO', 'module': {'DocumentProcessor':  module } }
            else:
                self._sdk['module']['DocumentProcessor'] = module
        
        return module
    
    def LoadRA(self, version, module_name):
        ra_modules = self._loaded_modules['RepositoryAccess']
        module_whitelist = ['RepositoryAccess', 'DocumentServices', 'ClientAutomation'] 
        module = None

        if version in ra_modules.keys() and module_name in ra_modules[version].keys():
            module = ra_modules[version][module_name]
        else:
            try:
                if module_name == 'ClientAutomation':
                    dll_path = r'{}\ClientAutomation.dll'.format(
                        self._args.RepositoryAccess_Paths[version]
                    )
                else: 
                    dll_path = r'{}\Laserfiche.{}.dll'.format(
                        self._args.RepositoryAccess_Paths[version],
                        module_name
                    )
                namespace = 'Laserfiche.{}'.format(module_name)

                try:
                    if module_name == 'ClientAutomation':
                        clr.AddReference(module_name)
                    else:
                        clr.AddReference(namespace)
                    module = __import__(namespace)
                except:
                    # Add reference and import target module
                    clr.AddReferenceToFileAndPath(dll_path)
                    module = __import__(namespace)

                temp = ra_modules[version] if len(ra_modules[version].keys()) != 0 else { } 
                temp[module_name] = module
                ra_modules[version] = temp
                    
            except KeyError:
                print 'Repository Access v{} could not be found. Please check your environment.py file'.format(version)

        #if a module was found set it as the new default
        if module != None:
            self._sdk = { 'type': 'RA', 'module': module }
            
        return module

def main() :
    global LF
    LF = LFWrapper(Environment())

# run for debugging
def debug():
    global LF
    LF = LFWrapper(Environment())
    LF.LoadRA('10.0', 'RepositoryAccess')
    #LF.LoadRA('10.0', 'DocumentServices')
    LF.Connect(server='localhost', database='stg-dev')

    print 'Connected!' 

# Run main if not loaded as a module
if __name__ == '__main__':
    if DEBUG:
        debug()
    else:
        main()

