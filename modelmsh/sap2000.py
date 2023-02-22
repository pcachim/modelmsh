
import meshio
import gmsh
import openpyxl
import numpy as np
import pandas as pd
import pathlib
import sys
import logging
import timeit

# Element type
POINT = 15
FRAME2 = 1
FRAME3 = 8
TRIANGLE3 = 2
TRIANGLE6 = 9
QUADRANGLE4 = 3
QUADRANGLE8 = 16
QUADRANGLE9 = 10
HEXAHEDRON8 = 5
HEXAHEDRON20 = 17
HEXAHEDRON27 = 12
PYRAMID5 = 6
PYRAMID13 = 18

# Dimension
POINT = 0
LINE = 1
CURVE = 1
SURFACE = 2
VOLUME = 3


def read_line(s: str, s0, cont: bool=False) -> dict:

    if cont:
        s = s0 + s
    t = s

    variables = {}
    s = " ".join(s.strip().split())
    if len(s) == 0:
        variables["type"] = "empty"
        return variables
    
    if (s[len(s)-1] == '_'):
        variables['type'] = "cont"
        variables['previous'] = t.strip()[0:len(t)-2] + ' '
        return variables

# teste 

    if s[0:4].lower() == "file":
        variables["type"] = "empty"
        return variables
    
    if s[0:5].lower() == "table":
        variables["type"] = "table"
        # result = re.search('\"(.*)\"', " ".join(s[7:].split()))
        # variables["title"] = result.group()
        variables["title"] = " ".join(s[7:].split(r'"')).strip()
        return variables

    start = 0
    variables["type"] = "values"
    variables["values"] = {}
    wlist = []
    words = " ".join(s.split("=")).split()
    iterate = False
    jo = ""
    for w in words:
        if iterate:
            if w[len(w)-1] == r'"':
                jo += w[0:len(w)-1]
                iterate = False
                wlist.append(jo)
            else:
                jo += w + ' '
        else:
            if w[0] == r'"':
                iterate = True
                jo += w[1:] + ' '
            else:
                wlist.append(w)
    
    size = len(wlist) - 1
    for i in range(0, size, 2):
        variables["values"][wlist[i]] = wlist[i+1]

    return variables


def rename_area_nodes(elem, nodes):
    surf = gmsh.model.addDiscreteEntity(SURFACE)
    if len(nodes) == 3:
        gmsh.model.mesh.addElementsByType(surf, TRIANGLE3, [elem], nodes)
    else:
        gmsh.model.mesh.addElementsByType(surf, QUADRANGLE4, [elem], nodes)
    return

def rename_elem_nodes(joints, elem, node1, node2):
    surf = gmsh.model.addDiscreteEntity(LINE)
    lst =  [joints.at[node1, "JoinTag"],
            joints.at[node2, "JoinTag"]]
    gmsh.model.mesh.addElementsByType(surf, LINE, [elem], lst)
    return lst


class sap2000_handler:
    
    def __init__(self):
        self.s2kDatabase = {}  # SAP2000 S2K file database


    def get_table(self, tabletitle):
        tabletitle = ""
        try:
            return self.s2kDatabase[tabletitle]
        except KeyError as error:
            return None


    def read_s2k(self, filename: str) -> dict:
        """_summary_

        Args:
            filename (str): the name of the file to be read

        Returns:
            dict: a dictionary with the tables of the s2k file
        """
        logging.info("Reading file: %s", filename)
        
        s2k = {}
        f = open(filename, 'r')
        tabletitle = ""
        cont = False
        previous = ""
        for line in f:
            l = read_line(line, previous, cont)
            if l["type"] == "empty": 
                cont = False
                continue
            elif l["type"] == "cont": 
                cont = True
                previous = l["previous"]
                continue
            elif l["type"] == "table":
                cont = False
                tabletitle = l["title"]
                s2k[tabletitle] = []
                continue
            else:
                cont = False
                s2k[tabletitle].append(l["values"])
        f.close()
        
        for s in s2k:
            self.s2kDatabase[s.upper()] = pd.DataFrame(s2k[s])
            
        logging.info("End rreading file: %s", filename)
        return s2k


    def read_excel(self, filename: str, out: str = 'pandas'):
        """Reads a SAP2000 excel file

        Args:
            filename (str): the name of the file to be read
            out (str, optional): specifies if the return value is a pandas dataframe or a xl objecct. Defaults to 'pandas'.

        Returns:
            *varies*: the database of the SAP2000 excel file as a pandas dataframe or a xl object
        """

        logging.info("Reading file: %s", filename)

        s2k = pd.read_excel(filename, sheet_name=None, skiprows=lambda x: x in [0, 2])
        for df in s2k:
            self.s2kDatabase[df.upper()] = s2k[df]

        if out.lower() == 'openpyxl' or out.lower() == 'xl':
            xlsx = openpyxl.load_workbook(filename)
        else:
            xlsx = self.s2kDatabase
            
        logging.info("End reading file: %s", filename)
        return xlsx


    def write_msh(self, filename: str):
        """Writes a GMSH mesh file

        Args:
            filename (str): the name of the file to be written
        """


        joints = self.s2kDatabase['Joint Coordinates'.upper()]
        elems = self.s2kDatabase['Connectivity - Frame'.upper()]
        areas = self.s2kDatabase['Connectivity - Area'.upper()]
        try:
            mats = self.s2kDatabase['MatProp 01 - General'.upper()]
        except:
            mats = self.s2kDatabase['Material Properties 01 - General'.upper()]
        try:
            sect = self.s2kDatabase['Frame Props 01 - General'.upper()]
        except:
            sect = self.s2kDatabase['Frame Section Properties 01 - General'.upper()]
        sectassign = self.s2kDatabase['Frame Section Assignments'.upper()]
        
        try:
            title = self.s2kDatabase['PROJECT INFORMATION'].at['Project Name', 0]
        except:
            title = "filename"
            
        # prepares the GMSH model
        njoins = joints.shape[0]
        ijoins = np.arange(1, njoins+1)
        joints.insert(0, "JoinTag", ijoins, False)
        joints['Joint'] = joints['Joint'].map(str) 
        joints.set_index('Joint', inplace=True)
        joints['coord'] = joints.apply(lambda x: np.array([x['XorR'], x['Y'], x['Z']]),axis=1) 
        lst1 = joints['coord'].explode().to_list()
        
        nelems = elems.shape[0]
        ielems = np.arange(1, nelems+1)
        elemlist = []
        elemnodes = []
        elems.insert(0, "ElemTag", ielems, False)
        elems['Frame'] = elems['Frame'].map(str) 
        elems['JointI'] = elems['JointI'].map(str)
        elems['JointJ'] = elems['JointJ'].map(str)
        df_dict = elems.to_dict('records')
        elems.set_index('Frame', inplace=True)
        for row in df_dict:
            elemlist.append(row['ElemTag'])
            elemnodes.append(joints.at[row['JointI'], 'JoinTag'])
            elemnodes.append(joints.at[row['JointJ'], 'JoinTag'])

        nelems = areas.shape[0]
        iareas = np.arange(1, nelems+1)
        arealist = [[], []]
        areanodes = [[], []]
        areas.insert(0, "ElemTag", iareas, False)
        areas.insert(0, "ElemType", np.array(['QUAD' for _ in range(nelems)]), False)
        areas['Joint1'] = areas['Joint1'].map(str)
        areas['Joint2'] = areas['Joint2'].map(str)
        areas['Joint3'] = areas['Joint3'].map(str)
        areas['Joint4'] = areas['Joint4'].map(str)
        df_dict = areas.to_dict('records')
        areas.set_index('Area', inplace=False)
        for row in df_dict:
            if row['Joint4'] == 'nan':
                areas.at[row['Area'], 'ElemType'] = 'TRI'
                arealist[1].append(row['ElemTag'])
                areanodes[1].append(joints.at[row['Joint1'], 'JoinTag'])
                areanodes[1].append(joints.at[row['Joint2'], 'JoinTag'])
                areanodes[1].append(joints.at[row['Joint3'], 'JoinTag'])
            else:
                arealist[0].append(row['ElemTag'])
                areanodes[0].append(joints.at[row['Joint1'], 'JoinTag'])
                areanodes[0].append(joints.at[row['Joint2'], 'JoinTag'])
                areanodes[0].append(joints.at[row['Joint3'], 'JoinTag'])
                areanodes[0].append(joints.at[row['Joint4'], 'JoinTag'])

        # initialize gmsh
        gmsh.initialize(sys.argv)
        gmsh.model.add("title")
        
        line = gmsh.model.addDiscreteEntity(LINE)
        surf = gmsh.model.addDiscreteEntity(SURFACE)

        # We add 4 nodes and 2 3-node triangles (element type "2")
        gmsh.model.mesh.addNodes(LINE, line, ijoins, lst1)
        gmsh.model.mesh.addElementsByType(line, FRAME2, elemlist, elemnodes)
        gmsh.model.mesh.addElements(SURFACE, surf, [QUADRANGLE4, TRIANGLE3], arealist, areanodes)

        sect['SectionName'] = sect['SectionName'].map(str) 
        sect.set_index('SectionName', inplace=False)
        seclist = {}
        nsects = sect.shape[0]
        i = 0
        for sec in sect.iterrows():
            secname = sec[1]['SectionName'].upper()
            seclist[secname] = [++i, secname]

        sectaglist = [[] for _ in range(nsects)]
        
        sectassign['Frame'] = sectassign['Frame'].map(str) 
        df_dict = sectassign.to_dict('records')
        sectassign.set_index('Frame', inplace=False)
        for row in df_dict:
            # sec = row['AnalSect'].upper()
            # ielem = str(row['Frame'])
            newielem = elems.at[str(row['Frame']), 'ElemTag']
            sectaglist[seclist[row['AnalSect'].upper()][0]].append(newielem)

        for sec in seclist:
            gmsh.model.addPhysicalGroup(LINE, sectaglist[seclist[sec][0]], name=seclist[sec][1])
        # gmsh.model.addPhysicalGroup(LINE, [line], name="Material1")
        # gmsh.model.addPhysicalGroup(SURFACE, [surf], name="Material2")

        gmsh.option.setNumber("Mesh.SaveAll", 1)
        gmsh.write("title.msh")

        # Launch the GUI to see the results:
        if '-nopopup' not in sys.argv:
            gmsh.fltk.run()

        gmsh.finalize()

        return


    def write_msh_2(self, filename: str):
        """Writes a GMSH mesh file

        Args:
            filename (str): the name of the file to be written
        """

        # initialize gmsh
        gmsh.initialize(sys.argv)
        
        try:
            title = self.s2kDatabase['PROJECT INFORMATION'].at['Project Name', 0]
        except:
            title = pathlib.Path(filename).stem
        gmsh.model.add(title)
        
        joints = self.s2kDatabase['Joint Coordinates'.upper()]
        elems = self.s2kDatabase['Connectivity - Frame'.upper()]
        areas = self.s2kDatabase['Connectivity - Area'.upper()]
        try:
            sect = self.s2kDatabase['Frame Props 01 - General'.upper()]
        except:
            sect = self.s2kDatabase['Frame Section Properties 01 - General'.upper()]
        sectassign = self.s2kDatabase['Frame Section Assignments'.upper()]
        areasect = self.s2kDatabase['Area Section Properties'.upper()]
        areaassign = self.s2kDatabase['Area Section Assignments'.upper()]
        groups = self.s2kDatabase['Groups 1 - Definitions'.upper()]
        groupsassign = self.s2kDatabase['Groups 2 - Assignments'.upper()]
        

        logging.basicConfig(level=logging.DEBUG)
        logging.info("Writing GMSH file: %s", filename)
            
        # prepares the GMSH model
        njoins = joints.shape[0]
        logging.info(f"Processing nodes ({njoins})...")
        ijoins = np.arange(1, njoins+1)
        joints.insert(0, "JoinTag", ijoins, False)
        joints['Joint'] = joints['Joint'].map(str)
        joints['Joint2'] = joints.loc[:, 'Joint']
        joints.set_index('Joint', inplace=True)
        joints['coord'] = joints.apply(lambda x: np.array([x['XorR'], x['Y'], x['Z']]),axis=1) 
        lst1 = joints['coord'].explode().to_list()


        line = gmsh.model.addDiscreteEntity(POINT)
        gmsh.model.mesh.addNodes(POINT, line, ijoins, lst1)

        nelems = elems.shape[0]
        logging.info(f"Processing frames ({nelems})...")
        elems.insert(1, "ElemTag", np.arange(1, nelems+1), False)
        elems.insert(2, "Section", sectassign['AnalSect'].values, False)
        elems[['Frame', 'JointI', 'JointJ']] = elems[['Frame', 'JointI', 'JointJ']].astype(str)
        
        elems['Nodes'] = elems.apply(
            lambda row: rename_elem_nodes(joints, row['ElemTag'], row["JointI"],row["JointJ"]), 
            axis=1
            )

        starttime = timeit.default_timer()

        nelems = areas.shape[0]
        logging.info(f"Processing ares ({nelems})...")
        areas.insert(1, "ElemTag", np.arange(1, nelems+1), False)
        areas.insert(2, "Section", areaassign['Section'].values, False)
        areas[['Area','Joint1','Joint2','Joint3','Joint4']] = areas[['Area','Joint1','Joint2','Joint3','Joint4']].astype(str)
        areas['Node1'] = joints.loc[areas['Joint1'].values, 'JoinTag'].values
        areas['Node2'] = joints.loc[areas['Joint2'].values, 'JoinTag'].values
        areas['Node3'] = joints.loc[areas['Joint3'].values, 'JoinTag'].values
        areas['Node4'] = areas.apply(lambda row: 'nan' if row['Joint4'] == 'nan' else joints.at[row['Joint4'], 'JoinTag'], axis=1)
        areas['Nodes'] = areas.apply(lambda x:[x['Node1'], x['Node2'], x['Node3']] 
                if x['Joint4'] == 'nan' else [x['Node1'], x['Node2'], x['Node3'], x['Node4']], axis=1)

        #areas['Nodes'] = areas[["Node1", "Node2", "Node3"]].values.tolist()
        #areas['Nodes'] = areas.loc[areas['Joint4'] == 'nan', ["Node1", "Node2", "Node3"]].values.tolist()
        #areas['Nodes'] = areas.apply(lambda x: np.array([joints.at[x['Joint1'], "JoinTag"], x['Joint2'], x['Joint3']]),axis=1) 
        areas.apply(
            lambda x: rename_area_nodes(x['ElemTag'],x["Nodes"]), 
            axis=1
            )

        logging.debug(f"Execution time: {round((timeit.default_timer() - starttime)*1000,3)} ms")
        logging.debug("Processing groups...")

        for row in groups.itertuples():
            group = getattr(row, 'GroupName')
            lst = groupsassign.loc[(groupsassign['ObjectType']=='Frame') & (groupsassign['GroupName']==group)]['ObjectLabel'].values
            if len(lst) > 0:
                lst2 = elems[elems['Frame'].isin(lst)]['ElemTag'].values
                gmsh.model.addPhysicalGroup(LINE, lst2, name="Group: " + group)            
            
            lst = groupsassign.loc[(groupsassign['ObjectType']=='Area') & (groupsassign['GroupName']==group)]['ObjectLabel'].values
            if len(lst) > 0:
                lst2 = areas[areas['Area'].isin(lst)]['ElemTag'].values
                gmsh.model.addPhysicalGroup(SURFACE, lst2, name="Group: " + group)

        logging.debug("Processing frame sections...")

        for row in sect.itertuples():
            sec = getattr(row, 'SectionName')
            lst = elems.loc[elems['Section']==sec]['ElemTag'].values
            gmsh.model.addPhysicalGroup(LINE, lst, name="Frame section: " + sec)

        logging.debug("Processing area sections...")

        for row in areasect.itertuples():
            sec = getattr(row, 'Section')
            lst = areas.loc[areas['Section']==sec]['ElemTag'].values
            gmsh.model.addPhysicalGroup(SURFACE, lst, name="Area section: " + sec)

        logging.debug("Processing GMSH intialization...")

        gmsh.option.setNumber("Mesh.SaveAll", 1)
        gmsh.option.setNumber("Mesh.Lines", 1)
        gmsh.option.setNumber("Mesh.SurfaceFaces", 1)
        gmsh.option.setNumber("Mesh.LineWidth", 5)
        gmsh.option.setNumber("Mesh.ColorCarousel", 2)

        size = gmsh.model.getBoundingBox(-1, -1)
        gmsh.write("title.msh")

        # Launch the GUI to see the results:
        if '-nopopup' not in sys.argv:
            gmsh.fltk.run()

        gmsh.finalize()

        return
