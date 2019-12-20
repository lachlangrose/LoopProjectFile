import netCDF4

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
    