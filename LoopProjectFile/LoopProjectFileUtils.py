import netCDF4

def GetGroup(node,groupName,verbose=False):
    """
    **GetGroup** - Gets the requested group node within the
    netCDF Loop Project File
    
    Parameters
    ----------
    rootGroup: netCDF4.Group
        A group node of a Loop Project File
    
    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a netCDF4 Group containing data for this project
        
    """
    if groupName in node.groups:
        return {"errorFlag":False,"value":node.groups.get(groupName)}
    else:
        errString = "No ",groupName," present on access request"
        if verbose: print(errString)
        return {"errorFlag":True,"errorString":errString}

