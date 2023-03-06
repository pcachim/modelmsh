import modelmsh as msh
import os
import logging

logging.basicConfig(level=logging.DEBUG)

femix = msh.femix_handler()
fname = os.path.join( os.getcwd(), "tests/x4_t1_1.msh")
femix.read_msh(fname)
femix.read_s3dx(fname)

s2000 = msh.sap2000_handler()

#fname = os.path.join( os.getcwd(), "test.s2k")
#s2000.read_s2k(fname)
fname = os.path.join( os.getcwd(), "test.xlsx")
s2000.read_excel(fname, 'pandas')
fname = os.path.join( os.getcwd(), "test.msh")
s2000.write_msh_2(fname)

logging.debug("Test finished.")
