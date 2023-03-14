"""
Define the C-variables and functions from the C-files that are needed in Python
"""
from ctypes import c_double, c_int, CDLL
import os

 
ME_S3D =  1 # /*    1) _me.s3d file with the undeformed mesh                       */
GE_S3D =  2 # /*    2) _ge.s3d file with the geometric data                        */
GL_LPT =  3 # /*    3) _gl.lpt file with the geometry and loads                    */
RS_LPT =  4 # /*    4) _rs.lpt file with the results                               */
DM_S3D =  5 # /*    5) _dm.s3d file with the deformed mesh                         */
DI_PVA =  6 # /*    6) _di.pva file with the nodal displacements                   */
PS_S3D =  7 # /*    7) _ps.s3d file with the principal stresses                    */
ST_PVA =  8 # /*    8) _st.pva file with the nodal stresses                        */
SG_S3D =  9 # /*    9) _sg.s3d file with the stress graphics                       */
SR_PVA = 10 # /*   10) _sr.pva file with the nodal reinforcement.                  */
RG_S3D = 11 # /*   11) _rg.s3d file with the reinforcement graphics.               */
RS_CSV = 12 # /*   12) _rs.csv file with the results.                              */
ME_S3DX = 13 # /*  13) _me.s3dx file with the results.                              */

BOTO_XX = 1
BOTO_YY = 2
BOTO_XXENV = 3
BOTO_YYENV = 4

MEBE_MEMBRRANE = 1
MEBE_BENDING = 2

SRES_RESULTANT = 1
SRES_STRESSES = 2

SURF_BOTTOM = 1
SURF_MIDDLE = 2
SURF_TOP = 3


#lib_path = os.path.join(os.getcwd(), 'build/src/libfemixpy.dylib')
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libfemixpy.dylib')
try:
    libfemixpy = CDLL(lib_path)
except:
    print("Cannot load library 'libfemixpy'")
    exit()

prefemixlib = libfemixpy.prefemixlib
prefemixlib.restype = int
femixlib = libfemixpy.femixlib
femixlib.restype = int
posfemixlib = libfemixpy.posfemixlib
posfemixlib.restype = int


def prefemix2(filename: str):
    """_summary_

    Args:
        filename (str): the name of the file to be read

    Returns:
        error code: 0 if no error, 1 if error
    """""""""
    n = prefemixlib(filename.encode())
    return n


def femix2(filename: str, soalg: str='d', randsn: float=1.0e-6):
    """_summary_

    Args:
        filename (str): the name of the file to be read

    Returns:
        error code: 0 if no error, 1 if error
    """""""""
    n = femixlib(filename.encode(), soalg.encode(), c_double(randsn))
    return n


def posfemix2(filename: str, code: int=1, lcaco: str='l', cstyn: str='y', 
                            stnod: str='a', csryn: str='n', ksres=1):
    """_summary_

    Args:
        filename (str): the name of the file to be read

    Returns:
        error code: 0 if no error, 1 if error
    """""""""

    if ksres not in [1, 2]:
        ksres = 1
        print("\n'ksres' must be 1 or 2. 'ksres' changed to 1")

    lcaco = lcaco.lower()
    if lcaco not in ['l', 'c']:
        lcaco = 'l'
        print("\n'lcaco' must be 'l'oad case or 'c'ombination. 'lcaco' changed to 'l")
    
    stnod = stnod.lower()
    if stnod not in ['a', 'e']:
        stnod = 'a'
        print("\n'stnod' must be 'a'veraged or 'e'element. 'stnod' changed to 'a")

    csryn = csryn.lower()
    if csryn not in ['y', 'n']:
        csryn = 'n'
        print("\n'csryn' must be 'y'es or 'n'o. 'csryn' changed to 'n")

    cstyn = cstyn.lower()
    if cstyn not in ['y', 'n']:
        cstyn = 'n'
        print("\n'cstyn' must be 'y'es or 'n'o. 'cstyn' changed to 'y")

    n = posfemixlib(filename.encode(), c_int(code), 
                    lcaco.encode(), cstyn.encode(), stnod.encode(), csryn.encode())
    return n


def femPostprocess(filename: str, **kwargs):
    """_summary_

    Args:
        filename (str): the name of the file to be read

    Returns:
        error code: 0 if no error, 1 if error
    """""""""

    if 'code' not in kwargs:
        code = RS_LPT
    else:
        code = kwargs['code']
    
    if 'lcaco' not in kwargs:
        lcaco = 'l'
    else:
        lcaco = kwargs['lcaco'].lower()
        if lcaco not in ['l', 'c']: 
            lcaco = 'l'
            print("\n'lcaco' must be 'l'oad case or 'c'ombination. 'lcaco' changed to 'l")

    if 'cstyn' not in kwargs:
        cstyn = 'y'
    else:
        cstyn = kwargs['cstyn'].lower()
        if cstyn not in ['y', 'n']: 
            cstyn = 'n'
            print("\n'cstyn' must be 'y'es or 'n'o. 'cstyn' changed to 'y")
        
    if 'stnod' not in kwargs:
        stnod = 'a'
    else:
        stnod = kwargs['stnod'].lower()
        if stnod not in ['a', 'e']: 
            stnod = 'a'
            print("\n'stnod' must be 'a'veraged or 'e'element. 'stnod' changed to 'a")
        
    if 'csryn' not in kwargs:
        csryn = 'n'
    else:
        csryn = kwargs['csryn'].lower()
        if csryn not in ['y', 'n']: 
            csryn = 'n'
            print("\n'csryn' must be 'y'es or 'n'o. 'csryn' changed to 'n")

    if 'ksres' not in kwargs:
        ksres = 1
    else:
        ksres = kwargs['ksres']
        if ksres not in [1, 2]:
            ksres = 1
            print("\n'ksres' must be 1 or 2. 'ksres' changed to 1")

    n = posfemixlib(filename.encode(), c_int(code), 
                    lcaco.encode(), cstyn.encode(), 
                    stnod.encode(), csryn.encode(), c_int(ksres))
    return n


def femSolver(filename: str, soalg: str='d', randsn: float=1.0e-6) -> int:
    """Reads the input file and solves the system of linear equations

    Args:
        filename (str): the name of the file to be read without extension
        soalg (str, optional): the algorithm used to solve the sysytem of linear equations, 'd' direct, 'i' iterative. Defaults to 'd'.
        randsn (float, optional): converge criteria to stop the iterative solver. Defaults to 1.0e-6.

    Returns:
        error code: 0 if no error, 1 if error
    """

    soalg = soalg.lower()
    if soalg not in ['d', 'i']:
        soalg = 'd'
        print("\n'soalg' must be 'd' or 'i'. 'soalg' changed to 'd")

    if randsn < 0 and soalg == 'i':
        randsn = 1.0e-6
        print("\n'randsn' must be > 0. 'randsn' changed to 1.0e-6")

    n = prefemixlib(filename.encode())
    n = femixlib(filename.encode(), soalg.encode(), c_double(randsn))
    print()
    return n

