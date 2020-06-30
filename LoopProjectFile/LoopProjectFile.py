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
import numpy
import pandas
import sys
import os

import netCDF4
import LoopProjectFile.Version as Version
import LoopProjectFile.Extents as Extents
import LoopProjectFile.StructuralModels as StructuralModels
import LoopProjectFile.DataCollection as DataCollection
import LoopProjectFile.ExtractedInformation as ExtractedInformation
import LoopProjectFile.GeophysicalModels as GeophysicalModels
import LoopProjectFile.ProbabilityModels as ProbabilityModels

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
        response = Version.SetVersion(rootGroup, version=Version.LoopVersion())
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
        observations: "data" = the observations data in the following structure
                        a list of observations containing
                        ((northing,easting,altitude),   = the location (truple of doubles)
                        dipdir,                         = the dip direction (double)
                        dip,                            = the dip (double)
                        polarity,                       = the polarity (int)
                        formation,                      = the formation (string) (Hammerley,...)
                        layer)                          = the layer to associate with (string)("S0","F1",...)
                      "verbose" = optional extra console logging
    
    Examples
    --------
    For setting version number:
    >>> LoopProjectFile.Set("test.loop3d","version",version=[1,0,0])
      or
    >>> resp = LoopProjectFile.Set("test.loop3d","version",version=[1,0,0])
    >>> if resp["errorFlag"]: print(resp["errorString"])
    
    For saving data:
    >>> LoopProjectFile.Set("test.loop3d","strModel",data=dataset,index=0,verbose=True)
      or
    >>> resp = LoopProjectFile.Set("test.loop3d","strModel",data=dataset,index=0,verbose=True)
    >>> if resp["errorFlag"]: print(resp["errorString"])
    
    For saving extents (in the middle of the pacific ocean):
    >>> LoopProjectFile.Set("test.loop3d","extents",geodesic=[0,1,-180,-179], \
        utm=[1,1,10000000,9889363.77,833966.132,722587.169], depth=[1000,2000] \
        spacing=[1000,1000,10],preference="utm")

    For saving field observations:
    >>> data = ((northing,easting,altitude),dipdir,dip,polarity,formation,layer) * X rows
    >>> resp = LoopProjectFile.Set("test.loop3d","observations",data=data,append=False,verbose=True)
    >>> if resp["errorFlag"]: print resp["errorString"])
    
    
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
        if element == "version": response = Version.SetVersion(root, **kwargs)
        elif element == "extents": response = Extents.SetExtents(root, **kwargs)
        elif element == "strModel": response = StructuralModels.SetStructuralModel(root, **kwargs)
        elif element == "faultObservations": response = DataCollection.SetFaultObservations(root, **kwargs)
        elif element == "faultObservationsAppend": response = DataCollection.SetFaultObservations(root, append=True, **kwargs)
        elif element == "foldObservations": response = DataCollection.SetFoldObservations(root, **kwargs)
        elif element == "foldObservationsAppend": response = DataCollection.SetFoldObservations(root, append=True, **kwargs)
        elif element == "foliationObservations": response = DataCollection.SetFoliationObservations(root, **kwargs)
        elif element == "foliationObservationsAppend": response = DataCollection.SetFoliationObservations(root, append=True, **kwargs)
        elif element == "discontinuityObservations": response = DataCollection.SetDiscontinuityObservations(root, **kwargs)
        elif element == "discontinuityObservationsAppend": response = DataCollection.SetDiscontinuityObservations(root, append=True, **kwargs)
        elif element == "stratigraphicObservations": response = DataCollection.SetStratigraphicObservations(root, **kwargs)
        elif element == "stratigraphicObservationsAppend": response = DataCollection.SetStratigraphicObservations(root, append=True, **kwargs)
        elif element == "contacts": response = DataCollection.SetContacts(root, **kwargs)
        elif element == "contactsAppend": response = DataCollection.SetContacts(root, append=True, **kwargs)
        elif element == "stratigraphicLog": response = ExtractedInformation.SetStratigraphicLog(root, **kwargs)
        elif element == "stratigraphicLogAppend": response = ExtractedInformation.SetStratigraphicLog(root, append=True, **kwargs)
        elif element == "faultLog": response = ExtractedInformation.SetFaultLog(root, **kwargs)
        elif element == "faultLogAppend": response = ExtractedInformation.SetFaultLog(root, append=True, **kwargs)
        elif element == "foldLog": response = ExtractedInformation.SetFoldLog(root, **kwargs)
        elif element == "foldLogAppend": response = ExtractedInformation.SetFoldLog(root, append=True, **kwargs)
        elif element == "foliation": response = ExtractedInformation.SetFoliationLog(root, **kwargs)
        elif element == "foliationAppend": response = ExtractedInformation.SetFoliationLog(root, append=True, **kwargs)
        elif element == "discontinuity": response = ExtractedInformation.SetDiscontinuityLog(root, **kwargs)
        elif element == "discontinuityAppend": response = ExtractedInformation.SetDiscontinuityLog(root, append=True, **kwargs)
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
    
    For extracting structural model data:
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
        if element == "version": response = Version.GetVersion(root)
        elif element == "extents": response = Extents.GetExtents(root)
        elif element == "strModel": response = StructuralModels.GetStructuralModel(root,**kwargs)
        elif element == "faultObservations": response = DataCollection.GetFaultObservations(root,**kwargs)
        elif element == "foldObservations": response = DataCollection.GetFoldObservations(root,**kwargs)
        elif element == "foliationObservations": response = DataCollection.GetFoliationObservations(root,**kwargs)
        elif element == "discontinuityObservations": response = DataCollection.GetDiscontinuityObservations(root,**kwargs)
        elif element == "stratigraphicObservations": response = DataCollection.GetStratigraphicObservations(root,**kwargs)
        elif element == "contacts": response = DataCollection.GetContacts(root,**kwargs)
        elif element == "stratigraphicLog": response = ExtractedInformation.GetStratigraphicLog(root,**kwargs)
        elif element == "faultLog": response = ExtractedInformation.GetFaultLog(root,**kwargs)
        elif element == "foldLog": response = ExtractedInformation.GetFoldLog(root,**kwargs)
        elif element == "foliationLog": response = ExtractedInformation.GetFoliationLog(root,**kwargs)
        elif element == "discontinuityLog": response = ExtractedInformation.GetDiscontinuityLog(root,**kwargs)
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
        The name of the file to load data from
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
        valid = Version.CheckVersionValid(rootgrp, verbose) and valid
        valid = Extents.CheckExtentsValid(rootgrp, xyzGridSize, verbose) and valid
        valid = DataCollection.CheckDataCollectionValid(rootgrp, verbose) and valid
        valid = ExtractedInformation.CheckExtractedInformationValid(rootgrp, verbose) and valid
        valid = StructuralModels.CheckStructuralModelsValid(rootgrp,xyzGridSize, verbose) and valid
        valid = GeophysicalModels.CheckGeophysicalModelsValid(rootgrp, verbose) and valid
        valid = ProbabilityModels.CheckProbabilityModelValid(rootgrp, verbose) and valid
        
        # Close and report
        rootgrp.close()

        if valid:
            print("\nThis is a valid Loop Project File")
        else:
            print("\nThis Loop Project File is NOT valid")
    return valid

# Explicitly setup Compound Types used in the LoopProjectFile module
faultObservationType = numpy.dtype([('eventId','<u4'),
                        ('easting','<f8'),('northing','<f8'),('altitude','<f8'),
                        ('dipDir','<f8'),('dip','<f8'),('dipPolarity','<f8'),
                        ('val','<f8'),('displacement','<f8')])

foldObservationType = numpy.dtype([('eventId','<u4'),
                        ('easting','<f8'),('northing','<f8'),('altitude','<f8'),
                        ('axisX','<f8'),('axisY','<f8'),('axisZ','<f8'),
                        ('foliation','S30'),('whatIsFolded','S30')])

foliationObservationType = numpy.dtype([('eventId','<u4'),
                        ('easting','<f8'),('northing','<f8'),('altitude','<f8'),
                        ('dipDir','<f8'),('dip','<f8')])

discontinuityObservationType = numpy.dtype([('eventId','<u4'),
                        ('easting','<f8'),('northing','<f8'),('altitude','<f8'),
                        ('dipDir','<f8'),('dip','<f8')])

contactObservationType = numpy.dtype([('layerId','<u4'),
                        ('easting','<f8'),('northing','<f8'),('altitude','<f8')])

stratigraphicObservationType = numpy.dtype([('layerId','<u4'),
                        ('easting','<f8'),('northing','<f8'),('altitude','<f8'),
                        ('dipDir','<f8'),('dip','<f8'),('dipPolarity','<f8'),
                        ('layer','S30')])

faultEventType = numpy.dtype([('eventId','<u4'),
                        ('minAge','<f8'),('maxAge','<f8'),('avgDisplacement','<f8'),
                        ('enabled','u1'),('name','S30')])

foldEventType = numpy.dtype([('eventId','<u4'),
                        ('minAge','<f8'),('maxAge','<f8'),
                        ('periodic','u1'),('wavelength','<f8'),('amplitude','<f8'),
                        ('asymmetry','u1'),('asymmetryShift','<f8'),
                        ('secondaryWavelength','<f8'),('secondaryAmplitude','<f8'),
                        ('enabled','u1'),('name','S30')])

foliationEventType = numpy.dtype([('eventId','<u4'),
                        ('minAge','<f8'),('maxAge','<f8'),
                        ('lowerScalarValue','<f8'),('upperScalarValue','<f8'),
                        ('enabled','u1'),('name','S30')])

discontinuityEventType = numpy.dtype([('eventId','<u4'),
                        ('minAge','<f8'),('maxAge','<f8'),
                        ('scalarValue','<f8'),('enabled','u1'),('name','S30')])

stratigraphicLayerType = numpy.dtype([('layerId','<u4'),
                        ('minAge','<f8'),('maxAge','<f8'),
                        ('formation','S20'),('thickness','f8'),
                        ('colour1Red','u1'),('colour1Green','u1'),('colour1Blue','u1'),
                        ('colour2Red','u1'),('colour2Green','u1'),('colour2Blue','u1')])

def ConvertDataFrame(df,dtype):
    if isinstance(df,pandas.DataFrame):
        return numpy.array(df.to_records(index=False).tolist(),dtype=dtype)
    else:
        raise NotADataFrame
