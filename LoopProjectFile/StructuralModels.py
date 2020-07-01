import netCDF4
import LoopProjectFile.Extents as Extents

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
            smGridSize = [smGroup.dimensions["easting"].size,smGroup.dimensions["northing"].size,smGroup.dimensions["depth"].size]
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

# Get Structural Models group if present
def GetStructuralModelsGroup(rootGroup, verbose=False):
    """
    **GetStructuralModelsGroup** - Gets the stuctural models group node within the
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
        errStr = "No Structural Models Group Present on access request"
        if verbose: print(errStr)
        return {"errorFlag":True,"errorString":errStr}


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
    resp = GetStructuralModelsGroup(root)
    if resp["errorFlag"]: response = resp
    else:
        smGroup = resp["value"]
        # Check data exists at the specified index value 
        # TODO Better checking to remove back indexing or out-of-bounds access
#        if smGroup.variables.
        data = smGroup.variables.get('data')[:,:,:,index].data
        if verbose: print("The shape of the structuralModel is", data.shape)
        response["value"] = data
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
    Extents.CheckExtentsValid(root, xyzGridSize, verbose)
    resp = GetStructuralModelsGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        structuralModelsGroup = root.createGroup("StructuralModels")
        structuralModelsGroup.createDimension("easting",xyzGridSize[0])
        structuralModelsGroup.createDimension("northing",xyzGridSize[1])
        structuralModelsGroup.createDimension("depth",xyzGridSize[2])
        structuralModelsGroup.createDimension("index",None)
        structuralModelsGroup.createVariable('data','f4',('easting','northing','depth','index'),zlib=True,complevel=9,fill_value=0)
        structuralModelsGroup.createVariable('minVal','f4',('index'),zlib=True,complevel=9,fill_value=0)
        structuralModelsGroup.createVariable('maxVal','f4',('index'),zlib=True,complevel=9,fill_value=0)
        structuralModelsGroup.createVariable('valid','S1',('index'),zlib=True,complevel=9,fill_value=0)
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
            minValLocation = structuralModelsGroup.variables['minVal']
            minValLocation[index] = data.min()
            maxValLocation = structuralModelsGroup.variables['maxVal']
            maxValLocation[index] = data.max()
            validLocation = structuralModelsGroup.variables['valid']
            validLocation[index] = 1
    return response