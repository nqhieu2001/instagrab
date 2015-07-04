from distutils.core import setup
import py2exe

setup(
	windows=[{"script":"instagrab-gui.py","dest_base":"Instagrab"}],
	data_files=["cacert.pem"], 
	options={"py2exe":{"includes":["sip"]}}
	)