import numpy as np
import glob
import os

#Run after successfully creating all
#met_em files

year1, year2 = 1960, 2100

for iyear in np.arange(year1,year2+1):

	directive = 'rm WPS_%s/FILE*' %(iyear)
	os.system(directive)
	print (directive)
