import netCDF4
import LoopProjectFile.LoopProjectFileUtils as LoopProjectFileUtils

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
    return LoopProjectFileUtils.GetGroup(rootGroup,"DataCollection",verbose)

# Get Orientations group if present
def GetOrientationsGroup(rootGroup,verbose=False):
    response = {"errorFlag":False}
    resp = GetDataCollectionGroup(rootGroup,verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"],"Orientations",verbose)

# Get Contacts group if present
def GetContactsGroup(rootGroup,verbose=False):
    response = {"errorFlag":False}
    resp = GetDataCollectionGroup(rootGroup,verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"],"Contacts",verbose)

#Extract orientations
def GetOrientations(root, indexList=[], indexRange=(0,0), keyword="", verbose=False):
    response = {"errorFlag":False}
    resp = GetOrientationsGroup(root)
    if resp["errorFlag"]: response = resp
    else:
        group = resp["value"]
        data = []
        # Select all option
        if indexList==[] and len(indexRange) == 2 and indexRange[0] == 0 \
          and indexRange[1] == 0 and keyword == "":
            # Create list of orientations as:
            # ((northing,easting,altitude),dipdir,dip,formation,layer)
            for i in range(0,group.dimensions['index'].size):
                data.append(((group.variables.get('northing')[i].data.item(), \
                          group.variables.get('easting')[i].data.item(), \
                          group.variables.get('altitude')[i].data.item()), \
                          group.variables.get('dipdir')[i].data.item(), \
                          group.variables.get('dip')[i].data.item(), \
                          group.variables.get('polarity')[i].data.item(), \
                          group.variables.get('formation')[i], \
                          group.variables.get('layer')[i]))
            response["value"] = data
        # Select based on keyword and list of indices option
        elif keyword != "" and indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < group.dimensions['index'].size \
                    and group.variables.get('layer')[i] == keyword:
                    data.append(((group.variables.get('northing')[i].data.item(), \
                              group.variables.get('easting')[i].data.item(), \
                              group.variables.get('altitude')[i].data.item()), \
                              group.variables.get('dipdir')[i].data.item(), \
                              group.variables.get('dip')[i].data.item(), \
                              group.variables.get('polarity')[i].data.item(), \
                              group.variables.get('formation')[i], \
                              group.variables.get('layer')[i]))
            response["value"] = data
        # Select based on keyword option
        elif keyword != "":
            for i in range(0,group.dimensions['index'].size):
                if group.variables.get('layer')[i] == keyword:
                    data.append(((group.variables.get('northing')[i].data.item(), \
                              group.variables.get('easting')[i].data.item(), \
                              group.variables.get('altitude')[i].data.item()), \
                              group.variables.get('dipdir')[i].data.item(), \
                              group.variables.get('dip')[i].data.item(), \
                              group.variables.get('polarity')[i].data.item(), \
                              group.variables.get('formation')[i], \
                              group.variables.get('layer')[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append(((group.variables.get('northing')[i].data.item(), \
                              group.variables.get('easting')[i].data.item(), \
                              group.variables.get('altitude')[i].data.item()), \
                              group.variables.get('dipdir')[i].data.item(), \
                              group.variables.get('dip')[i].data.item(), \
                              group.variables.get('polarity')[i].data.item(), \
                              group.variables.get('formation')[i], \
                              group.variables.get('layer')[i]))
            response["value"] = data
        # Select based on indices range option
        elif len(indexRange) == 2 and indexRange[0] >= 0 and indexRange[1] >= indexRange[0]:
            for i in range(indexRange[0],indexRange[1]):
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append(((group.variables.get('northing')[i].data.item(), \
                              group.variables.get('easting')[i].data.item(), \
                              group.variables.get('altitude')[i].data.item()), \
                              group.variables.get('dipdir')[i].data.item(), \
                              group.variables.get('dip')[i].data.item(), \
                              group.variables.get('polarity')[i].data.item(), \
                              group.variables.get('formation')[i], \
                              group.variables.get('layer')[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose: print(errStr)
            response = {"errorFlag":True,"errorString":errStr}
    return response


# Set orientations
def SetOrientations(root, data, amend=False, verbose=False):
    """
    **SetOrientations** - Saves a list of orientations in ((northing,easting,
    altitude),dipdir,dip,layer) format into the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: list of ((X,Y,Z),dipdir,dip,polarity,formation,layer)
        The data to save
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
    else:
        dcGroup = resp["value"]

    resp = GetOrientationsGroup(root)
    if resp["errorFlag"]:
        group = dcGroup.createGroup("Orientations")
        group.createDimension("index",None)
        group.createVariable('northing' ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('easting'  ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('altitude' ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('dipdir'   ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('dip'      ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('polarity' ,'i4',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('formation','S20',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('layer'    ,'S20',('index'),zlib=True,complevel=9,fill_value=0)
    else:
        group = resp["value"]

    if group:
        northingLocation = group.variables['northing']
        eastingLocation = group.variables['easting']
        altitudeLocation = group.variables['altitude']
        dipdirLocation = group.variables['dipdir']
        dipLocation = group.variables['dip']
        polarityLocation = group.variables['polarity']
        formationLocation = group.variables['formation']
        layerLocation = group.variables['layer']
        if amend: index = group.dimensions['index'].size
        else: index = 0
        for i in data:
            ((northing,easting,altitude),dipdir,dip,polarity,formation,layer) = i
            northingLocation[index] = northing
            eastingLocation[index] = easting
            altitudeLocation[index] = altitude
            dipdirLocation[index] = dipdir
            dipLocation[index] = dip
            polarityLocation[index] = polarity
            formationLocation[index] = formation
            layerLocation[index] = layer
            index += 1
    else:
        errStr = "(ERROR) Failed to Create orientation group for orientations setting"
        if verbose: print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    return response

# Set contacts
def SetContacts(root, data, amend=False, verbose=False):
    """
    **SetContacts** - Saves a list of contacts in ((northing,easting,
    altitude),formation) format into the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: list of ((X,Y,Z),formation)
        The data to save
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
    else:
        dcGroup = resp["value"]

    resp = GetContactsGroup(root)
    if resp["errorFlag"]:
        group = dcGroup.createGroup("Contacts")
        group.createDimension("index",None)
        group.createVariable('northing' ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('easting'  ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('altitude' ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('formation','S20',('index'),zlib=True,complevel=9,fill_value=0)
    else:
        group = resp["value"]

    if group:
        northingLocation = group.variables['northing']
        eastingLocation = group.variables['easting']
        altitudeLocation = group.variables['altitude']
        formationLocation = group.variables['formation']
        if amend: index = group.dimensions['index'].size
        else: index = 0
        for i in data:
            ((northing,easting,altitude),formation) = i
            northingLocation[index] = northing
            eastingLocation[index] = easting
            altitudeLocation[index] = altitude
            formationLocation[index] = formation
            index += 1
    else:
        errStr = "(ERROR) Failed to Create contacts group for contact setting"
        if verbose: print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    return response

#Extract contacts 
def GetContacts(root, indexList=[], indexRange=(0,0), keyword="", verbose=False):
    response = {"errorFlag":False}
    resp = GetContactsGroup(root)
    if resp["errorFlag"]: response = resp
    else:
        group = resp["value"]
        data = []
        # Select all option
        if indexList==[] and len(indexRange) == 2 and indexRange[0] == 0 \
          and indexRange[1] == 0 and keyword == "":
            # Create list of orientations as:
            # ((northing,easting,altitude),dipdir,dip,formation,layer)
            for i in range(0,group.dimensions['index'].size):
                data.append(((group.variables.get('northing')[i].data.item(), \
                          group.variables.get('easting')[i].data.item(), \
                          group.variables.get('altitude')[i].data.item()), \
                          group.variables.get('formation')[i]))
            response["value"] = data
        # Select based on keyword and list of indices option
        elif keyword != "" and indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < group.dimensions['index'].size \
                    and group.variables.get('layer')[i] == keyword:
                    data.append(((group.variables.get('northing')[i].data.item(), \
                              group.variables.get('easting')[i].data.item(), \
                              group.variables.get('altitude')[i].data.item()), \
                              group.variables.get('formation')[i]))
            response["value"] = data
        # Select based on keyword option
        elif keyword != "":
            for i in range(0,group.dimensions['index'].size):
                if group.variables.get('layer')[i] == keyword:
                    data.append(((group.variables.get('northing')[i].data.item(), \
                              group.variables.get('easting')[i].data.item(), \
                              group.variables.get('altitude')[i].data.item()), \
                              group.variables.get('formation')[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append(((group.variables.get('northing')[i].data.item(), \
                              group.variables.get('easting')[i].data.item(), \
                              group.variables.get('altitude')[i].data.item()), \
                              group.variables.get('formation')[i]))
            response["value"] = data
        # Select based on indices range option
        elif len(indexRange) == 2 and indexRange[0] >= 0 and indexRange[1] >= indexRange[0]:
            for i in range(indexRange[0],indexRange[1]):
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append(((group.variables.get('northing')[i].data.item(), \
                              group.variables.get('easting')[i].data.item(), \
                              group.variables.get('altitude')[i].data.item()), \
                              group.variables.get('formation')[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose: print(errStr)
            response = {"errorFlag":True,"errorString":errStr}
    return response