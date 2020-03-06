import netCDF4
import LoopProjectFile
import LoopProjectFile.LoopProjectFileUtils as LoopProjectFileUtils
import numpy

# Check Extracted Information valid if present
def CheckExtractedInformationValid(rootGroup, verbose=False):
    """
    **CheckExtractedInformationValid** - Checks for valid extracted information
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
        True if valid extracted information in project file, False otherwise.

    """
    valid = True
    if "ExtractedInformation" in rootGroup.groups:
        if verbose: print("  Extracted Information Group Present")
        eriGroup = rootGroup.groups.get("ExtractedInformation")
#        if verbose: print(eriGroup)
    else:
        if verbose: print("No Extracted Information Group Present")
    return valid

def GetExtractedInformationGroup(rootGroup, verbose=False):
    return LoopProjectFileUtils.GetGroup(rootGroup,"ExtractedInformation",verbose)

def GetStratigraphicInformationGroup(rootGroup,verbose=False):
    response = {"errorFlag":False}
    resp = GetExtractedInformationGroup(rootGroup,verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"],"StratigraphicInformation",verbose)

def GetEventLogGroup(rootGroup,verbose=False):
    response = {"errorFlag":False}
    resp = GetExtractedInformationGroup(rootGroup,verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"],"EventLog",verbose)

# Set fault log
def SetFaultLog(root, data, amend=False, verbose=False):
    response = {"errorFlag":False}
    resp = GetEventLogGroup(root)
    if resp["errorFlag"]:
        # Create  Extracted Information Group as it doesn't exist
        elGroup = root.createGroup("ExtractedInformation")
    else:
        elGroup = resp["value"]

    resp = GetEventLogGroup(root)
    if resp["errorFlag"]:
        print(resp["errorString"])
        group = elGroup.createGroup("EventLog")
        group.createDimension("index",None)
        faultEventType_t = group.createCompoundType(LoopProjectFile.faultEventType,'faultEventType')
        group.createVariable('faultEvents',faultEventType_t,('index'),zlib=True,complevel=9)
        # group.createVariable('folds','<u4,<f8,<f8,<f8,<f8,<f8,<f8,<f8,<f8,i1',('index'),zlib=True,complevel=9)
        # group.createVariable('foliations','<u4,<f8,<f8,<f8,<f8,i1',('index'),zlib=True,complevel=9)
        # group.createVariable('discontinuities','<u4,<f8,<f8,<f8,i1',('index'),zlib=True,complevel=9)
    else:
        group = resp["value"]

    if group:
        faultLocation = group.variables['faultEvents']
        # foldLocation = group.variables['folds']
        # foliationLocation = group.variables['foliations']
        # discontinuityLocation = group.variables['discontinuities']
        if amend: index = group.dimensions['index'].size
        else: index = 0
        for i in data:
            faultLocation[index] = i
            index += 1
    else:
        errStr = "(ERROR) Failed to create event log group"
        if verbose: print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    return response



# Set stratigraphic log
def SetStratigraphicLog(root, data, amend=False, verbose=False):
    """
    **SetStratigraphicLog** - Saves a list of strata in (formation,
    thickness) format into the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: list of (formation,thickness)
        The data to save
    amend: bool
        Flag of whether to amend new data to existing log
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag":False}
    resp = GetExtractedInformationGroup(root)
    if resp["errorFlag"]:
        # Create  Extracted Information Group as it doesn't exist
        eiGroup = root.createGroup("ExtractedInformation")
    else:
        eiGroup = resp["value"]

    resp = GetStratigraphicInformationGroup(root)
    if resp["errorFlag"]:
        print(resp["errorString"])
        group = eiGroup.createGroup("StratigraphicInformation")
        group.createDimension("index",None)
        group.createVariable('formation','S20',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('thickness' ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('colour1Red','u1',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('colour1Green','u1',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('colour1Blue','u1',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('colour2Red','u1',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('colour2Green','u1',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('colour2Blue','u1',('index'),zlib=True,complevel=9,fill_value=0)
    else:
        group = resp["value"]

    if group:
        formationLocation = group.variables['formation']
        thicknessLocation = group.variables['thickness']
        if amend: index = group.dimensions['index'].size
        else: index = 0
        for i in data:
            (formation,thickness) = i
            formationLocation[index] = formation
            thicknessLocation[index] = thickness
            index += 1
    else:
        errStr = "(ERROR) Failed to create stratigraphic log group for strata setting"
        if verbose: print(errStr)
        response = {"errorFlag":True,"errorString":errStr}
    return response

def GetStratigraphicLog(root, indexList=[], indexRange=(0,0), verbose=False):
    response = {"errorFlag":False}
    resp = GetStratigraphicInformationGroup(root)
    if resp["errorFlag"]: response = resp
    else:
        group = resp["value"]
        data = []
        # Select all option
        if indexList==[] and len(indexRange) == 2 and indexRange[0] == 0 \
          and indexRange[1] == 0:
            # Select all
            for i in range(0,group.dimensions['index'].size):
                data.append((group.variables.get('formation')[i], \
                          group.variables.get('thickness')[i].data.item()))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append((group.variables.get('formation')[i], \
                              group.variables.get('thickness')[i].data.item()))
            response["value"] = data
        # Select based on indices range option
        elif len(indexRange) == 2 and indexRange[0] >= 0 and indexRange[1] >= indexRange[0]:
            for i in range(indexRange[0],indexRange[1]):
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append((group.variables.get('formation')[i], \
                              group.variables.get('thickness')[i].data.item()))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose: print(errStr)
            response = {"errorFlag":True,"errorString":errStr}
    return response

def GetFaultLog(root, indexList=[], indexRange=(0,0), verbose=False):
    response = {"errorFlag":False}
    resp = GetEventLogGroup(root)
    if resp["errorFlag"]: response = resp
    else:
        group = resp["value"]
        data = []
        # Select all option
        if indexList==[] and len(indexRange) == 2 and indexRange[0] == 0 \
          and indexRange[1] == 0:
            # Select all
            for i in range(0,group.dimensions['index'].size):
                data.append((group.variables.get('folds')[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append((group.variables.get('folds')[i]))
            response["value"] = data
        # Select based on indices range option
        elif len(indexRange) == 2 and indexRange[0] >= 0 and indexRange[1] >= indexRange[0]:
            for i in range(indexRange[0],indexRange[1]):
                if int(i) >= 0 and int(i) < group.dimensions['index'].size:
                    data.append((group.variables.get('folds')[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose: print(errStr)
            response = {"errorFlag":True,"errorString":errStr}
    return response

