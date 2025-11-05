import base_interactive as base_interactive
import inspect

zos = base_interactive.PythonZOSConnection()
ZOSAPI = zos.ZOSAPI
TheApplication = zos.TheApplication
TheSystem = zos.TheSystem

print('Connected to OpticStudio')

# The connection should now be ready to use.  For example:
print('Serial #: ', TheApplication.SerialCode)



# Example: list everything under Layouts
Layouts = TheSystem.Tools.Layouts


def explore_namespace(obj):
    # 1) See all attribute names
    print("Attribute names:\n", dir(obj))

    # 2) Filter only callable members (methods)
    print("Callable members (methods):\n", [name for name in dir(obj) if callable(getattr(obj, name)) and not name.startswith('_')])
