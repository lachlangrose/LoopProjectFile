import netCDF4

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

# Get Data Collection group if present
def GetDataCollectionGroup(rootGroup, verbose=False):
    """
    **GetDataCollectionGroup** - Gets the data collection group node within the
    netCDF Loop Project File
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    
    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a netCDF4 Group containing all the third-party data for this
        project
        
    """
    if "DataCollection" in rootGroup.groups:
        dcGroup = rootGroup.groups.get("DataCollection")
        return {"errorFlag":False,"value":dcGroup}
    else:
        errString = "No Data Collection Group Present on access request"
        if verbose: print(errString)
        return {"errorFlag":True,"errorString":errString}

#Extract observations
def GetObservations(root, indexList=[], indexRange=(0,0), keyword="", verbose=False):
    response = {"errorFlag":False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]: response = resp
    else:
        dcGroup = resp["value"]
        data = []
        # Select all option
        if indexList==[] and len(indexRange) == 2 and indexRange[0] == 0 \
          and indexRange[1] == 0 and keyword == "":
            # Create list of observations as:
            # ((northing,easting,altitude),strike,dip,type,layer)
            for i in range(0,dcGroup.dimensions['index'].size):
                data.append(((dcGroup.variables.get('northing')[i].data.item(), \
                          dcGroup.variables.get('easting')[i].data.item(), \
                          dcGroup.variables.get('altitude')[i].data.item()), \
                          dcGroup.variables.get('strike')[i].data.item(), \
                          dcGroup.variables.get('dip')[i].data.item(), \
                          dcGroup.variables.get('type')[i], \
                          dcGroup.variables.get('layer')[i]))
            response["value"] = data
        # Select based on keyword and list of indices option
        elif keyword != "" and indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < dcGroup.dimensions['index'].size \
                    and dcGroup.variables.get('layer')[i] == keyword:
                    data.append(((dcGroup.variables.get('northing')[i].data.item(), \
                              dcGroup.variables.get('easting')[i].data.item(), \
                              dcGroup.variables.get('altitude')[i].data.item()), \
                              dcGroup.variables.get('strike')[i].data.item(), \
                              dcGroup.variables.get('dip')[i].data.item(), \
                              dcGroup.variables.get('type')[i], \
                              dcGroup.variables.get('layer')[i]))
            response["value"] = data
        # Select based on keyword option
        elif keyword != "":
            for i in range(0,dcGroup.dimensions['index'].size):
                if dcGroup.variables.get('layer')[i] == keyword:
                    data.append(((dcGroup.variables.get('northing')[i].data.item(), \
                              dcGroup.variables.get('easting')[i].data.item(), \
                              dcGroup.variables.get('altitude')[i].data.item()), \
                              dcGroup.variables.get('strike')[i].data.item(), \
                              dcGroup.variables.get('dip')[i].data.item(), \
                              dcGroup.variables.get('type')[i], \
                              dcGroup.variables.get('layer')[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < dcGroup.dimensions['index'].size:
                    data.append(((dcGroup.variables.get('northing')[i].data.item(), \
                              dcGroup.variables.get('easting')[i].data.item(), \
                              dcGroup.variables.get('altitude')[i].data.item()), \
                              dcGroup.variables.get('strike')[i].data.item(), \
                              dcGroup.variables.get('dip')[i].data.item(), \
                              dcGroup.variables.get('type')[i], \
                              dcGroup.variables.get('layer')[i]))
            response["value"] = data
        # Select based on indices range option
        elif len(indexRange) == 2 and indexRange[0] >= 0 and indexRange[1] >= indexRange[0]:
            for i in range(indexRange[0],indexRange[1]):
                if int(i) >= 0 and int(i) < dcGroup.dimensions['index'].size:
                    data.append(((dcGroup.variables.get('northing')[i].data.item(), \
                              dcGroup.variables.get('easting')[i].data.item(), \
                              dcGroup.variables.get('altitude')[i].data.item()), \
                              dcGroup.variables.get('strike')[i].data.item(), \
                              dcGroup.variables.get('dip')[i].data.item(), \
                              dcGroup.variables.get('type')[i], \
                              dcGroup.variables.get('layer')[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose: print(errStr)
            response = {"errorFlag":True,"errString":errStr}
    return response


# Set observation
def SetObservations(root, data, amend=False, verbose=False):
    """
    **SetObservations** - Saves a list of observation in ((northing,easting,
    altitude),strike,dip,layer) format into the netCDF Loop Project File
    
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
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        dcGroup = root.createGroup("DataCollection")
        dcGroup.createDimension("index",None)
        dcGroup.createVariable('northing','f8',('index'),zlib=True,complevel=9,fill_value=0)
        dcGroup.createVariable('easting' ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        dcGroup.createVariable('altitude','f8',('index'),zlib=True,complevel=9,fill_value=0)
        dcGroup.createVariable('strike'  ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        dcGroup.createVariable('dip'     ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        dcGroup.createVariable('type'    ,'S20',('index'),zlib=True,complevel=9,fill_value=0)
        dcGroup.createVariable('layer'   ,'S20',('index'),zlib=True,complevel=9,fill_value=0)
        # Check creation worked??
    else:
        dcGroup = resp["value"]
    if dcGroup:
        northingLocation = dcGroup.variables['northing']
        eastingLocation = dcGroup.variables['easting']
        altitudeLocation = dcGroup.variables['altitude']
        strikeLocation = dcGroup.variables['strike']
        dipLocation = dcGroup.variables['dip']
        typeLocation = dcGroup.variables['type']
        layerLocation = dcGroup.variables['layer']
        if amend: index = dcGroup.dimensions['index'].size
        else: index = 0
        for i in data:
            ((northing,easting,altitude),strike,dip,dType,layer) = i
            northingLocation[index] = northing
            eastingLocation[index] = easting
            altitudeLocation[index] = altitude
            strikeLocation[index] = strike
            dipLocation[index] = dip
            typeLocation[index] = dType
            layerLocation[index] = layer
            index += 1
    else:
        errStr = "(ERROR) Creating data collection group for observation setting"
        if verbose: print(errStr)
        response = {"errorFlag":True,"errString":errStr}
    return response
