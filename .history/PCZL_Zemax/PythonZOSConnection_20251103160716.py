import base
import pczl

zos = base.PythonZOSConnection()
ZOSAPI = zos.ZOSAPI
TheApplication = zos.TheApplication
TheSystem = zos.TheSystem

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

# Set Wavelengths Values of Cellphone lens
if num_wavelengths == 1:
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
Surface[1].Thickness = 1.0
Surface[1].Comment = "Dummy"

Surface[2].IsStop = True 

Paraxial_Surface = ZOSAPI.Editors.LDE.SurfaceType.Paraxial
Paraxial_Focal_Length = ZOSAPI.Editors.LDE.SurfaceColumn.Par1

# Change Surface Types to Paraxial
for i in range(2, num_surfaces - 1):
    st = SysLDE.GetSurfaceAt(i).GetSurfaceTypeSettings(Paraxial_Surface)
    Surface[i].ChangeType(st)

# Get the values of the PCZL parameters
pczl = pczl.PCZL(f_3 = 1.2, m_4 = 3, d_12s = 0.5, d_34s = 0.5, q = 0.2785, num_samples=101)

Surface[2].Comment = "Front Fixed Group"
#Surface[2].GetSurfaceCell(Paraxial_Focal_Length).DoubleValue = 20.0
Surface[2].SurfaceData.Par1.DoubleValue = pczl.f_1

Surface[3].Comment = "Variator"
Surface[3].SurfaceData.Par1.DoubleValue = pczl.f_2

Surface[4].Comment = "Compensator"
Surface[4].SurfaceData.Par1.DoubleValue = pczl.f_3

Surface[5].Thickness = pczl.l_4i
Surface[5].Comment = "Rear Fixed Group"
Surface[5].SurfaceData.Par1.DoubleValue = pczl.f_4

# Multi-configuration Setup
SysMCE = TheSystem.MCE

THIC = ZOSAPI.Editors.MCE.MultiConfigOperandType.THIC

num_configs = SysMCE.NumberOfConfigurations

if num_configs == 1:
    SysMCE.AddConfiguration(False)

num_operands = SysMCE.NumberOfOperands

if num_operands == 1:
    for i in range(2):
        SysMCE.AddOperand()

num_operands = SysMCE.NumberOfOperands
print("Number of MC operands: ", num_operands)

MC_Operand=[SysMCE.GetOperandAt(i) for i in range(1, num_operands + 1)] # Use a list to store all MC operands objects
MC_Operand.insert(0, None)  # to make the index start from 1

for i in range(1, num_operands + 1):
    MC_Operand[i].ChangeType(THIC)
    MC_Operand[i].Param1 = i + 1  # Surface Number

# Thickness values for short focal length position
MC_Operand[1].GetOperandCell(1).DoubleValue = pczl.d_12s    # Thickness of Surface 2
MC_Operand[2].GetOperandCell(1).DoubleValue = pczl.d_23[-1] # Thickness of Surface 3
MC_Operand[3].GetOperandCell(1).DoubleValue = pczl.d_34s    # Thickness of Surface 4

# Thickness values for long focal length position
MC_Operand[1].GetOperandCell(2).DoubleValue = pczl.d_12[0]  # Thickness of Surface 2
MC_Operand[2].GetOperandCell(2).DoubleValue = pczl.d_23[0]  # Thickness of Surface 3
MC_Operand[3].GetOperandCell(2).DoubleValue = pczl.d_34[0]  # Thickness of Surface 4

# Export Cross Section
SysTool = TheSystem.Tools
Systool.CrossSection

