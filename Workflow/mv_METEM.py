import os

for iyear in range(1940,1980):

	directive = 'mv WPS_%s/met_em* met_em_files' %(iyear)
	os.system(directive)
	print (directive)
