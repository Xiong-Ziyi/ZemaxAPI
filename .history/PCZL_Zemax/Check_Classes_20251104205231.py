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
OpenCrossSectionExport = TheSystem.Tools.Layouts.OpenCrossSectionExport()

def explore_api(obj):
    print("=== Methods ===")
    for name in dir(obj):
        if callable(getattr(obj, name)) and not name.startswith("_"):
            print(" •", name)
    print("\n=== Properties ===")
    for name in dir(obj):
        if not callable(getattr(obj, name)) and not name.startswith("_"):
            print(" •", name)

# explore_api(OpenCrossSectionExport)
help(OpenCrossSectionExport)