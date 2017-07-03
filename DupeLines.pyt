#see BriceWolfgang.com for moar


import arcpy
import arcgisscripting
import traceback


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "DupeTools"
        self.alias = "Duplicate Tools"

        # List of tool classes associated with this toolbox
        self.tools = [DupeLines]

# This tool takes a feature class and a field. 
# If there is more than one feature with ideentiacl values in the selected field 
# it draws a line between the features. 
# 
class DupeLines(object):
    def __init__(self):

        self.label = "DupeLines"
        self.description = "Draws lines between duplicate points based on a atribute field"
        self.canRunInBackground = False

    def getParameterInfo(self):
        #Input Fetures 
        in_feat = arcpy.Parameter(
            displayName = "Input Fearutes",
            name = "in_feat",
            datatype = "Feature Layer",
            parameterType="Required",
            direction="Input")

        #Field that is checked for duplication
        field = arcpy.Parameter(
            displayName = "Field for Duplciate Checking",
            name = "field_name",
            datatype = "Field",
            parameterType="Required",
            direction="Input")
        
        # Only fields from the in_feat will appear in the field selector list
        field.parameterDependencies = [in_feat.name]

        #Output Features
        out_feat = arcpy.Parameter(
            displayName = "Output Location",
            name = "out_feat",
            datatype = "Feature Layer",
            parameterType="Required",
            direction="Output")

        params = [in_feat,field,out_feat]
        return params

    def isLicensed(self):
        """ Must be 10.1=> http://pro.arcgis.com/en/pro-app/arcpy/functions/getinstallinfo.htm"""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        fieldName = parameters[1]

        # Make sure the shape field is not selected
        if fieldName.value:
            if fieldName.valueAstext == "Shape":
                fieldName.setErrorMessage("Shape Field Not Supported")
        return

        #####################################################################
        # Dose not handle joined data sets i.e. dfield is like FCName.dfile #
        ######################################################################

    def execute(self, parameters, messages):
        try:
            #Delete prvious version of temporary feature class
            arcpy.Delete_management("in_memory/dupeLines")


            #Get Paremters
            inFC = parameters[0]
            dupeField = parameters[1]
            dFieldName = parameters[1].valueAstext # This is the name of the field that will be checkd for dupe values
            inFCSpatRef = arcpy.Describe(inFC).spatialReference #The spatial refrence of the input feature class
            arcpy.AddMessage("Searching for duplicates in field: " + dFieldName)
            outFC = parameters[2]


            ###############################################
            # Create temporary class and add fields to it #
            ###############################################


            #Create feature class in memory to store lines as they are found
            #has same spaital ref as input feature class
            arcpy.CreateFeatureclass_management(
             "in_memory", 
             "dupeLines", 
             "POLYLINE",
             "",
             "DISABLED",
             "DISABLED",
             inFCSpatRef)


            #Create field to record the "duplicate field" info
            #Has the same field name and data type as the field used to find duplicats 
            arcpy.AddField_management(
                "in_memory/dupeLines", 
                dFieldName, 
                arcpy.Describe(dupeField).type)

            arcpy.AddMessage("Field data type: " + arcpy.Describe(dupeField).type)

            #Create field to record the level of duplication for each line created
            arcpy.AddField_management(
                "in_memory/dupeLines",
                "Duplicate_Count",
                "SHORT")

            #Object ID of start feature
            arcpy.AddField_management(
                "in_memory/dupeLines",
                "Start_FID",
                "SHORT")

            #Object ID of end feature
            arcpy.AddField_management(
                "in_memory/dupeLines",
                "End_FID",
                "SHORT")



            ##################################################
            # Create the serach cursor and the insert cursor #
            ##################################################


            #The SearchCursor will be sorted by the dField and then iterated throught
            #AddFieldDelimiter deals with the ecentrities of diffrent database implimentations!
            sort_clause = "ORDER BY {0}".format(arcpy.AddFieldDelimiters(inFC,dFieldName))

            #Creating the SearchCursor
            #           Searches the inFC feature class
            #           only returns OID, centroid XY, and the field that is being check for duplication
            #           no where clause
            #           has same spatial ref as the input feature class
            #           do not explode to points
            #           no SQL prefix clause, sort_clause from above as the postfix clause 
            inFCSearcher = arcpy.da.SearchCursor(
                            inFC.Value,
                            ("OID@","SHAPE@xy",dFieldName),
                            None,
                            inFCSpatRef,
                            False,
                            (None,sort_clause))

            
            #Insert cursor to store the lines that will be drawn b/t duplicates
            #will store:
            #           the line that is drawn between duplicates
            #           the value of the field that is checked for duplication
            #           how many of each duplicate have been found
            #           feature ID of the starting feature
            #           feature ID of the end feature 
            dupeLinesInserter = arcpy.da.InsertCursor(
                            "in_memory/dupeLines",
                                ["SHAPE@", 
                                 dFieldName,
                                 "Duplicate_Count",
                                 "Start_FID",
                                 "End_FID"])


            ##############################################
            # Find duplicates, create lines between them #
            ##############################################

            t = 0  # total lines the search cursor dose
            tD = 0 # number of duplicates found
            dC = 0 # to count multiples of duplicates 
            sPoint = arcpy.Point() # Start point of a line
            ePoint = arcpy.Point() # End point of a line
            array = arcpy.Array()  # Start and end will go in here

    
            r0 = None  # Previous row

            for r1 in inFCSearcher:
              
                if not r0: # On first run set the current row to previous row
                    r0 = r1 
                    t = t+1 #itearte total counter
                    continue
                
                if r0[2] == r1[2]: #Check for duplicate values 
                    dC = dC + 1 
                    #arcpy.AddMessage("Dupe found:{0}".format(r0[2]))

                    
                    sPoint = arcpy.Point(r0[1][0],r0[1][1])#Make a point from the X and Y of r0
                    #arcpy.AddMessage("{0} Dupe{1} P0 X{2},Y{3}".format(r0[2],dC,r0[1][0],r0[1][1]))
                    ePoint = arcpy.Point(r1[1][0],r1[1][1])#Make a point from the X and Y of r1
                    #arcpy.AddMessage("{0} Dupe{1} P1 X{2},Y{3}".format(r0[2],dC,r1[1][0],r1[1][1]))


                    array.add(sPoint)
                    array.add(ePoint) #Start and end points into the array


                    dupeLine = arcpy.Polyline(array) #The line between two duplicates


                    #In human readable form the new row contains:
                    #the line, value of the field being check for duplicates, duplicate counter, start point OID, end point OID
                    dupeLinesInserter.insertRow([dupeLine,r0[2],dC,r0[0],r1[0]])


                    array.removeAll() #cleans out the array



                else:
                    #When a non duplicate is found
                    tD = tD + dC #Update total duplicates counter
                    dC = 0       #Resets the multiple duplicate counter  


                #End of every loop (execpt the 1st)
                r0 = r1 #Current row move to previous row
                t = t+1 #itearte total counter



            ########################################
            # Some useful info for the message box #
            ########################################

            arcpy.AddMessage("Rows Checked:{0}".format(t))
            arcpy.AddMessage("Duplicates Found:{0}".format(tD))
            #arcpy.AddMessage("in_memory:{0}".format(arcpy.GetCount_management("in_memory/dupeLines")))
            

            ######################################
            # Creating an output Feature Dataset #
            #  and copying the features into it  #
            ######################################


            #Getting name and path based on input pramaters
            outParts = outFC.valueAstext.split("\\")
            out_name = outParts[-1]
            out_path = "\\".join(outParts[0:-2])


            #Creating a feature class on disk 
            arcpy.CreateFeatureclass_management(
             out_path, 
             out_name, 
             "POLYLINE",
             "",
             "DISABLED",
             "DISABLED",
             inFCSpatRef)

            #copy the stuff in_memory to the feature class on disk
            arcpy.CopyFeatures_management(
                "in_memory/dupeLines",
                out_name)

            # Ta Da! 

        except:
            arcpy.AddError(traceback.format_exc()) #get errors from python
            arcpy.AddMessage(arcpy.GetMessages())