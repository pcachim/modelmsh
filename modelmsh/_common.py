
meshio_gmsh = {
    "line": 1,
    "triangle": 2,
    "quad": 3,
    "tetra": 4,
    "hexahedron": 5,
    "wedge": 6,
    "pyramid": 7,
    "line3": 8,
    "triangle6": 9,
    "quad9": 10,
    "tetra10": 11,
    "hexahedron27": 12,
    "wedge18": 13,
    "pyramid14": 14,
    "vertex": 15,
    "quad8": 16,
    "hexahedron20": 17,
    "triangle10": 18
}
gmsh_meshio = {v: k for k, v in meshio_gmsh.items()}

meshio_femix = {
    "line": (7, 2, 1, 1, 2, 1, 2),
    "triangle": (9, 3, 1, 3, 3, 3, 3),
    "quad": (9, 4, 1, 1, 2, 1, 2),
    "tetra": (4, 4, 0, 1, 2, 1, 2),
    "hexahedron": (4, 8, 0, 1, 2, 1, 2),
    "wedge": (4, 6, 0, 1, 2, 1, 2),
    "pyramid": (4, 5, 0, 1, 2, 1, 2),
    "line3": (14, 3, 1, 1, 2, 1, 2),
    "triangle6": (9, 6, 1, 3, 3, 3, 3),
    "quad9": (9, 9, 1, 1, 2, 1, 2),
    "tetra10": (4, 10, 0, 1, 2, 1, 2),
    "hexahedron27": (4, 27, 0, 1, 2, 1, 2),
    "wedge18": (4, 18, 0, 1, 2, 1, 2),
    "pyramid14": (4, 14, 0, 1, 2, 1, 2),
    "vertex": (0, 1, 0, 0, 0, 0, 0),
    "quad8": (9, 8, 1, 1, 2, 1, 2),
    "hexahedron20": (4, 20, 0, 1, 2, 1, 2),
    "triangle10": (9, 10, 1, 3, 3, 3, 3)
}

meshio_sections = {
    "line": 1,
    "triangle": 2,
    "quad": 2,
    "tetra": 3,
    "hexahedron": 3,
    "wedge": 3,
    "pyramid": 3,
    "line3": 1,
    "triangle6": 2,
    "quad9": 2,
    "tetra10": 3,
    "hexahedron27": 3,
    "wedge18": 3,
    "pyramid14": 3,
    "vertex": 0,
    "quad8": 2,
    "hexahedron20": 3,
    "triangle10": 2
}

sections_meshio = {
    0: "point",
    1: "curve",
    2: "area",
    3: "volume",
}

sections = {
    "point": {"material": 'spring'},
    "curve": {"area": 0.001, "torsion": 0.00001, "inertia2": 0.0001, "inertia3": 0.00001, "angle": 0.0, "material": 'steel'},
    "area": {"thick": 0.25, "material": 'concrete'},
    "volume": {"material": 'concrete'}
}

materials = {
    'point': {
        "young": 200000000.0,
        "poisson": 0.2,
        "weight": 77.0,
        "thermal": 1.0e-6},
    'curve': {
        "young": 200000000.0,
        "poisson": 0.2,
        "weight": 77.0,
        "thermal": 1.0e-6,
        "shear": 8000000.0,
        "mass": 7850.0,
        "damping": 0.02,
        "design": "steel"},
    'area': {
        "young": 30000000.0,
        "poisson": 0.2,
        "weight": 25.0,
        "thermal": 1.0e-6,
        "shear": 8000000.0,
        "mass": 2500.0,
        "damping": 0.05,
        "design": "concrete"},
    'volume': {
        "young": 30000000.0,
        "poisson": 0.2,
        "weight": 25.0,
        "thermal": 1.0e-6,
        "shear": 8000000.0,
        "mass": 2500.0,
        "damping": 0.05,
        "design": "concrete"},
    'interface': {
        "stift": 1.0e6,
        "stifn": 1.0e10},
    'soil': {
        "subre": 1.0e6},
    'spring': {
        "stift": 1.0e6,
        "stifn": 1.0}
}
