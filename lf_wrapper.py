import sys
import os

#Define global vars
LF = None
DEBUG = False
# Hack for running pdb under ipy. Local path not automatically added to sys
if 'pdb' in sys.modules:
    sys.path.insert(0, os.getcwd())
    DEBUG = True

# import CLR and environment paths
import clr
from environment import Environment

# Define an instance of the LF ClR. Valid Args are:
# target = <SDK Target>.  Valid options are:
#       
class LfWrapper:
    def __init__(self, args):
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

        self._args = args
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
                target = namespace[attr] 
                return target

        #if no match is found raise an exception
        raise KeyError('Command not found')

    # LFSOd does not have namespacing infront of the methods.  We can check the module dir directly and return
    def _get_fromCOM(self, module, attr):
        for mod in module.keys():
            namespaces = dir(module[mod])
            if attr in namespaces:
                return module[mod][attr]
        raise KeyError('Command not found')

    # this is used to overload the property operator for the LfWrapper object
    # it will allow short cut access to SDK objects through the wrapper without having to go through
    # the namespaces or import specific functions from the module.
    def __getattr__(self, attr):
        if self._sdk == None:
            raise Exception('SDK is not loaded')
        else:
            type = self._sdk['type']
            module = self._sdk['module']
            return self._get_fromRA(module, attr) if type == 'RA' else self._get_fromCOM(module, attr)

    def Connect(self):
        def ConnectRA():
            if self._lf_session == None:
                credentials = (self._lf_credentials['server'],
                               self._lf_credentials['database'],
                               self._lf_credentials['username'],
                               self._lf_credentials['password'])

                self._lf_session = self.Session.Create(*credentials)
            else:
                raise Exception('Please load a version of the SDK')
            return self._lf_session
        
        def ConnectLfso():
            if self._db == None:
                credentials = (self._lf_credentials['database'],
                               self._lf_credentials['server'], 
                               self._lf_credentials['username'],
                               self._lf_credentials['password'])

                app = self.LFApplicationClass()
                self._db = app.ConnectToDatabase(*credentials)
            return self._db

        sdk_loaded = self._sdk != None
        if sdk_loaded:
            type = self._sdk['type']
            return ConnectRA() if type == 'RA' else ConnectLfso()
        else:
            raise Exception('Please load a version of the SDK')

    def Disconnect(self):
        def DisconnectLfso():
            if self._db != None:
                self._db.CurrentConnection.Terminate()

        def DisconnectRA():
            if self._lf_session != None:
                self._lf_session.LogOut()

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
                clr.AddReferenceToFileAndPath(dll_path)
                module = __import__(lib_name) 
                lfso_modules[version] = module
            except KeyError:
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

                #loads the LFSO reference and add it to the loaded modules list
                clr.AddReferenceToFileAndPath(dll_path)
                module = __import__(lib_name) 
                doc_modules[version] = module
            except KeyError:
                pass 

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
    LF = LfWrapper(Environment())

# run for debugging
def debug():
    global LF
    LF = LfWrapper(Environment())
    LF.LoadLfso('10.0')
    #LF.LoadRA('10.0', 'RepositoryAccess')
    #LF.LoadRA('10.0', 'DocumentServices')
    LF.Connect()

    print ('Connected!') 

# Run main if not loaded as a module
if __name__ == '__main__':
    if DEBUG:
        debug()
    else:
        main()

