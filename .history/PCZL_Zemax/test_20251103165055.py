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

# 1) See all attribute names
print("Attribute names:\n", dir(Layouts))

# 2) Filter only callable members (methods)
print("Callable members (methods):\n", [name for name in dir(Layouts) if callable(getattr(Layouts, name)) and not name.startswith('_')])

# 3) Or, more detailed: get actual type info
for name, member in inspect.getmembers(Layouts):
    if not name.startswith('_'):
        print(name, ":", type(member))
