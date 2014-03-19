import imp
import os

import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Graph Coloring"
        self.alias = "gcolor"
        self.tools = [GraphColorTool]

class GraphColorTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Graph Coloring Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        input_layer = arcpy.Parameter(name="in_layer",
                                      displayName="Input Feature Layer",
                                      direction="Input",
                                      datatype="GPFeatureLayer")

        input_field = arcpy.Parameter(name="summary_field", 
                                      displayName="Input Field",
                                      direction="Input",
                                      datatype="GPString")

        params = [input_layer, input_field]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[0].value:
            fc = parameters[0].value
            parameters[1].filter.list = [f.name
                                         for f in arcpy.ListFields(fc)
                                         if f.type.lower() in ('double',
                                                               'smallinteger',
                                                               'integer')]

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        pass

    def execute(self, parameters, messages):
        """The source code of the tool."""
        module_info = imp.find_module('graph_color',
                                      [os.path.dirname(__file__)])
        graph_color = imp.load_module('graph_color', *module_info)
        graph_color.graph_color(parameters[0].valueAsText,
                                parameters[1].valueAsText)
