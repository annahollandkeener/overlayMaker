
from overlayMaker.main import *

print("Hey")


#the "block" parameter must be a vector layer of a block within the project area with a "wl" column filled with 
#its respective water level
#the "overlayRange" parameter must be a list containing the overlays wished to be created below or above the current water level for the block 
#the "dem" parameter is the elevation for the project area

def stats(dem, blocks, overlayRange):
    #clipping dem to block 
    blockDEM = processing.run("gdal:cliprasterbymasklayer", {'INPUT':'C:/Users/KBE/Desktop/pyproj/overlays/overlay(1).tif','MASK':'C:/Users/KBE/Desktop/pyproj/overlays/block.shp','SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
    #getting raster stats of basic elevation for the block
    zonalStats = processing.run("native:zonalstatisticsfb", {'INPUT':'C:/Users/KBE/Desktop/pyproj/overlays/block.shp','INPUT_RASTER':'C:/Users/KBE/Desktop/pyproj/overlays/flat_raster(1).tif','RASTER_BAND':1,'COLUMN_PREFIX':'_','STATISTICS':[0,1,2],'OUTPUT':'TEMPORARY_OUTPUT'})
    
    
    for number in overlayRange:
        #keeping track of each different overlay generated
        n = 1
        #adding field to attribute table
        processing.run("native:addfieldtoattributestable", {'INPUT':'memory://MultiPolygon?crs=EPSG:2264&field=id:long(10,0)&field=wl:double(10,3)&field=_count:double(0,0)&field=_sum:double(0,0)&field=_mean:double(0,0)&uid={d255e972-07dd-48d3-ab0a-e863f64dee94}','FIELD_NAME':'wl','FIELD_TYPE':1,'FIELD_LENGTH':10,'FIELD_PRECISION':0,'FIELD_ALIAS':'','FIELD_COMMENT':'','OUTPUT':'TEMPORARY_OUTPUT'})        
        
        