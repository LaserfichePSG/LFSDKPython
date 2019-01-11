# CERTAIN VALUES ARE INTENTIONALLY BLANK FOR DEMONSTRATION PURPOSES
class Environment:
    def __init__(self):
        self._dot_net = '4.0'
        self._cpu_target = 'x64'
        
        # Keys should be version numbers, and vals should be direct paths to the DLLs
        self.LFSO_Paths = {
            '8.3': r'C:\Program Files\Laserfiche\SDK 10.2\bin\COM\x64\Interop.LFSO83Lib.dll',
            '9.2': r'C:\Program Files\Laserfiche\SDK 10.2\bin\COM\x64\Interop.LFSO92Lib.dll',
            '10.0': r'C:\Program Files\Laserfiche\SDK 10.2\bin\COM\x64\Interop.LFSO100Lib.dll'
        }
        
        # Keys should be version numbers, and vals should be direct paths to the DLLs
        self.DocumentProcessor_Paths = {
            '8.3': r'C:\Program Files\Laserfiche\SDK 10.2\bin\COM\x64\Interop.DocumentProcessor83.dll',
            '9.2': r'C:\Program Files\Laserfiche\SDK 10.2\bin\COM\x64\Interop.DocumentProcessor92.dll',
            '10.0': r'C:\Program Files\Laserfiche\SDK 10.2\bin\COM\x64\Interop.DocumentProcessor100.dll'
        }

        # Keys should be version numbers, and vals should be direct paths to the DLLs
        self.RepositoryAccess_Paths = {
            '8.2': r'C:\Program Files\Laserfiche\SDK 10.2\bin\8.2',
            '8.3': r'C:\Program Files\Laserfiche\SDK 10.2\bin\8.3\net-4.0',
            '9.0': r'C:\Program Files\Laserfiche\SDK 10.2\bin\9.0\net-4.0',
            '9.1': r'C:\Program Files\Laserfiche\SDK 10.2\bin\9.1\net-4.0',
            '9.2': r'C:\Program Files\Laserfiche\SDK 10.2\bin\9.2\net-4.0',
            '10.0': r'C:\Program Files\Laserfiche\SDK 10.2\bin\10\net-4.0',
            '10.2': r'C:\Program Files\Laserfiche\SDK 10.2\bin\10.2\net-4.0'
        }

        #U Configuration used to make the default connection to Laserfiche
        self.LaserficheConnection = {
            'server': '',
            'database': '',
            'username': '',
            'password': '' 
        }
