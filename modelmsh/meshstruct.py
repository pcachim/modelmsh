"""_summary_line = "This modules generates and calculates simple structures with simple geometries" # for summary file
"""

import sys
import gmsh
import numpy as np
import pathlib
#import eurocodepy as ec
from . import ofemlib
from ._common import *

RECTANGULAR = 1
TRIANGULAR = 2
CIRCULAR = 3
CIRCULAR_QUARTER = 4
CIRCULAR_WITH_HOLE = 5
CIRCULAR_SEGMENT = 6
POLYGON = 7

FREE = -1
HINGED = 0
FIXED = 1


def rot(point1: tuple, point2: tuple, angle: float) -> tuple:
    """Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    """
    ox, oy, _ = point1
    px, py = point2
    qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
    qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)
    return qx, qy


def Circle(center: tuple, radius: float, msize: float = 0.3):
    gmsh.model.add("slab")
    pt1 = gmsh.model.geo.addPoint(center[0], center[1], center[2], msize)
    pt2 = gmsh.model.geo.addPoint(center[0]+radius, center[1], center[2], msize)
    pt3 = gmsh.model.geo.addPoint(center[0]-radius, center[1], center[2], msize)
    sf1 = gmsh.model.geo.addCircleArc(pt2, pt1, pt3)
    sf2 = gmsh.model.geo.addCircleArc(pt3, pt1, pt2)
    circle = gmsh.model.geo.addCurveLoop([sf1, sf2],)
    area = gmsh.model.geo.addPlaneSurface([circle])
    gmsh.model.geo.synchronize()
    # gmsh.option.setNumber("Mesh.ElementOrder", 2)
    # gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
    gmsh.model.mesh.generate(2)


def CircleWithHole(center: tuple, radius: float, angle: float, msize: float = 0.3):
    pass


def CircleSegment(center: tuple, radius: float, startangle: float, endangle: float, msize: float = 0.3):
    gmsh.model.add("slab")
    angle = endangle - startangle
    pt1 = gmsh.model.geo.addPoint(center[0], center[1], center[2], msize)
    pn2 = rot(center, (center[0]+radius, center[1]), startangle)
    pt2 = gmsh.model.geo.addPoint(pn2[0], pn2[1], center[2], msize)
    pn3 = rot(center, (center[0]+radius, center[1]), endangle)
    pt3 = gmsh.model.geo.addPoint(pn3[0], pn3[1], center[2], msize)
    sf1 = gmsh.model.geo.addCircleArc(pt2, pt1, pt3)
    sf2 = gmsh.model.geo.addLine(pt3, pt1)
    sf3 = gmsh.model.geo.addLine(pt1, pt2)
    circle = gmsh.model.geo.addCurveLoop([sf1, sf2, sf3],)
    area = gmsh.model.geo.addPlaneSurface([circle])
    gmsh.model.geo.synchronize()
    # gmsh.option.setNumber("Mesh.ElementOrder", 2)
    # gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
    gmsh.model.mesh.generate(2)
    return area


def CirleQuarter(center: tuple, radius: float, angle: float, msize: float = 0.3):
    gmsh.model.add("slab")
    pt1 = gmsh.model.geo.addPoint(center[0], center[1], center[2], msize)
    pn2 = rot(center, (center[0]+radius, center[1]), angle)
    pt2 = gmsh.model.geo.addPoint(pn2[0], pn2[1], center[2], msize)
    pn3 = rot(center, (center[0], center[1]+radius), angle)
    pt3 = gmsh.model.geo.addPoint(pn3[0], pn3[1], center[2], msize)
    sf1 = gmsh.model.geo.addCircleArc(pt2, pt1, pt3)
    sf2 = gmsh.model.geo.addLine(pt3, pt1)
    sf3 = gmsh.model.geo.addLine(pt1, pt2)
    circle = gmsh.model.geo.addCurveLoop([sf1, sf2, sf3],)
    area = gmsh.model.geo.addPlaneSurface([circle])
    gmsh.model.geo.synchronize()
# To generate a curvilinear mesh and optimize it to produce provably valid
# curved elements (see A. Johnen, J.-F. Remacle and C. Geuzaine. Geometric
# validity of curvilinear finite elements. Journal of Computational Physics
# 233, pp. 359-372, 2013; and T. Toulorge, C. Geuzaine, J.-F. Remacle,
# J. Lambrechts. Robust untangling of curvilinear meshes. Journal of
# Computational Physics 254, pp. 8-26, 2013), you can uncomment the following
# lines:
#
# gmsh.option.setNumber("Mesh.ElementOrder", 2)
# gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
    gmsh.model.mesh.generate(2)
    return area


def Rectangle(bleft: tuple, width: float, height: float, angle: float, msize: float = 0.3):
    gmsh.model.add("slab")
    pt1 = gmsh.model.geo.addPoint(bleft[0]      , bleft[1]       , bleft[2], msize)
    pn2 = rot(bleft, (bleft[0]+width, bleft[1]), angle)
    pt2 = gmsh.model.geo.addPoint(pn2[0], pn2[1], bleft[2], msize)
    pn3 = rot(bleft, (bleft[0]+width, bleft[1]+height), angle)
    pt3 = gmsh.model.geo.addPoint(pn3[0], pn3[1], bleft[2], msize)
    pn4 = rot(bleft, (bleft[0], bleft[1]+height), angle)
    pt4 = gmsh.model.geo.addPoint(pn4[0], pn4[1], bleft[2], msize)
    sf1 = gmsh.model.geo.addLine(pt1, pt2)
    sf2 = gmsh.model.geo.addLine(pt2, pt3)
    sf3 = gmsh.model.geo.addLine(pt3, pt4)
    sf4 = gmsh.model.geo.addLine(pt4, pt1)
    circle = gmsh.model.geo.addCurveLoop([sf1, sf2, sf3, sf4],)
    area = gmsh.model.geo.addPlaneSurface([circle])
    gmsh.model.geo.synchronize()
    # gmsh.option.setNumber("Mesh.ElementOrder", 2)
    # gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
    gmsh.model.mesh.generate(2)
    return area


def Triangle(point1: tuple, point2: tuple, point3: tuple, angle: float, msize: float = 0.3):
    pt1 = gmsh.model.geo.addPoint(point1[0], point1[1], point1[2], msize)
    pn2 = rot(point1, point2, angle)
    pt2 = gmsh.model.geo.addPoint(pn2[0], pn2[1], point2[2], msize)
    pn2 = rot(point1, point3, angle)
    pt3 = gmsh.model.geo.addPoint(pn2[0], pn2[1], point3[2], msize)
    sf1 = gmsh.model.geo.addLine(pt1, pt2)
    sf2 = gmsh.model.geo.addLine(pt2, pt3)
    sf3 = gmsh.model.geo.addLine(pt3, pt1)
    circle = gmsh.model.geo.addCurveLoop([sf1, sf2, sf3])
    area = gmsh.model.geo.addPlaneSurface([circle])
    gmsh.model.geo.synchronize()
    # gmsh.option.setNumber("Mesh.ElementOrder", 2)
    # gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
    gmsh.model.mesh.generate(2)
    return area


def Polygon(points: tuple, msize: float = 0.3):
    pt = []
    ln = []
    for i in range(len(points)):
        k = gmsh.model.geo.addPoint(points[i][0], points[i][1], points[i][2], msize)
        pt.append(k)
    pt.append(pt[0])
    for i in range(len(points)):
        k = gmsh.model.geo.addLine(pt[i], pt[i+1])
        ln.append(k)
    poly = gmsh.model.geo.addCurveLoop(ln)
    area = gmsh.model.geo.addPlaneSurface([poly])
    gmsh.model.geo.synchronize()
    # gmsh.option.setNumber("Mesh.ElementOrder", 2)
    # gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
    gmsh.model.mesh.generate(2)
    return area

class Slab:
    
    def __init__(self) -> None:
        if not gmsh.is_initialized():
            gmsh.initialize()
        return
    
    def addGeometry(self, geometry: int, *args, **kwargs):
        """_summary_

        Args:
            geometry (int): _description_

        Raises:
            ValueError: _description_
        """
        gmsh.model.add("slab")
        if geometry == RECTANGULAR:
            msize = 0.3 if len(args) < 5 else args[4]
            Rectangle(args[0], args[1], args[2], args[3], msize)
        elif geometry == TRIANGULAR:
            msize = 0.3 if len(args) < 5 else args[4]
            Triangle(args[0], args[1], args[2], args[3], msize)
        elif geometry == CIRCULAR:
            msize = 0.3 if len(args) < 3 else args[2]
            Circle(args[0], args[1], msize)
        elif geometry == CIRCULAR_QUARTER:
            msize = 0.3 if len(args) < 4 else args[3]
            CirleQuarter(args[0], args[1], args[2], msize)
        elif geometry == CIRCULAR_WITH_HOLE:
            pass
        elif geometry == CIRCULAR_SEGMENT:
            msize = 0.3 if len(args) < 5 else args[4]
            CircleSegment(args[0], args[1], args[2], args[3], msize)
        elif geometry == POLYGON:
            msize = 0.3 if len(args) < 2 else args[1]
            Polygon(args[0], msize)
        else:
            raise ValueError("Invalid geometry type.")
        
        if len(kwargs) > 0:
            self.addParameters(**kwargs)
        return
    
    def addParameters(self, **kwargs):
        self.fixno = {}
        if "boundary" in kwargs:
            bounddary_condition = kwargs["boundary"]
            # if len(bounddary_condition) != len (bounds):
            #     raise ValueError("Invalid boundary conditions.")
            for i, b in enumerate(bounddary_condition):
                bounds, _, _ = gmsh.model.mesh.getNodes(1, i+1, includeBoundary=True)
                if b == FREE:
                    pass
                elif b == FIXED or b == HINGED:
                    for inode in bounds:
                        self.fixno[inode] = b if inode not in self.fixno else max(b, self.fixno[inode])
                else:
                    raise ValueError("Invalid boundary conditions.")
        
        if "material" in kwargs:
            self.material = kwargs["material"]
        
        if "thick" in kwargs:
            self.thick = kwargs["thick"]
        
        if "load" in kwargs:
            self.load = float(kwargs["load"])

        return
    
    def to_gldat(self, mesh_file: str):
        """Writes a femix .gldat mesh file

        Args:
            mesh_file (str): the name of the file to be written
        """
        ndime = 3
        
        path = pathlib.Path(mesh_file)
        if path.suffix.lower() != ".gldat":
            mesh_file = path.with_suffix('').resolve() + ".gldat"

        nodeTags, nodeCoords, _ = gmsh.model.mesh.getNodes(2, includeBoundary=True)
        coordlist = dict(zip(nodeTags, np.arange(len(nodeTags))))
        # coords = np.array(nodeCoords).reshape(-1, 3)
        # sorted_dict_by_keys = {key: coordlist[key] for key in sorted(coordlist)}
        eleTypes, eleTags, eleNodes = gmsh.model.mesh.getElements(2)
        elemlist = dict(zip(np.arange(1, 1+len(eleTags[0])), eleTags[0]))
        self.nelems = len(eleTags[0])
        self.npoints = len(nodeTags)
        self.nmats = 1
        self.nsections = 1
        self.nspecnodes = len(self.fixno)
        ndime = 3
        props = meshio_femix[gmsh_meshio[eleTypes[0]]]
        ntype = props[0]
        nnode = props[1]

        with open(mesh_file, 'w') as file:

            file.write("### Main title of the problem\n")
            file.write("Slab mesh\n")

            file.write("\n")
            file.write("### Main parameters\n")
            file.write("%5d # nelem (n. of elements in the mesh)\n" % self.nelems)
            file.write("%5d # npoin (n. of points in the mesh)\n" % self.npoints)
            file.write("%5d # nvfix (n. of points with fixed degrees of freedom)\n" % self.nspecnodes)
            file.write("%5d # ncase (n. of load cases)\n" % 1)
            file.write("%5d # nselp (n. of sets of element parameters)\n" % 1)
            file.write("%5d # nmats (n. of sets of material properties)\n" % 1)
            file.write("%5d # nspen (n. of sets of element nodal properties)\n" % 1)
            file.write("%5d # nmdim (n. of geometric dimensions)\n" % 2)
            file.write("%5d # nnscs (n. of nodes with specified coordinate systems)\n" % 0)
            file.write("%5d # nsscs (n. of sets of specified coordinate systems)\n" % 0)
            file.write("%5d # nncod (n. of nodes with constrained d.o.f.)\n" % 0)
            file.write("%5d # nnecc (n. of nodes with eccentric connections)\n" % 0)

            file.write("\n")
            file.write("### Sets of element parameters\n")
            file.write("# iselp\n")
            file.write(" %6d\n" % 1)
            file.write("# element parameters\n")
            file.write("%5d # ntype (n. of element type)\n" % 5)
            file.write("%5d # nnode (n. of nodes per element)\n" % props[1])
            file.write("%5d # ngauq (n. of Gaussian quadrature) (stiffness)\n" % props[3])
            file.write("%5d # ngaus (n. of Gauss points in the formulation) (stiffness)\n" % props[4])
            file.write("%5d # ngstq (n. of Gaussian quadrature) (stresses)\n" % props[5])
            file.write("%5d # ngstr (n. of Gauss points in the formulation) (stresses)\n" % props[6])

            file.write("\n")
            file.write("### Sets of material properties\n")
            file.write("### (Young modulus, Poisson ratio, mass/volume and thermic coeff.\n")
            file.write("# imats         young        poiss        dense        alpha\n")
            file.write("  %5d  %16.3f %16.3f %16.3f %16.3f\n" % (1,
                self.material['E'],self.material['nu'],self.material['rho'],self.material['alpha']))

            file.write("\n")
            file.write("### Sets of element nodal properties\n")
            file.write("# ispen\n")
            file.write(" %6d\n" % 1)
            file.write("# inode       thick\n")
            for inode in range(1, nnode+1):
                file.write(" %6d     %15.3f\n" % (inode, self.thick))

            file.write("\n")
            file.write("### Element parameter index, material properties index, element nodal\n")
            file.write("### properties index and list of the nodes of each element\n")
            file.write("# ielem ielps matno ielnp       lnods ...\n")
            count = 0
            for i, elem in enumerate(eleTags[0]):
                file.write(" %6d %5d %5d %5d    " % (i+1, 1, 1, 1))
                for inode in range(nnode):
                    file.write(" %8d" % eleNodes[0][count])
                    count += 1
                file.write("\n")

            file.write("\n")
            file.write("### Coordinates of the points\n")
            file.write("# ipoin            coord-x            coord-y            coord-z\n")
            icount = 1
            for i, ipoin in enumerate(nodeTags):
                node = coordlist[i+1]
                count = int(3*node)
                file.write(" %6d    %16.8lf   %16.8lf\n" % (i+1, nodeCoords[count], nodeCoords[count+1]))
                icount += 1

            file.write("\n")
            file.write("### Points with fixed degrees of freedom and fixity codes (1-fixed0-free)\n")
            file.write("# ivfix  nofix       ifpre ...\n")
            count = 1
            for i, fix in self.fixno.items():
                sup = " 1  1  1" if fix==FIXED else " 1  0  0"
                file.write(" %6d %6d      %s\n" % (count, i, sup))
                count += 1

            file.write("\n")
            file.write("# ===================================================================\n")

            file.write("\n")
            file.write("### Load case n. %8d\n" % 1)

            file.write("\n")
            file.write("### Title of the load case\n")
            file.write("Uniform distributed load\n")

            file.write("\n")
            file.write("### Load parameters\n")
            file.write("%5d # nplod (n. of point loads in nodal points)\n" % 0)
            file.write("%5d # ngrav (gravity load flag: 1-yes0-no)\n" % 0)
            file.write("%5d # nedge (n. of edge loads) (F.E.M. only)\n" % 0)
            file.write("%5d # nface (n. of face loads) (F.E.M. only)\n" % self.nelems)
            file.write("%5d # ntemp (n. of points with temperature variation) (F.E.M. only)\n" % 0)
            file.write("%5d # nudis (n. of uniformly distributed loads " % 0)
            file.write("(3d frames and trusses only)\n")
            file.write("%5d # nepoi (n. of element point loads) (3d frames and trusses only)\n" % 0)
            file.write("%5d # nprva (n. of prescribed and non zero degrees of freedom)\n" % 0)

            file.write("\n")
            file.write("### Face load (loaded element, loaded points and load value)\n")
            file.write("### (local coordinate system)\n")
            count = 0
            for i, elem in enumerate(eleTags[0]):
                file.write("# iface  loelf\n")
                file.write(" %5d %5d\n" % (i+1, i+1))
                file.write("# lopof       prfac-n   prfac-mb   prfac-mt\n")
                for j in range(nnode):
                    inode = eleNodes[0][count]
                    file.write(" %5d %16.3f %16.3f %16.3f\n" % (inode, self.load, 0.0, 0.0))
                    count += 1

            file.write("\n")
            file.write("END_OF_FILE\n")

        jobname = str(path.parent / path.stem)
        ofemlib.ofemSolver(jobname)

        # for i in range(1, 4):
        #     options = {'code': ofemlib.DI_PVA, 'csryn': 'n', 'ksres': 2, 'kdisp': i}
        #     ofemlib.ofemPostprocess(jobname, **options)
        #     df = ofemlib.ofemReadPVA(jobname + 'd_di.pva')
            
        #     t1 = gmsh.view.add("disp-" + str(i))
        #     gmsh.view.addHomogeneousModelData(
        #             t1, 0, "slab", "NodeData", df["point"].values, df['values'].values) 

        options = {'code': ofemlib.DI_CSV, 'csryn': 'n', 'ksres': 2}
        ofemlib.ofemPostprocess(jobname, **options)
        df = ofemlib.ofemReadCSV(jobname + '_di.csv')
            
        for i in range(1, 4):
            t1 = gmsh.view.add("disp-" + str(i))
            gmsh.view.addHomogeneousModelData(
                    t1, 0, "slab", "NodeData", df["point"].values, df['disp-'+str(i)].values) 

        options = {'code': ofemlib.AST_CSV, 'csryn': 'n', 'ksres': 2, 'stnod': 'a'}
        ofemlib.ofemPostprocess(jobname, **options)
        df = ofemlib.ofemReadCSV(jobname + '_avgst.csv')

        for i in range(1, 6):
            t1 = gmsh.view.add("str_avg-" + str(i))
            gmsh.view.addHomogeneousModelData(
                    t1, 0, "slab", "NodeData", df['point'].values, df['str-'+str(i)].values) 

        options = {'code': ofemlib.EST_CSV, 'csryn': 'n', 'ksres': 2, 'stnod': 'e', 'kstre': i}
        ofemlib.ofemPostprocess(jobname, **options)
        df = ofemlib.ofemReadCSV(jobname + '_elnst.csv')
        unique_values = [elemlist.get(item, item) for item in df["element"].unique().tolist()]
    
        for i in range(1, 6):
            t1 = gmsh.view.add("str_eln-" + str(i))
            gmsh.view.addHomogeneousModelData(
                    t1, 0, "slab", "ElementNodeData", unique_values, df['str-'+str(i)].values) 

        return

    def run(self):
        # Launch the GUI to see the results:
        if '-nopopup' not in sys.argv:
            gmsh.fltk.run()

        gmsh.finalize()

    
class Beam:
    pass

