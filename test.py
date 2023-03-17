import modelmsh as msh
import os
import logging
import pathlib

logging.basicConfig(level=logging.DEBUG)

# fname = os.path.join( os.getcwd(), "tests/x4_t1_1.msh")
# path = pathlib.Path(fname)
# mesh = msh.mesh_handler()
# mesh.import_mesh(fname)
# fname = os.path.join(path.parent, path.stem + ".gldat")
# mesh.to_femix(fname)

# femix = msh.femix_handler()
# femix.run(fname)
# options = [{'code': msh.femixlib.RS_CSV, 'lcaco': 'l', 'cstyn': 'y', 'stnod': 'a', 'csryn': 'n', 'ksres': 2}]
# femix.posprocess(fname, options)

# femix.read_msh(fname)

slab = msh.Slab()

fname = os.path.join( os.getcwd(), "tests/test.s2k")
s2000 = msh.sap2000_handler(fname)
s2000.to_femix()
# fname = os.path.join( os.getcwd(), "test.xlsx")
# s2000.read_excel(fname, 'pandas')
s2000.to_msh_and_open(entities='sections', physicals='sections')

# s2000 = msh.sap2000_handler()
# fname = os.path.join( os.getcwd(), "tests/test.s2k")
# s2000.read_s2k(fname)
# fname = os.path.join( os.getcwd(), "tests/test-2.msh")
# s2000.write_msh(fname)

logging.debug("Test finished.")
