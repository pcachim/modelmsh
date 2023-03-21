"""
Define the C-variables and functions from the C-files that are needed in Python
"""
from ctypes import c_double, c_int, CDLL, POINTER
import os
import pandas as pd
import pathlib
import zipfile

ME_S3D  =  1 # /*    1) _me.s3d file with the undeformed mesh.                      */
GE_S3D  =  2 # /*    2) _ge.s3d file with the geometric data.                       */
GL_LPT  =  3 # /*    3) _gl.lpt file with the geometry and loads.                   */
RS_LPT  =  4 # /*    4) _rs.lpt file with the results.                              */
DM_S3D  =  5 # /*    5) _dm.s3d file with the deformed mesh.                        */
DI_PVA  =  6 # /*    6) _di.pva file with the nodal displacements.                  */
PS_S3D  =  7 # /*    7) _ps.s3d file with the principal stresses.                   */
ST_PVA  =  8 # /*    8) _st.pva file with the nodal stresses.                       */
SG_S3D  =  9 # /*    9) _sg.s3d file with the stress graphics.                      */
SR_PVA  = 10 # /*   10) _sr.pva file with the nodal reinforcement.                  */
RG_S3D  = 11 # /*   11) _rg.s3d file with the reinforcement graphics.               */
RS_CSV  = 12 # /*   12) _rs.csv file with the results.                              */
ME_S3DX = 13 # /*   13) _me.s3dx file with the results.                             */
DM_S3DX = 14 # /*   14) _dm.s3dx file with the deformed mesh.                       */
AST_CSV = 15 # /*   15) _avgst.csv file with the stresses in the nodes.             */
EST_CSV = 16 # /*   16) _elnst.csv file with the stresses in the nodes.             */
DI_CSV  = 17 # /*   17) _di.csv file with the displacements in the nodes.           */

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

posofemlib = libfemixpy.posofemlib
posofemlib.restype = int

def compress_ofem(filename: str):
    """_summary_

    Args:
        filename (str): the name of the file to be read

    Returns:
        error code: 0 if no error, 1 if error
    """""""""
    jobname = pathlib.Path(filename).stem
    with zipfile.ZipFile(filename + '.ofem', 'w') as ofemfile:
        ofemfile.write(filename + '.gldat', arcname=jobname+".gldat", compress_type=zipfile.ZIP_DEFLATED)
        ofemfile.write(filename + '_gl.bin', arcname=jobname+"_gl.bin")
        ofemfile.write(filename + '_re.bin', arcname=jobname+"_re.bin")
        ofemfile.write(filename + '_di.bin', arcname=jobname+"_di.bin")
        ofemfile.write(filename + '_sd.bin', arcname=jobname+"_sd.bin")
        if pathlib.Path(filename + '_st.bin').exists():
            ofemfile.write(filename + '_st.bin', arcname=jobname+"_st.bin", compress_type=zipfile.ZIP_DEFLATED)
        if pathlib.Path(filename + '_di.csv').exists():
            ofemfile.write(filename + '_di.csv', arcname=jobname+"_di.csv", compress_type=zipfile.ZIP_DEFLATED)
        if pathlib.Path(filename + '_avgst.csv').exists():
            ofemfile.write(filename + '_avgst.csv', arcname=jobname+"_avgst.csv", compress_type=zipfile.ZIP_DEFLATED)
        if pathlib.Path(filename + '_elnst.csv').exists():
            ofemfile.write(filename + '_elnst.csv', arcname=jobname+"_elnst.csv", compress_type=zipfile.ZIP_DEFLATED)

    remove_ofem_files(filename)
    return


def add_to_ofem(filename: str, file_to_add: str):
    """_summary_

    Args:
        filename (str): the name of the file to be read

    Returns:
        error code: 0 if no error, 1 if error
    """""""""
    jobname = pathlib.Path(filename).name
    with zipfile.ZipFile(filename + '.ofem', 'a') as ofemfile:
        ofemfile.write(file_to_add, arcname=jobname, compress_type=zipfile.ZIP_DEFLATED)

    os.remove(file_to_add)
    return


def get_csv_from_ofem(filename: str, code: int) -> pd.DataFrame:
    """_summary_

    Args:
        filename (str): _description_
        code (int): _description_

    Returns:
        pd.DataFrame: _description_
    """

    path = pathlib.Path(filename + '.ofem')
    if code == DI_CSV:
        file_to_extract = pathlib.Path(filename + '_di.csv')
    elif code == EST_CSV:
        file_to_extract = pathlib.Path(filename + '_elnst.csv')
    elif code == AST_CSV:
        file_to_extract = pathlib.Path(filename + '_avgst.csv')
        
    with zipfile.ZipFile(filename + '.ofem', 'r') as ofemfile:
        with ofemfile.open(file_to_extract.name) as file:
            df = pd.read_csv(file, sep=';')

    return df


def remove_ofem_files(filename: str):
    os.remove(filename + '.gldat')
    os.remove(filename + '_gl.bin')
    os.remove(filename + '_re.bin')
    os.remove(filename + '_di.bin')
    os.remove(filename + '_sd.bin')
    if pathlib.Path(filename + '_st.bin').exists():
        os.remove(filename + '_st.bin')
    if pathlib.Path(filename + '_di.csv').exists():
        os.remove(filename + '_di.csv')
    if pathlib.Path(filename + '_avgst.csv').exists():
        os.remove(filename + '_avgst.csv')
    if pathlib.Path(filename + '_elnst.csv').exists():
        os.remove(filename + '_elnst.csv')
    return

def extract_ofem(filename: str):
    path = pathlib.Path(filename + '.ofem')
    with zipfile.ZipFile(filename + '.ofem', 'r') as ofemfile:
        ofemfile.extractall(path.parent)
    return


def extract_ofem_bin(filename: str):
    path = pathlib.Path(filename + '.ofem')
    with zipfile.ZipFile(filename + '.ofem', 'r') as ofemfile:
        # listOfFileNames = ofemfile.namelist()
        for fileName in ofemfile.namelist():
            if fileName.endswith('.bin'):
                ofemfile.extract(path.name, path.parent)
    return


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


def ofemPostprocess(filename: str, **kwargs):
    """_summary_

    Args:
        filename (str): the name of the file to be read

    Returns:
        error code: 0 if no error, 1 if error
    """""""""
    
    extract_ofem(filename)

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

    if 'kstre' not in kwargs:
        kstre = 1
    else:
        kstre = kwargs['kstre']
        if kstre not in [1, 2, 3, 4, 5, 6, 7, 8]:
            kstre = 1
            print("\n'kstre' must be between 1 and 8. 'ksres' changed to 1")

    if 'kdisp' not in kwargs:
        kdisp = 1
    else:
        kdisp = kwargs['kdisp']
        if kdisp not in [1, 2, 3, 4, 5, 6]:
            kdisp = 1
            print("\n'kdisp' must be between 1 and 6. 'ksres' changed to 1")

    n = posfemixlib(filename.encode(), c_int(code), 
                    lcaco.encode(), cstyn.encode(), 
                    stnod.encode(), csryn.encode(), 
                    c_int(ksres), c_int(kstre), c_int(kdisp))

    compress_ofem(filename)
    #add_to_ofem(filename)

    return n


def ofemPostsolver(filename: str, codes: list, **kwargs):
    """_summary_

    Args:
        filename (str): the name of the file to be read

    Returns:
        error code: 0 if no error, 1 if error
    """""""""
    
    extract_ofem(filename)

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

    if 'kstre' not in kwargs:
        kstre = 1
    else:
        kstre = kwargs['kstre']
        if kstre not in [1, 2, 3, 4, 5, 6, 7, 8]:
            kstre = 1
            print("\n'kstre' must be between 1 and 8. 'ksres' changed to 1")

    if 'kdisp' not in kwargs:
        kdisp = 1
    else:
        kdisp = kwargs['kdisp']
        if kdisp not in [1, 2, 3, 4, 5, 6]:
            kdisp = 1
            print("\n'kdisp' must be between 1 and 6. 'ksres' changed to 1")

    ncode = len(codes)

    # Pass a pointer to the integer object to the C function
    myarray = (c_int * len(codes))(*codes)
    n = posofemlib(filename.encode(), c_int(ncode), myarray,
                    lcaco.encode(), cstyn.encode(), 
                    stnod.encode(), csryn.encode(), 
                    c_int(ksres), c_int(kstre), c_int(kdisp))

    compress_ofem(filename)
    #add_to_ofem(filename)

    return n


def ofemSolver(filename: str, soalg: str='d', randsn: float=1.0e-6) -> int:
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
    
    compress_ofem(filename)

    return n


def ofemReadCSV(filename: str) -> pd.DataFrame:
    """Reads the stress output file

    Args:
        filename (str): the name of the file to be read without extension

    Returns:
        error code: 0 if no error, 1 if error
    """

    df = pd.read_csv(filename, sep=';')
    return df


def ofemReadPVA(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename, sep='\s+', header=None)
    df.columns = ['point', 'values']
    return df
