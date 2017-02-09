Introduction
------------
This project creates a CLR environment for the Laserfiche (R) API. It is intended for demonstration/personal use only. The API is not included in this package and must be obtained from the [Laserfiche Support Site](https://support.laserfiche.com)

Prerequisites
-------------
1. [Python 2.7.x](https://www.python.org/downloads/)
2. [Iron Python 2.7](http://ironpython.net/) or [Python.NET](http://pythonnet.sourceforge.net/)
3. [Laserfiche SDK](https://support.laserfiche.com)
4. [.NET 4.x](https://www.microsoft.com/net).

Getting Started
---------------
0. It's highly recommended that you add you updated your environment paths to point to python and Iron Python if it's being used.

1. Verify that the SDK paths are correct.  Paths to the SDK dlls are defined in ```environment.py```.  They target the .NET 4.0 libraries for Repository access.  If you wish to run this project in .NET 2.x you may need to update some paths.  You will also need to update references if you have installed Laserfiche SDK in a non default directory.

2. Update the default laserfiche credentials.  ***For Windows Authentication set the user and password to None***

    **Note: It is highly recommended that you use Windows authentication.  If you chose to use Laserfiche credentials, your username/password will be stored in plain text.**

3. Start Python in interpreted mode.  

    If using Iron Python ```ipy -i lf_wrapper.py```

    If using PythonNet ```python -i lf_wrapper.py```

4. Once on the Python prompt ```>>>``` an object named ```LF``` is automatically created.  This is the entry point.

Wrapper Commands
----------------

**Connect**
Connects to the repository specified in your enviornment.py flie.  This method can also be overridden to pass in aritrary credentials

**LoadRA**

**LoadCom**

SDK Commands
------------
Once the SDK has been loaded in the wrapper SDK commands can be executed directy from the wrapper.  The internal session object will automatically be passed into any call that is made.
