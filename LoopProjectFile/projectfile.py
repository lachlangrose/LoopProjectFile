from .LoopProjectFile import Get, Set, CreateBasic, OpenProjectFile
# from .LoopProjectFileUtils import ElementToDataframe, ElementFromDataframe
import LoopProjectFile

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
        error  = OpenProjectFile(project_filename)
        if error['errorFlag']:
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
        return self.__init__(filename)
    
    def _add_names_to_df(self, log, df):
        df['name'] = 'none'
        for stratigraphic_id in log.index:
            df.loc[df.index== stratigraphic_id,'name'] = \
            log.loc[stratigraphic_id,'name']


    @property
    def extents(self):
        resp = Get(self.project_filename,'extents')
        if resp['errorFlag'] == True:
            return None
        return resp['value']

    @property
    def version(self):
        resp = Get(self.project_filename,'version')
        if resp['errorFlag'] == True:
            return None
        return "{}.{}.{}".format(*resp['value'])

    @property
    def faultObservations(self):
        return self.__getitem__('faultObservations')

    @property
    def faultLocations(self):
        df = self.__getitem__('faultObservations')
        self._add_names_to_df(self.faultLog,df)
        return df.loc[df['posOnly']==1,:]

    @property
    def faultOrientations(self):
        df = self.__getitem__('faultObservations')
        self._add_names_to_df(self.faultLog,df)
        return df.loc[df['posOnly']==0,:]

    @property
    def faultLog(self):
        return self.__getitem__('faultLog')
            
    @property
    def foliationObservations(self):
        return self.__getitem__('foliationObservations')

    @property
    def foldObservations(self):
        return self.__getitem__('foldObservations')
    @property
    def stratigraphicLog(self):
        return self.__getitem__('stratigraphicLog')

    

    @property
    def stratigraphyLocations(self):
        df = self.__getitem__('contacts')
        self._add_names_to_df(self.stratigraphicLog,df)
        return df

    @property
    def stratigraphyOrientations(self):
        df = self.__getitem__('stratigraphicObservations')
        self._add_names_to_df(self.stratigraphicLog,df)
        return df

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
            Set(self.project_filename,element,value)
        else:
            LoopProjectFileUtils.ElementFromDataframe(self.project_filename,element,compoundTypeMap[self.element],value)