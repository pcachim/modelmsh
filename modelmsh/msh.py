import meshio
import gmsh
import openpyxl
import numpy as np
import pandas as pd
import pathlib
import sys
import logging
import timeit
from . import femixlib


class msh_handler:
    def __init__(self):
        if not gmsh.isInitialized():
            gmsh.initialize()


    def import_s3dx(self, filename: str):
        """Import a .s3dx file and write a .msh file

        Args:
            filename (str): the .s3dx file to be imported

        Raises:
            Exception: wrong file extension
        """

        path = pathlib.Path(filename)
        if path.suffix.lower() != ".s3dx":
            raise Exception("File extension is not .s3dx")
        self._filename = str(path.parent / path.stem)

        with open(filename, 'r') as f:
            title = f.readline()

            while True:
                try:
                    title = f.readline()
                    if title.strip() == "": break
                except:
                    break

                nelems, nnodes, nspec = f.readline().strip().split()

                elems = []
                types = []
                lnode = []
                ndims = []
                for i in range(int(nelems)):
                    lin = f.readline().strip().split()
                    # n, ty, nn, ln = f.readline().strip().split()
                    n  = int(lin[0])
                    ty = int(lin[1])
                    nn = int(lin[2])
                    ln = lin[-nn:]
                    code, ndim, ln = femix2gmsh(ty, nn, ln)
                    if code not in types:
                        types.append(code)
                        elems.append([n])
                        lnode.append(ln)
                        ndims.append(int(ndim))
                    else:
                        index = types.index(code)
                        lnode[index].extend(ln)
                        elems[index].append(n)

                nodes = []
                coord = []
                for i in range(int(nnodes)):
                    lin = f.readline().strip().split()
                    nodes.append(int(lin[0]))
                    coord.extend([float(lin[1]), float(lin[2]), float(lin[3])])

                specs = []
                for i in range(int(nspec)):
                    lin = f.readline().strip().split()
                    specs.append(int(lin[1]))

        gmsh.model.add(title)
        for i in range(len(elems)):
            tag = gmsh.model.addDiscreteEntity(ndims[i], -1)
            gmsh.model.mesh.addNodes(ndims[i], tag, nodes, coord)
            gmsh.model.mesh.addElements(ndims[i], tag, [types[i]], [elems[i]], [lnode[i]])

        gmsh.write(self._filename + ".msh")
        return



    def addNodeData ():
        # "ElementNodeData":
        t1 = gmsh.view.add("Continuous")
        for step in range(0, 10):
            gmsh.view.addHomogeneousModelData(
                t1, step, "simple model", "NodeData",
                [1, 2, 3, 4],  # tags of nodes
                [10., 10., 12. + step, 13. + step])  # data, per node
        return


    def addElementNodeData ():
        # "ElementNodeData":
        t2 = gmsh.view.add("Discontinuous")
        for step in range(0, 10):
            gmsh.view.addHomogeneousModelData(
                t2, step, "simple model", "ElementNodeData",
                [1, 2],  # tags of elements
                [10., 10., 12. + step, 14., 15., 13. + step])  # data per element nodes
        return


    def addElementData ():
        # "ElementNodeData":
        t2 = gmsh.view.add("Discontinuous")
        for step in range(0, 10):
            gmsh.view.addHomogeneousModelData(
                t2, step, "simple model", "ElementData",
                [1, 2],  # tags of elements
                [10., 12. + step])  # data per element nodes
        return


    def finalize(self):
        if gmsh.isInitialized():
            gmsh.finalize()
        return


