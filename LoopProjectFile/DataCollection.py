import netCDF4
import LoopProjectFile.LoopProjectFileUtils as LoopProjectFileUtils
import LoopProjectFile

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

# Get Observations group if present
def GetObservationsGroup(rootGroup,verbose=False):
    response = {"errorFlag":False}
    resp = GetDataCollectionGroup(rootGroup,verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"],"Observations",verbose)

# Get Contacts group if present
def GetContactsGroup(rootGroup,verbose=False):
    response = {"errorFlag":False}
    resp = GetDataCollectionGroup(rootGroup,verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"],"Contacts",verbose)

def CreateObservationGroup(dataCollectionGroup):
    obGroup = dataCollectionGroup.createGroup("Observations")
    obGroup.createDimension("faultObservationIndex",None)
    obGroup.createDimension("foldObservationIndex",None)
    obGroup.createDimension("foliationObservationIndex",None)
    obGroup.createDimension("discontinuityObservationIndex",None)
    obGroup.createDimension("stratigraphicObservationIndex",None)
    faultObservationType_t = obGroup.createCompoundType(LoopProjectFile.faultObservationType,'FaultObservation')
    obGroup.createVariable('faultObservations',faultObservationType_t,('faultObservationIndex'),zlib=True,complevel=9)
    foldObservationType_t = obGroup.createCompoundType(LoopProjectFile.foldObservationType,'FoldObservation')
    obGroup.createVariable('foldObservations',foldObservationType_t,('foldObservationIndex'),zlib=True,complevel=9)
    foliationObservationType_t = obGroup.createCompoundType(LoopProjectFile.foliationObservationType,'FoliationObservation')
    obGroup.createVariable('foliationObservations',foliationObservationType_t,('foliationObservationIndex'),zlib=True,complevel=9)
    discontinuityObservationType_t = obGroup.createCompoundType(LoopProjectFile.discontinuityObservationType,'DiscontinuityObservation')
    obGroup.createVariable('discontinuityObservations',discontinuityObservationType_t,('discontinuityObservationIndex'),zlib=True,complevel=9)
    stratigraphicObservationType_t = obGroup.createCompoundType(LoopProjectFile.stratigraphicObservationType,'StratigraphicObservation')
    obGroup.createVariable('stratigraphicObservations',stratigraphicObservationType_t,('stratigraphicObservationIndex'),zlib=True,complevel=9)
    return obGroup

#Extract observations
def GetObservations(root, indexName, variableName, indexList=[], indexRange=(0,0), keyword="", verbose=False):
    response = {"errorFlag":False}
    resp = GetObservationsGroup(root)
    if resp["errorFlag"]: response = resp
    else:
        if verbose: print("Getting variable " + variableName)
        oGroup = resp["value"]
        data = []
        # Select all option
        if indexList==[] and len(indexRange) == 2 and indexRange[0] == 0 \
          and indexRange[1] == 0 and keyword == "":
            if verbose: print("Getting all")
            # Create list of observations as:
            # ((easting,northing,altitude),dipdir,dip,formation,layer)
            for i in range(0,oGroup.dimensions[indexName].size):
                data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on keyword and list of indices option
        elif keyword != "" and indexList != []:
            if verbose: print("Getting keyword and index list")
            for i in indexList:
                if int(i) >= 0 and int(i) < oGroup.dimensions[indexName].size \
                    and oGroup.variables.get(variableName)[i] == keyword:
                    data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on keyword option
        elif keyword != "":
            if verbose: print("Getting keyword")
            for i in range(0,oGroup.dimensions[indexName].size):
                if oGroup.variables.get(variableName)[i] == keyword:
                    data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            if verbose: print("Getting index list")
            for i in indexList:
                if int(i) >= 0 and int(i) < oGroup.dimensions[indexName].size:
                    data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on indices range option
        elif len(indexRange) == 2 and indexRange[0] >= 0 and indexRange[1] >= indexRange[0]:
            if verbose: print("Getting index range")
            for i in range(indexRange[0],indexRange[1]):
                if int(i) >= 0 and int(i) < oGroup.dimensions[indexName].size:
                    data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose: print(errStr)
            response = {"errorFlag":True,"errorString":errStr}
    return response

def GetFaultObservations(root, indexList=[], indexRange=(0,0), keyword="", verbose=False):
    return GetObservations(root,'faultObservationIndex','faultObservations',indexList,indexRange,keyword,verbose)

def GetFoldObservations(root, indexList=[], indexRange=(0,0), keyword="", verbose=False):
    return GetObservations(root,'foldObservationIndex','foldObservations',indexList,indexRange,keyword,verbose)

def GetFoliationObservations(root, indexList=[], indexRange=(0,0), keyword="", verbose=False):
    return GetObservations(root,'foliationObservationIndex','foliationObservations',indexList,indexRange,keyword,verbose)

def GetDiscontinuityObservations(root, indexList=[], indexRange=(0,0), keyword="", verbose=False):
    return GetObservations(root,'discontinuityObservationIndex','discontinuityObservations',indexList,indexRange,keyword,verbose)

def GetStratigraphicObservations(root, indexList=[], indexRange=(0,0), keyword="", verbose=False):
    return GetObservations(root,'stratigraphicObservationIndex','stratigraphicObservations',indexList,indexRange,keyword,verbose)

# Set observations
# Set observations
def SetObservations(root, data, indexName, variableName, append=False, verbose=False):
    """
    **SetObservations** - Saves a list of observations in ((easting,northing,
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

    resp = GetObservationsGroup(root)
    if resp["errorFlag"]:
        oGroup = CreateObservationGroup(dcGroup)
    else:
        oGroup = resp["value"]

    if oGroup:
        observationLocation = oGroup.variables[variableName]
        if append: index = oGroup.dimensions[indexName].size
        else: index = 0
        for i in data:
            observationLocation[index] = i
            index += 1
    else:
        errStr = "(ERROR) Failed to Create observations group for observations setting"
        if verbose: print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    return response

def SetFaultObservations(root, data, append=False, verbose=False):
    return SetObservations(root, data, 'faultObservationIndex', 'faultObservations', append, verbose)

def SetFoldObservations(root, data, append=False, verbose=False):
    return SetObservations(root, data, 'foldObservationIndex', 'foldObservations', append, verbose)

def SetFoliationObservations(root, data, append=False, verbose=False):
    return SetObservations(root, data, 'foliationObservationIndex', 'foliationObservations', append, verbose)

def SetDiscontinuityObservations(root, data, append=False, verbose=False):
    return SetObservations(root, data, 'discontinuityObservationIndex', 'discontinuityObservations', append, verbose)

def SetStratigraphicObservations(root, data, append=False, verbose=False):
    return SetObservations(root, data, 'stratigraphicObservationIndex', 'stratigraphicObservations', append, verbose)

# Set contacts
# Set contacts
def SetContacts(root, data, append=False, verbose=False):
    """
    **SetContacts** - Saves a list of contacts in ((easting,northing,
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
        contactObservationType_t = group.createCompoundType(LoopProjectFile.contactObservationType,'contactObservationType')
        group.createVariable('contacts',contactObservationType_t,('index'),zlib=True,complevel=9)
    else:
        group = resp["value"]

    if group:
        contactsLocation = group.variables['contacts']
        if append: index = group.dimensions['index'].size
        else: index = 0
        for i in data:
            contactsLocation[index] = i
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
            # Create list of observations as:
            # ((easting,northing,altitude),dipdir,dip,formation,layer)
            for i in range(0,group.dimensions['index'].size):
                data.append((group.variables.get('contacts')[i]))
            response["value"] = data
        # Select based on keyword and list of indices option
        elif keyword != "" and indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < group.dimensions['index'].size \
                    and group.variables.get('layer')[i] == keyword:
                    data.append((group.variables.get('contacts')[i]))
            response["value"] = data
        # Select based on keyword option
        elif keyword != "":
            for i in range(0,group.dimensions['index'].size):
                if group.variables.get('layer')[i] == keyword:
                    data.append((group.variables.get('contacts')[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append((group.variables.get('contacts')[i]))
            response["value"] = data
        # Select based on indices range option
        elif len(indexRange) == 2 and indexRange[0] >= 0 and indexRange[1] >= indexRange[0]:
            for i in range(indexRange[0],indexRange[1]):
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append((group.variables.get('contacts')[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose: print(errStr)
            response = {"errorFlag":True,"errorString":errStr}
    return response