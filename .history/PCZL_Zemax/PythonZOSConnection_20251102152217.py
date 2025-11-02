import clr, os, winreg
from itertools import islice

from .PCZL import PCZL

# This boilerplate requires the 'pythonnet' module.
# The following instructions are for installing the 'pythonnet' module via pip:
#    1. Ensure you are running a Python version compatible with PythonNET. Check the article "ZOS-API using Python.NET" or
#    "Getting started with Python" in our knowledge base for more details.
#    2. Install 'pythonnet' from pip via a command prompt (type 'cmd' from the start menu or press Windows + R and type 'cmd' then enter)
#
#        python -m pip install pythonnet

# determine the Zemax working directory
aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)
zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
NetHelper = os.path.join(os.sep, zemaxData[0], r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
winreg.CloseKey(aKey)

# add the NetHelper DLL for locating the OpticStudio install folder
clr.AddReference(NetHelper)
import ZOSAPI_NetHelper # type: ignore

#pathToInstall = ''
# uncomment the following line to use a specific instance of the ZOS-API assemblies
pathToInstall = r'\C:\Program Files\Zemax OpticStudio'

# connect to OpticStudio
success = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(pathToInstall)

zemaxDir = ''
if success:
    zemaxDir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
    print('Found OpticStudio at:   %s' + zemaxDir)
else:
    raise Exception('Cannot find OpticStudio')

# load the ZOS-API assemblies
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI.dll'))
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI_Interfaces.dll'))
import ZOSAPI # type: ignore

TheConnection = ZOSAPI.ZOSAPI_Connection()
if TheConnection is None:
    raise Exception("Unable to intialize NET connection to ZOSAPI")

TheApplication = TheConnection.ConnectAsExtension(0)
if TheApplication is None:
    raise Exception("Unable to acquire ZOSAPI application")

if TheApplication.IsValidLicenseForAPI == False:
    raise Exception("License is not valid for ZOSAPI use.  Make sure you have enabled 'Programming > Interactive Extension' from the OpticStudio GUI.")

TheSystem = TheApplication.PrimarySystem
if TheSystem is None:
    raise Exception("Unable to acquire Primary system")


def reshape(data, x, y, transpose = False):
    """Converts a System.Double[,] to a 2D list for plotting or post processing
    
    Parameters
    ----------
    data      : System.Double[,] data directly from ZOS-API 
    x         : x width of new 2D list [use var.GetLength(0) for dimension]
    y         : y width of new 2D list [use var.GetLength(1) for dimension]
    transpose : transposes data; needed for some multi-dimensional line series data
    
    Returns
    -------
    res       : 2D list; can be directly used with Matplotlib or converted to
                a numpy array using numpy.asarray(res)
    """
    if type(data) is not list:
        data = list(data)
    var_lst = [y] * x
    it = iter(data)
    res = [list(islice(it, i)) for i in var_lst]
    if transpose:
        return transpose(res)
    return res
    
def transpose(data):
    """Transposes a 2D list (Python3.x or greater).  
    
    Useful for converting mutli-dimensional line series (i.e. FFT PSF)
    
    Parameters
    ----------
    data      : Python native list (if using System.Data[,] object reshape first)    
    
    Returns
    -------
    res       : transposed 2D list
    """
    if type(data) is not list:
        data = list(data)
    return list(map(list, zip(*data)))


print('Connected to OpticStudio')

# The connection should now be ready to use.  For example:
print('Serial #: ', TheApplication.SerialCode)

# Insert Code Here

# Define System Explore
SysExplore = TheSystem.SystemData

# Set Title and Notes
SysExplore.TitleNotes.Title = "Paraxial Zoom Lens Generator"
SysExplore.TitleNotes.Notes = "Generate a paraxial zoom lens based on the calculation of the positive and negative compensated zoom lens formulas."
SysExplore.TitleNotes.Author = "Ziyi Xiong"

# Set Aperture
SysExplore.Aperture.ApertureType = ZOSAPI.SystemData.ZemaxApertureType.ImageSpaceFNum
SysExplore.Aperture.ApertureValue = 5.6

# Set Fields
SysExplore.Fields.SetFieldType(ZOSAPI.SystemData.FieldType.ParaxialImageHeight)
SysExplore.Fields.ApplyFieldWizard(ZOSAPI.SystemData.FieldPattern.EqualAreaY, 9, 6.6, 0, 0, 0, True, False)

# Set Wavelengths
# SysExplore.Wavelengths.SelectWavelengthPreset(ZOSAPI.SystemData.WavelengthPreset.FdC_Visible)

# Remove wavelengths
num_wavelengths = SysExplore.Wavelengths.NumberOfWavelengths
print("Number of wavelengths before insertion: ", num_wavelengths)

'''
if num_fields > 1:
    for i in range(num_fields, 1, -1):
        SysExplore.Wavelengths.RemoveWavelength(i)
'''

if num_wavelengths == 1:
# Set Wavelengths Values of Cellphone lens
    SysExplore.Wavelengths.GetWavelength(1).Wavelength = 0.5876
    SysExplore.Wavelengths.GetWavelength(1).Weight = 24
    SysExplore.Wavelengths.AddWavelength(0.6563, 11)
    SysExplore.Wavelengths.AddWavelength(0.5461, 24)
    SysExplore.Wavelengths.AddWavelength(0.4861, 12)
    SysExplore.Wavelengths.AddWavelength(0.4360, 3)
    SysExplore.Wavelengths.AddWavelength(0.4047, 1)

num_wavelengths = SysExplore.Wavelengths.NumberOfWavelengths
print("Number of wavelengths after insertion: ", num_wavelengths)

# Define Lens Data
SysLDE = TheSystem.LDE
num_surfaces = SysLDE.NumberOfSurfaces
print("Number of surfaces before insertion: ", num_surfaces)

if num_surfaces == 3:
    for i in range(4): # range(4) = [0, 1, 2, 3]
        SysLDE.AddSurface()

num_surfaces = SysLDE.NumberOfSurfaces
print("Number of surfaces after insertion: ", num_surfaces)

Surface=[SysLDE.GetSurfaceAt(i) for i in range(0, num_surfaces)] # Use a list to store all surfaces objects

'''
for i in range(1, num_surfaces - 1):
    s = SysLDE.GetSurfaceAt(i)
    Surface.append(s)
'''
Surface[1].Thickness = 5.0
Surface[1].Comment = "Dummy"

Surface[2].IsStop = True 

Paraxial_Surface = ZOSAPI.Editors.LDE.SurfaceType.Paraxial
Paraxial_Focal_Length = ZOSAPI.Editors.LDE.SurfaceColumn.Par1

# Change Surface Types to Paraxial
for i in range(2, num_surfaces - 1):
    st = SysLDE.GetSurfaceAt(i).GetSurfaceTypeSettings(Paraxial_Surface)
    Surface[i].ChangeType(st)
    
Surface[2].Thickness = 50.0
Surface[2].Comment = "Front Fixed Group"

#Surface[2].GetSurfaceCell(Paraxial_Focal_Length).DoubleValue = 20.0
Surface[2].SurfaceData.Par1.DoubleValue = 20.0

Surface[3].Thickness = 50.0
Surface[3].Comment = "Variator"
Surface[3].SurfaceData.Par1.DoubleValue = 20.0

Surface[4].Thickness = 50.0
Surface[4].Comment = "Compensator"
Surface[4].SurfaceData.Par1.DoubleValue = 20.0

Surface[5].Thickness = 50.0
Surface[5].Comment = "Rear Fixed Group"
Surface[5].SurfaceData.Par1.DoubleValue = 20.0

# Multi-configuration Setup
SysMCE = TheSystem.MCE

SysMCE.AddConfiguration(False)
SysMCE.AddOperand()
SysMCE.AddOperand()


