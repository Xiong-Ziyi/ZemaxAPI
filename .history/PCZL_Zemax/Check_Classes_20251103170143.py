import base
import inspect

zos = base.PythonZOSConnection()
ZOSAPI = zos.ZOSAPI
TheApplication = zos.TheApplication
TheSystem = zos.TheSystem

print('Connected to OpticStudio')

# The connection should now be ready to use.  For example:
print('Serial #: ', TheApplication.SerialCode)



# Example: list everything under Layouts
Layouts = TheSystem.Tools.Layouts

help(Layouts)