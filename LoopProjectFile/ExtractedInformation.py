import netCDF4
import LoopProjectFile.LoopProjectFileUtils as LoopProjectFileUtils

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
    return LoopProjectFileUtils.GetGroup(rootGroup,verbose)

def GetStratigraphicInformationGroup(rootGroup,verbose=False):
    response = {"errorFlag":False}
    resp = GetExtractedInformationGroup(rootGroup,verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"],"StratigraphicInformation",verbose)

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
        # Create Structural Models Group and add data shape based on project extents
        eiGroup = root.createGroup("ExtractedInformation")
    else:
        eiGroup = resp["value"]

    resp = GetStratigraphicInformationGroup(root)
    if resp["errorFlag"]:
        group = eiGroup.createGroup("StratigraphicInformation")
        group.createDimension("index",None)
        group.createVariable('formation','S20',('index'),zlib=True,complevel=9,fill_value=0)
        group.createVariable('thickness' ,'f8',('index'),zlib=True,complevel=9,fill_value=0)
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
        response = {"errorFlag":True,"errString":errStr}
    return response
