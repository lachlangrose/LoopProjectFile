# import netCDF4


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
        if verbose:
            print("  Geophysical Models Group Present")
        gmGroup = rootGroup.groups.get("GeophysicalModels")
        if verbose:
            print(gmGroup)
    else:
        if verbose:
            print("No Geophysical Models Group Present")
    return valid
