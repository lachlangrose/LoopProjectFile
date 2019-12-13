# -*- coding: utf-8 -*-
"""

This module provides accessor functions to a Loop Project file as defined in
<url pending>.  

Examples
--------
The main accessor functions are LoopProjectFile.Get and LoopProjectFile.Set 
which are used as below:
    >>> import LoopProjectFile
    >>> response = LoopProjectFile.Get(`filename`,`element`)
    >>> if response["errorFlag"]: print(response["errorString"])
    >>> else: value = response["value"]
or
    >>> import LoopProjectFile
    >>> response = LoopProjectFile.Set(`filename`,`element`,`value`)
    >>> if response["errorFlag"]: print(response["errorString"])
    >>> else: print("Successful set")
where:
    *filename* - is the Loop Project File filename including pathing
    *element* - is the field of the file to get/set
    *value* - is the data to set

Returns
-------
The structure of each Get or Set function is a dict with "errorFlag" which
indicates a failure (on True) to get/set and then "errorString" in the case of
a failure or "value" in the case of a successful get call.

"""
import netCDF4
import sys
import os
from numpy import dtype

#Current Loop Project File Version
def LoopVersion():
    """
    **LoopVersion** - hardcoded current version
    
    Returns
    -------
    [int,int,int]
        List of current version [Major,Minor,Sub]version
    
    """
    return [0,0,1]

# Check version of Loop Project File is valid
def CheckVersionValid(rootGroup, verbose=False):
    """
    **CheckVersionValid** - Checks for valid version information given a netCDF
    root node
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)
    
    Returns
    -------
    bool
        True if valid version in project file, False otherwise.
    
    """
    if rootGroup and "loopMajorVersion" in rootGroup.ncattrs() \
      and "loopMinorVersion" in rootGroup.ncattrs() \
      and "loopSubVersion" in rootGroup.ncattrs():
        version = [rootGroup.loopMajorVersion, \
                   rootGroup.loopMinorVersion, \
                   rootGroup.loopSubVersion]
        if verbose: print("  Loop Project File version" \
          +str(version[0])+"."+str(version[1])+"."+str(version[2]))
        return True
    else:
        errString = "(INVALID) No Version for this project file"
        print(errString)
        return False

# Check extents of Loop Project File is valid
def CheckExtentsValid(rootGroup, xyzGridSize, verbose=False):
    """
    **CheckExtentsValid** - Checks for valid extents (geodesic, utm, depth,
    and spacing) and working format in project file
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    xyzGridSize: [int,int,int]
        The 3D grid shape of expected data contained in this project file
        based on the extents contained within
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)
    
    Returns
    -------
    bool
        True if valid extents in project file, False otherwise.
    
    """
    valid = True
    # Check Projection Model
    if "workingFormat" in rootGroup.ncattrs():
        if verbose: print("  Working in ", "Geodesic" if rootGroup.workingFormat == 0 else "UTM", " Projection")
    else:
        print("(INVALID) No working format (Geodesic or UTM selection) in project file")
        valid = False

    # Check Geodesic extents
    if "minLatitude" in rootGroup.ncattrs() \
      and "maxLatitude" in rootGroup.ncattrs() \
      and "minLongitude" in rootGroup.ncattrs() \
      and "maxLongitude" in rootGroup.ncattrs():
        if verbose: 
            print("  Geodesic extents found (deg)")
            print("\t minLatitude   = ", rootGroup.minLatitude)
            print("\t maxLatitude   = ", rootGroup.maxLatitude)
            print("\t minLongitude  = ", rootGroup.minLongitude)
            print("\t maxLongitude  = ", rootGroup.maxLongitude)
    else:
        print("(INVALID) No Geodesic extents found")
        valid = False

    # Check UTM extents
    if "minNorthing" in rootGroup.ncattrs() \
      and "maxNorthing" in rootGroup.ncattrs() \
      and "minEasting" in rootGroup.ncattrs() \
      and "maxEasting" in rootGroup.ncattrs() \
      and "utmZone" in rootGroup.ncattrs() \
      and "utmNorthSouth" in rootGroup.ncattrs():
        if verbose:
            print("  UTM extents found (m)")
            print("\t minNorthing   = ", rootGroup.minNorthing)
            print("\t maxNorthing   = ", rootGroup.maxNorthing)
            print("\t minEasting    = ", rootGroup.minEasting)
            print("\t maxEasting    = ", rootGroup.maxEasting)
            print("\t utmZone       = ", rootGroup.utmZone)
            print("\t utmNorthSouth = ", 'N' if (rootGroup.utmNorthSouth == 1) else 'S')
    else:
        print("(INVALID) No UTM extents found")
        valid = False

    # Check Depth Extents
    if "minDepth" in rootGroup.ncattrs() \
      and "maxDepth" in rootGroup.ncattrs():
        if verbose:
            print("  Depth extents found (m)")
            print("\t minDepth      = ", rootGroup.minDepth)
            print("\t maxDepth      = ", rootGroup.maxDepth)
    else:
        print("(INVALID) No Depth extents found")
        valid = False

    # Check X/Y/Z spacing 
    if "spacingX" in rootGroup.ncattrs() \
      and "spacingY" in rootGroup.ncattrs() \
      and "spacingZ" in rootGroup.ncattrs():
        if verbose:
            print("  Axis Spacing (m)")
            print("\t spacing X axis = ", rootGroup.spacingX)
            print("\t spacing Y axis = ", rootGroup.spacingY)
            print("\t spacing Z axis = ", rootGroup.spacingZ)
    else:
        print("(INVALID) No spacing information in project file")
        valid = False
        
    if valid:
        xyzGridSize[0] =  int((rootGroup.maxEasting - rootGroup.minEasting) / rootGroup.spacingX + 1)
        xyzGridSize[1] =  int((rootGroup.maxNorthing - rootGroup.minNorthing) / rootGroup.spacingY + 1)
        xyzGridSize[2] =  int((rootGroup.maxDepth - rootGroup.minDepth) / rootGroup.spacingZ + 1)
        
    return valid

# Check Data Collection valid if present
def CheckDataCollectionValid(rootGroup, verbose=False):
    """
    **CheckDataCollectionValid** - Checks for valid data collection group data 
    given a netCDF root node
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)
    
    Returns
    -------
    bool
        True if valid data collection formatting in project file, False 
        otherwise.
    
    """
    valid = True
    if "DataCollection" in rootGroup.groups:
        if verbose: print("  Data Collection Group Present")
        dcGroup = rootGroup.groups.get("DataCollection")
#        if verbose: print(dcGroup)
    else:
        if verbose: print("No Data Collection Group Present")
    return valid

# Check Extracted Regional Information valid if present
def CheckExtractedRegionalInformationValid(rootGroup, verbose=False):
    """
    **CheckExtractedRegionalInformationValid** - Checks for valid extracted data
    given a netCDF root node
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)
    
    Returns
    -------
    bool
        True if valid extracted regional data in project file, False otherwise.
    
    """
    valid = True
    if "ExtractedRegionalInformation" in rootGroup.groups:
        if verbose: print("  Extracted Regional Information Group Present")
        eriGroup = rootGroup.groups.get("ExtractedRegionalInformation")
#        if verbose: print(eriGroup)
    else:
        if verbose: print("No Extracted Regional Information Group Present")
    return valid

# Check Structural Models valid if present
def CheckStructuralModelsValid(rootGroup, xyzGridSize=None, verbose=False):
    """
    **CheckStricturalModelsValid** - Checks for valid structural model group data
    given a netCDF root node
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    xyzGridSize: [int,int,int] or None
        The 3D grid shape to test data in this node to adhere to
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)
    
    Returns
    -------
    bool
        True if valid structural model data in project file, False otherwise.
    
    """
    valid = True
    if "StructuralModels" in rootGroup.groups:
        if verbose: print("  Structural Models Group Present")
        smGroup = rootGroup.groups.get("StructuralModels")
#        if verbose: print(smGroup)
        if xyzGridSize != None:
            # Check gridSize from extents matches models sizes
            smGridSize = [smGroup.dimensions["northing"].size,smGroup.dimensions["easting"].size,smGroup.dimensions["depth"].size]
            if smGridSize != xyzGridSize:
                print("(INVALID) Extents grid size and Structural Models Grid Size do NOT match")
                print("(INVALID) Extents Grid Size :           ", xyzGridSize)
                print("(INVALID) Structural Models Grid Size : ", smGridSize)
                valid = False
            else:
                if verbose: print("  Structural Models grid size adheres to extents")
    else:
        if verbose: print("No Structural Models Group Present")
    return valid

# Check Geophysical Models valid if present
def CheckGeophysicalModelsValid(rootGroup, verbose=False):
    """
    **CheckGeophysicalModelsValid** - Checks for valid geophysical model group data
    given a netCDF root node
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)
    
    Returns
    -------
    bool
        True if valid geophysical model data in project file, False otherwise.
    
    """
    valid = True
    if "GeophysicalModels" in rootGroup.groups:
        if verbose: print("  Geophysical Models Group Present")
        gmGroup = rootGroup.groups.get("GeophysicalModels")
#        if verbose: print(gmGroup)
    else:
        if verbose: print("No Geophysical Models Group Present")
    return valid

# Check Probability Model valid if present
def CheckProbabilityModelValid(rootGroup, verbose=False):
    """
    **CheckProbabilityModelValid** - Checks for valid Probability model group data
    given a netCDF root node
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)
    
    Returns
    -------
    bool
        True if valid probability data in project file, False otherwise.
    
    """
    valid = True
    if "ProbabilityModel" in rootGroup.groups:
        if verbose: print("  Probability Model Group Present")
        pmGroup = rootGroup.groups.get("ProbabilityModel")
#        if verbose: print(pmGroup)
    else:
        if verbose: print("No Probability Model Group Present")
    return valid




# Get the version of this loop project file in an array
def GetVersion(rootGroup):
    """
    **GetVersion** - Extracts the Loop Project File version data given a netCDF
    root node
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    
    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a [int,int,int] of the version of this project file

    """
    if CheckVersionValid(rootGroup, True):
        return {"errorFlag":False,"value":[rootGroup.loopMajorVersion,rootGroup.loopMinorVersion,rootGroup.loopSubVersion]}
    else:
        return {"errorFlag":True,"errorString":"No valid Version in Loop Project File"}

# Get Extents and return in a dict
def GetExtents(rootGroup):
    """
    **GetExtents** - Extracts Loop Project region of interest extents given a
    netCDF root node
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    
    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a dict{"geodesic":[double,double,double, double],
        "utm":[int,int,double,double,double,double],"depth":[double,double],
        "spacing":[double,double,double]} containing the extents of this
        project file
    
    """
    response = {"errorFlag":False}
    if "minLatitude" in rootGroup.ncattrs() \
      and "maxLatitude" in rootGroup.ncattrs() \
      and "minLongitude" in rootGroup.ncattrs() \
      and "maxLongitude" in rootGroup.ncattrs():
        geodesic = [rootGroup.minLatitude,rootGroup.maxLatitude,rootGroup.minLongitude,rootGroup.maxLongitude]
    else:
        errStr = "(ERROR) No or incomplete geodesic boundary in loop project file"
        print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    if "utmZone" in rootGroup.ncattrs() \
      and "utmNorthSouth" in rootGroup.ncattrs() \
      and "minNorthing" in rootGroup.ncattrs() \
      and "maxNorthing" in rootGroup.ncattrs() \
      and "minEasting" in rootGroup.ncattrs() \
      and "maxEasting" in rootGroup.ncattrs():
        utm = [rootGroup.utmZone,rootGroup.utmNorthSouth,rootGroup.minNorthing,rootGroup.maxNorthing,rootGroup.minEasting,rootGroup.maxEasting]
    else:
        errStr = "(ERROR) No or incomplete UTM boundary in loop project file"
        print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    if "minDepth" in rootGroup.ncattrs() \
      and "maxDepth" in rootGroup.ncattrs():
        depth = [rootGroup.minDepth,rootGroup.maxDepth]
    else:
        errStr = "(ERROR) No or incomplete depth boundary in loop project file"
        print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    if "spacingX" in rootGroup.ncattrs() \
      and "spacingY" in rootGroup.ncattrs() \
      and "spacingZ" in rootGroup.ncattrs():
        spacing = [rootGroup.spacingX,rootGroup.spacingY,rootGroup.spacingZ]
    else:
        errStr = "(ERROR) No or incomplete spacing data in loop project file"
        print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    if response["errorFlag"] == False:
        response["value"] = {"geodesic":geodesic,"utm":utm,"depth":depth,"spacing":spacing}
    return response

# Get Structural Models group if present
def GetStructuralModels(rootGroup):
    """
    **GetStructuralModels** - Gets the stuctural models group node within the
    netCDF Loop Project File
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    
    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a netCDF4 Group containing all the structural models
        
    """
    if "StructuralModels" in rootGroup.groups:
        smGroup = rootGroup.groups.get("StructuralModels")
        return {"errorFlag":False,"value":smGroup}
    else:
        errString = "No Structural Models Group Present on access request"
        print(errString)
        return {"errorFlag":True,"errorString":errString}

# Extract structural model indexed by parameter
def GetStructuralModel(root, verbose=False, index=0):
    """
    **GetStructuralModel** - Extracts the stuctural model indicated by index from
    the netCDF Loop Project File
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    
    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a double[int:int:int] which is scalar field of the structural
        model
        
    """    
    response = {"errorFlag":False}
    resp = GetStructuralModels(root)
    if resp["errorFlag"]: response = resp
    else:
        smGroup = resp["value"]
        # Check data exists at the specified index value
#        if smGroup.variables.
        data = smGroup.variables.get('data')[:,:,:,index].data
        if verbose: print("The shape of the structuralModel is", data.shape)
        response["value"] = data
    return response




# Set version on root group
def SetVersion(rootGroup, version):
    """
    **SetVersion** - Saves the version specified into the netCDF Loop Project File
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    version: [int,int,int]
        The version in list form with [Major/Minor/Sub] version
    
    Returns
    -------
       dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True
   
    """
    if len(version) != 3:
        errStr = "(ERROR) invalid version for setting current version " + version
        print(errStr)
        return {"errorFlag":True,"errorString":errStr}
    else:
        rootGroup.loopMajorVersion = version[0]
        rootGroup.loopMinorVersion = version[1]
        rootGroup.loopSubVersion = version[2]
        return {"errorFlag":False}

# Set extents of region of interest on root group
def SetExtents(rootGroup, geodesic, utm, depth, spacing, preference="utm"):
    """
    **SetExtents** - Saves the extents of the region of interest as specified into
    the netCDF Loop Project File
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    geodesic: [double,double,double,double]
        The latitude and longitude limits of the region in format:
        [minLat,maxLat,minLong,maxLong]
    utm: [int,int,double,double,double,double]
        The utmZone, utmNorth/South, northing and easting extents in format:
        [utmZone,utmNorthSouth,minNorthing,maxNorthing,minEasting,maxEasting]
    depth: [double,double]
        The depth minimum and maximums in format: [minDepth,maxDepth]
    spacing: [double, double, double]
        The spacing of adjacent points in the grid for X/Y/Z.  This corresponds
        to [latitude/northing,longitude/easting,depth]
    preference: string (optional)
        A string ("utm" or "geodesic") which specifies which format the Loop GUI
        region of interest should be displayed
    
    Returns
    -------
       dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True
   
    """
    response = {"errorFlag":False}
    if len(geodesic) != 4:
        errStr = "(ERROR) Invalid number of geodesic boundary values (" + str(len(geodesic)) + ")"
        print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    else:
        rootGroup.minLatitude = geodesic[0]
        rootGroup.maxLatitude = geodesic[1]
        rootGroup.minLongitude = geodesic[2]
        rootGroup.maxLongitude = geodesic[3]
    if len(utm) != 6:
        errStr = "(ERROR) Invalid number of UTM boundary values (" + str(len(utm)) + ")"
        print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    else:
        rootGroup.utmZone = utm[0]
        rootGroup.utmNorthSouth = 0 if utm[1] == "S" or utm[1] == "s" or utm[1] == 0 else 1
        rootGroup.minNorthing = utm[2]
        rootGroup.maxNorthing = utm[3]
        rootGroup.minEasting = utm[4]
        rootGroup.maxEasting = utm[5]
    if len(depth) != 2:
        errStr = "(ERROR) Invalid number of depth boundary values (" + str(len(depth)) + ")"
        print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    else:
        rootGroup.minDepth = depth[0]
        rootGroup.maxDepth = depth[1]
    if len(spacing) != 3:
        errStr = "(ERROR) Invalid number of spacing values (" + str(len(depth)) + ")"
        print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    else:
        rootGroup.spacingX = spacing[0]
        rootGroup.spacingY = spacing[1]
        rootGroup.spacingZ = spacing[2]
    rootGroup.workingFormat = 1 if preference == "utm" else 0
    return response
 
# Set structural model (with dimension checking)
def SetStructuralModel(root, data, index=0, verbose=False):
    """
    **SetStructuralModel** - Saves a 3D scalar representation of a structural
    geological model into the netCDF Loop Project File at specified index
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: double[int,int,int]
        The scalar data to save
    index: int
        The index of this data
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)
    
    Returns
    -------
       dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True
   
    """
    response = {"errorFlag":False}
    xyzGridSize = [0,0,0];
    CheckExtentsValid(root, xyzGridSize, verbose)
    resp = GetStructuralModels(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        structuralModelsGroup = root.createGroup("StructuralModels")
        structuralModelsGroup.createDimension("easting",xyzGridSize[0])
        structuralModelsGroup.createDimension("northing",xyzGridSize[1])
        structuralModelsGroup.createDimension("depth",xyzGridSize[2])
        structuralModelsGroup.createDimension("index",None)
        structuralModelsGroup.createVariable('data',dtype('float64').char,('northing','easting','depth','index'),zlib=True,complevel=9,fill_value=0)
        # Check creation worked??
    else:
        structuralModelsGroup = resp["value"]
    if structuralModelsGroup:
        # Do dimension checking between incoming data and existing netCDF data shape
        dataGridSize = list(data.shape)
        if dataGridSize != xyzGridSize:
            errStr = "(ERROR) Structural Model data shape does not match extents of project"
            print(errStr)
            response = {"errorFlag":True,"errorString":errStr}
        else:
#            structuralModelsGroup.variables('data')[:,:,:,index] = data
            dataLocation = structuralModelsGroup.variables['data']
            dataLocation[:,:,:,index] = data
    return response


####  External Accessors ####

# Create a basic loop project file if no file already exists
def CreateBasic(filename):
    """
    **CreateBasic** - Creates a basic Loop Project File without extents or data
    (will not overright existing files)
    
    Parameters
    ----------
    filename: string
        The name of the file to create
    
    Returns
    -------
    dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True
        
    """
    if os.path.isfile(filename):
        errStr = "File " + filename + " already exists"
        print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    else:
        rootGroup = netCDF4.Dataset(filename,"w",format="NETCDF4")
        response = SetVersion(rootGroup, version=LoopVersion())
        rootGroup.close()
    return response

# Open project file with error checking for file existing and of netCDF format
def OpenProjectFile(filename, readOnly=True, verbose=True):
    """
    **OpenProjectFile** - Open a Loop Project File and checks it exists and is a
    netCDF formatted file
    
    Parameters
    ----------
    filename: string
        The name of the file to open
    readOnly: bool
        Whether to open the file without data entry or not (True - read only,
        False - writable)
    
    Returns
    -------
    dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True    
    
    """
    if verbose: print("Accessing file named: " + filename)
    if not os.path.isfile(filename):
        errStr = "File " + filename + " does not exist"
        print(errStr)
        return {"errorFlag":True, "errorString":errStr}
    readFlag = "r" if readOnly else "a"
    rootgrp = netCDF4.Dataset(filename,readFlag,format="NETCDF4")
    if not rootgrp:
        errStr = "(ERROR) File was not a Loop Project File"
        print(errStr)
        return {"errorFlag":True,"errorString":errStr}    
    if verbose: print("NetCDF data model type: " + rootgrp.data_model)
    return {"errorFlag":False,"root":rootgrp}


# Accessor Function handling opening and closing of file and calling
# appropriate setter function
def Set(filename, element, **kwargs):
    """
    **Set** - The core set function for interacting with a Loop Project File
    Can set with element and kwargs:
        version     : "version" = [Major,Minor,Sub]
        extents     : "geodesic" = [minLat,maxLat,minLong,maxLong]
                      "utm" = [utmZone,utmNorthSouth,minNorthing,maxNorthing,minEasting,maxEasting]
                      "depth" = [minDepth,maxDepth]
                      "spacing" = [N/SSpacing,E/WSpacing,DepthSpacing]
                      "preference" = "utm" or "geodesic" (optional)
        strModel    : "data" = the 3D scalar field of structural data
                      "index" = the index of the dataset to save
                      "verbose" = optional extra console logging
    
    Examples
    --------
    For setting version number:
    >>> LoopProjectFile.Set("test.loop3d","version",version=[1,0,0])
      or
    >>> resp = LoopProjectFile.Set("test.loop3d",version=[1,0,0])
    >>> if resp["errorFlag"]: print(resp["errorString"])
    
    For saving data:
    >>> LoopProjectFile.Set("test.loop3d","strModel",data=dataset,index=0,verbose=True)
      or
    >>> resp = LoopProjectFile.Set("test.loop3d",data=dataset,index=0,verbose=True)
    >>> if resp["errorFlag"]: print(resp["errorString"])
    
    For saving extents (in the middle of the pacific ocean):
    >>> LoopProjectFile.Set("test.loop3d","extents",geodesic=[0,1,-180,-179], \
        utm=[1,1,10000000,9889363.77,833966.132,722587.169], depth=[1000,2000] \
        spacing=[1000,1000,10],preference="utm")
    
    
    Parameters
    ----------
    filename: string
        The name of the file to save data to
    element: string
        The name of the element to save
    kwargs: dict
        A dictionary contains the elements to save
        
    Returns
    -------
    dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True
    
    """
    fileResp = OpenProjectFile(filename, readOnly=False, verbose=False)
    if fileResp["errorFlag"]: response = fileResp
    else:
        root = fileResp["root"]
        if element == "version": response = SetVersion(root, **kwargs)
        elif element == "extents": response = SetExtents(root, **kwargs)
        elif element == "strModel": response = SetStructuralModel(root, **kwargs)
        else:
            errStr = "(ERROR) Unknown element for Set function \'" + element + "\'"
            print(errStr)
            response = {"errorFlag":True,"errorString":errStr}
        root.close()
    return response

# Accessor Function handling opening and closing of file and calling
# appropriate getter function
def Get(filename, element, **kwargs):
    """
    **Get** - The core getter function for interacting with a Loop Project File
    Can get data elements which returns a "value" of type:
        version     : "value" = [Major,Minor,Sub]
        extents     : "value" = {"geodesic" = [minLat,maxLat,minLong,maxLong]
                      "utm" = [utmZone,utmNorthSouth,minNorthing,maxNorthing,minEasting,maxEasting]
                      "depth" = [minDepth,maxDepth]
                      "spacing" = [N/SSpacing,E/WSpacing,DepthSpacing]
                      "preference" = "utm" or "geodesic" (optional)}
        strModel    : "value" = the 3D scalar field of structural data
    
    Examples
    --------
    For extracting the version number:
    >>> resp = LoopProjectFile.Get("test.loop3d","version")
    >>> if resp["errorFlag"]: print(resp["errorString"])
    >>> else: version = resp["value"]
    
    For extracting data:
    >>> resp = LoopProjectFile.Set("test.loop3d","strModel",data=dataset,index=0)
    >>> if resp["errorFlag"]: print(resp["errorString"])
    >>> else: data = resp["value"]
    
    For extracting the extents:
    >>> resp = LoopProjectFile.Get("test.loop3d","extents",index=0)
    >>> if resp["errorFlag"]: print(resp["errorString"])
    >>> else:
    >>>     data = resp["value"]
    >>>     geodesic = data["geodesic"]
    >>>     utm = data["utm"]
    >>>     depth = data["depth"]
    >>>     spacing = data["spacing"]
    
    Parameters
    ----------
    filename: string
        The name of the file to load data from
    element: string
        The name of the element to extract
    kwargs: dict
        A dictionary contains the optional get values such as index of 
        a structural model to extract
        
    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        errorString exist and contains error message only when errorFlag is
        True otherwise the extracted value is in the "value" keyword
    
    """

    fileResp = OpenProjectFile(filename, readOnly=True, verbose=False)
    if fileResp["errorFlag"]: response = fileResp
    else:
        root = fileResp["root"]
        if element == "version": response = GetVersion(root)
        elif element == "extents": response = GetExtents(root)
        elif element == "strModel": response = GetStructuralModel(root,**kwargs)
        else:
            errStr = "(ERROR) Unknown element for Get function \'" + element + "\'"
            print(errStr)
            response = {"errorFlag":True,"errorString":errStr}
        root.close()
    return response

# Check full project structure
def CheckFileValid(filename, verbose=False):
    """
    **CheckFileValid** - A function to check through a Loop Project File to 
    ensure that it is versioned, the extents are valid, and any data structures
    match the shape that the extents specify (comments on the structure are 
    output to console when in verbose mode)
    
    Parameters
    ----------
    filename: string
        The name of the file to laod data from
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
    bool
        A flag indicating whether the Loop Project File is valid
    
    """
    valid = True
    # Open project file
    fileResp = OpenProjectFile(filename, readOnly=True, verbose=verbose)
    if fileResp["errorFlag"]: valid = False
    else:
        rootgrp = fileResp["root"]

        xyzGridSize = [0,0,0];
        # Check for errors in project file
        valid = CheckVersionValid(rootgrp, verbose) and valid
        valid = CheckExtentsValid(rootgrp, xyzGridSize, verbose) and valid
        valid = CheckDataCollectionValid(rootgrp, verbose) and valid
        valid = CheckExtractedRegionalInformationValid(rootgrp, verbose) and valid
        valid = CheckStructuralModelsValid(rootgrp,xyzGridSize, verbose) and valid
        valid = CheckGeophysicalModelsValid(rootgrp, verbose) and valid
        valid = CheckProbabilityModelValid(rootgrp, verbose) and valid
        
        # Close and report
        rootgrp.close()

        if valid:
            print("\nThis is a valid Loop Project File")
        else:
            print("\nThis Loop Project File is NOT valid")
    return valid


