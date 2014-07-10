# -*- coding: utf-8 -*-
"""
Created on Thu Jul 03 12:39:03 2014

@author: paulinkenbrandt
"""

import arcpy

#input = arcpy.GetParameterAsText(0)

input = "C:\\GIS\\beef.gdb\\Test"


arcpy.AddField_management(input,'ParamSht',field_type = 'TEXT', field_length = 10)

arcpy.TableSelect_analysis(input, "C:\\GIS\\beef.gdb\\Test1", '"Param" in(\'Sulfate\', \'Nitrate\', \'Nitrite\', \'Calcium\', \'Potassium\', \'Sodium\', \'Sodium plus potassium\', \'Bicarbonate\', \'Carbonate\', \'Chloride\')')

input2 = "C:\\GIS\\beef.gdb\\Test1"

expression = "getChem(!Param!)"
codeblock = '''
def getChem(p):
    chemdict = {'Sulfate':'SO4', 'Nitrate':'NO3', 'Nitrite':'NO2', 'Calcium':'Ca', 'Potassium':'K', 'Sodium':'Na', 'Sodium plus potassium':'NaK', 'Bicarbonate':'HCO3', 'Carbonate':'CO3', 'Chloride':'Cl'}    
    return chemdict.get(p)
    '''


arcpy.CalculateField_management(input2,'ParamSht',expression, 'PYTHON_9.3', codeblock)


# Set a variable to store time field name
transposedFieldName = "Transposed_Field"
# Set a variable to store value field name
valueFieldName = "ResultValue"
out = "C:\\GIS\\beef.gdb\\Trans"

arcpy.PivotTable_management(input2, 'SampleId','ParamSht','ResultValue',out)
