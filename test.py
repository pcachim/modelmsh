import modelmsh as msh
import os
import logging
import timeit

logging.basicConfig(level=logging.DEBUG)

starttime = timeit.default_timer()
s2000 = msh.sap2000_handler()

fname = os.path.join( os.getcwd(), "test.s2k")
s2000.read_s2k(fname)
#fname = os.path.join( os.getcwd(), "test.xlsx")
#s2000.read_excel(fname, 'pandas')
fname = os.path.join( os.getcwd(), "test.msh")
s2000.write_msh_2(fname)

logging.info(f"Execution time: {round((timeit.default_timer() - starttime)*1000,3)} ms")
logging.debug("Test finished.")
