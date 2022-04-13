from .LoopProjectFile import Get, Set, CreateBasic, OpenProjectFile, CheckFileValid,CheckFileIsLoopProjectFile
from .LoopProjectFileUtils import ElementToDataframe, ElementFromDataframe
import LoopProjectFile
import pandas as pd
import numpy as np  
compoundTypeMap = {"version":None,
                "extents":None,
                "strModel":None,
                "faultObservations":LoopProjectFile.faultObservationType,
                "foldObservations":LoopProjectFile.foldObservationType,
                "foliationObservations":LoopProjectFile.foliationObservationType,
                "discontinuityObservations":LoopProjectFile.discontinuityObservationType,
                "stratigraphicObservations":LoopProjectFile.stratigraphicObservationType,
                "contacts":LoopProjectFile.contactObservationType,
                "stratigraphicLog":LoopProjectFile.stratigraphicLayerType,
                "faultLog":LoopProjectFile.faultEventType,
                "foldLog":None,
                "foliationLog":None,
                "discontinuityLog":None,
                "dataCollectionConfig":None,
                "dataCollectionSources":None,
                "eventRelationships":None,
                "structuralModelsConfig":None}

class ProjectFile:
    def __init__(self, project_filename):
        """Python interface for the Loop project file.

        Parameters
        ----------
        project_filename : string
            name/path of projectfile

        Raises
        ------
        BaseException
            Exception if project file doesn't exist
        """
        valid  = CheckFileIsLoopProjectFile(project_filename)
        if valid == False:
            raise BaseException('Project file does not exist') 
        self.project_filename = project_filename
        self.element_names = ["version",
                "extents",
                "strModel",
                "faultObservations",
                "foldObservations",
                "foliationObservations",
                "discontinuityObservations",
                "stratigraphicObservations",
                "contacts",
                "stratigraphicLog",
                "faultLog",
                "foldLog",
                "foliationLog",
                "discontinuityLog",
                "dataCollectionConfig",
                "dataCollectionSources",
                "eventRelationships",
                "structuralModelsConfig"]
    
    @classmethod
    def new(cls, filename):
        """Create a new project file.

        Parameters
        ----------
        filename : string
            name of projectfile

        Returns
        -------
        ProjectFile
            the new projectfile class
        """
        LoopProjectFile.CreateBasic(filename)
        projectfile = ProjectFile(filename)
        return projectfile
    
    def is_valid(self):
        return CheckFileValid(self.project_filename)

    def _add_names_to_df(self, log, df):
        df['name'] = 'none'
        for stratigraphic_id in log.index:
            df.loc[df['layerId'] == stratigraphic_id,'name'] = \
            log.loc[stratigraphic_id,'name']


    @property
    def extents(self):
        resp = Get(self.project_filename,'extents')
        if resp['errorFlag'] == True:
            return None
        return resp['value']

    @extents.setter
    def extents(self,extents):
        Set(self.project_filename,'extents',**extents)
        pass
    
    
    @property
    def version(self):
        resp = Get(self.project_filename,'version')
        if resp['errorFlag'] == True:
            return None
        return "{}.{}.{}".format(*resp['value'])

    @property
    def origin(self):
        origin = np.zeros(3)
        origin[0] = self.extents['utm'][2]
        origin[1] = self.extents['utm'][4]
        origin[2] = self.extents['depth'][0]
        return origin
    @property
    def maximum(self):
        maximum = np.zeros(3)
        maximum[0] = self.extents['utm'][3]
        maximum[1] = self.extents['utm'][5]
        maximum[2] = self.extents['depth'][1]
        return maximum
    # should we be able to set the version or should this be fixed?
    # @version.setter
    # def version(self, version):
    #     if isinstance(version, str):
    #         version = version.split('.')
    #         if len(version) != 3:
    #             raise ValueError('Version must be in the format major.minor.patch')
    #         version = list(map(int, version))
    #     resp = Set(self.project_filename,'version',version=version)
    #     if resp['errorFlag'] == True:
    #         raise ValueError('Version must be in the format major.minor.patch')        

    @property
    def faultObservations(self):
        return self.__getitem__('faultObservations')

    @faultObservations.setter
    def faultObservations(self, value):
        self.__setitem__('faultObservations', value)
        

    @property
    def faultLocations(self):
        df = self.__getitem__('faultObservations')
        # self._add_names_to_df(self.faultLog,df)
        return df.loc[df['posOnly']==1,:]

    @faultLocations.setter
    def faultLocations(self, value):
        df = self.__getitem__('faultObservations')
        value = pd.concat([value,df.loc[df['posOnly']==1,:]])
        value.reset_index(inplace=True)
        self.__setitem__('faultObservations', value)
        

    @property
    def faultOrientations(self):
        df = self.__getitem__('faultObservations')
        return df.loc[df['posOnly']==0,:]

    @faultOrientations.setter
    def faultOrientations(self, value):
        df = self.__getitem__('faultObservations')
        value = pd.concat([value,df.loc[df['posOnly']==0,:]])
        value.reset_index(inplace=True)
        self.__setitem__('faultObservations', value)
        

    @property
    def faultLog(self):
        return self.__getitem__('faultLog').set_index('name')
    
    @faultLog.setter
    def faultLog(self, value):
        self.__setitem__('faultLog',value)
        

    @property
    def foliationObservations(self):
        return self.__getitem__('foliationObservations')

    @foliationObservations.setter
    def foliationObservations(self, value):
        self.__setitem__('foliationObservations',value)
        

    @property
    def foldObservations(self):
        return self.__getitem__('foldObservations')

    @foldObservations.setter
    def foldObservations(self, value):
        self.__setitem__('foldObservations', value)
        

    @property
    def stratigraphicLog(self):
        return self.__getitem__('stratigraphicLog')

    @stratigraphicLog.setter
    def stratigraphicLog(self, value):
        self.__setitem__('stratigraphicLog', value)
        

    @property
    def stratigraphyLocations(self):
        df = self.__getitem__('contacts')
        self._add_names_to_df(self.stratigraphicLog,df)
        return df

    @stratigraphyLocations.setter
    def stratigraphyLocations(self, value):
        self.__setitem__('contacts',value)

    @property
    def stratigraphyOrientations(self):
        df = self.__getitem__('stratigraphicObservations')
        self._add_names_to_df(self.stratigraphicLog,df)
        return df

    @stratigraphyOrientations.setter
    def stratigraphyOrientations(self, value):
        self.__setitem__('stratigraphicObservations',value)
        
        
    def _ipython_key_completions_(self):
        return self.element_names

    def __getitem__(self, element):
        resp = Get(self.project_filename,element)
        if resp['errorFlag'] == False:
            if compoundTypeMap[element] == None:
                return resp['value']
            else: 
                return LoopProjectFile.ElementToDataframe(self.project_filename,
                                                                element,compoundTypeMap[element])
        # return ProjectFileElement(self.project_filename, element).value
    
    def __setitem__(self, element, value):
        if compoundTypeMap[element] == None:
            Set(self.project_filename,element,  value)
        else:
            if isinstance(value,pd.DataFrame):
                names = compoundTypeMap[element].names
                if pd.Index(names).isin(value.columns).all():
                    ElementFromDataframe(self.project_filename,value.loc[:,names],element,compoundTypeMap[element])                
                else:
                    raise ValueError('Dataframe must have columns: {}'.format(names))
            else:
                raise TypeError('Cannot set project file with {}'.format(type(value)))

