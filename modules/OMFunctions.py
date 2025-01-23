#--------------MANUAL INPUTS--------------
#NOTICE: Change manual to "True" if entering data manually. 
manual = True

#Set desired functions to "True" and undesired functions to "False"
functions = {

#generates overlays for a set of blocks by subtracting their flat water levels from the project area DEM
"flatOverlays" : False, 
#generates overlays for a set of blocks by subtracting their domed water levels from the project area DEM
"domedOverlays" : False,
#generates a range of overlays and histograms within a specified range for a given block 
"histogram" : True

}

#paths to vector files of blocks you want to make domes for
domedBlocks = ['']

#path to dem for project area
dem = "C:/wfh/per1/elevation/CarolinaRanch_2020lidar_3ft (2).tif"

#vector file including all blocks in project area 
#requires a "wl" column with a water level for each block
blocks = ["C:/wfh/per1/overlays/dry/all blocks/PER1_Blocks_Dry.shp"]

#for histogram creation. Allows for multiple overlays to be generated within specified distance from pre-existing water level
overlayRange = [-1.5, -1, -.5, 0, .5, 1, 1.5]

#output folder for flat overlays
outputFolderFO = "C:/wfh/per1/overlays/wet/completed_overlays/flat/"

#output folder for domed overlays
outputFolderDO = "C:/wfh/per1/overlays/wet/domed/dome_rasters/"

#QGIS style file 
stylePath = "C:/wfh/per1/overlays/styling/overlays_-.5to2.qml"

#--------PREP-------------------------------------------------------------------------

#if not manually inputting data, user input from main.py will be used (within the overlayMaker repo)
if manual != "YES":
    from imports import *

#-------FUNCTIONS--------------------------------------------------------------------------

#******Raster Subtractor*****
#Takes in path of elevation dem, path of dem representing water surface and a path of output folder
def rasterSubtractor(dem, waterTable, outputFolder):
    #subtracting flat raster of blocks from DEM using raster calculator
        #getting basename of file being used
        baseName = os.path.basename(waterTable).split(".")[0]
        
        outputPath = outputFolder + baseName
        
        topDEM = QgsRasterLayer(dem, "topDEM")
        bottomDEM = QgsRasterLayer(waterTable, "bottomDEM")
        
        top = QgsRasterCalculatorEntry()
        top.raster = topDEM
        top.bandNumber = 1
        top.ref = 'top_raster@1'
        
        bottom = QgsRasterCalculatorEntry()
        bottom.raster = bottomDEM
        bottom.bandNumber = 1
        bottom.ref = 'bottom_raster@1'
        
        calc=QgsRasterCalculator(('"top_raster@1" - "bottom_raster@1"'), outputPath, 'GTiff', bottomDEM.extent(), bottomDEM.width(), bottomDEM.height(), [top, bottom])
        calc.processCalculation()

        #adding raster to map viewer
        rasterOutput = iface.addRasterLayer(outputPath, baseName, "gdal")
        
        #styling raster
        rasterOutput.loadNamedStyle(stylePath)
        #updating raster to reflect style
        iface.layerTreeView().refreshLayerSymbology(rasterOutput.id())

        
        return calc

    
#******Generation of flat overlays****
def flatOverlays(dem = dem, blocks = blocks, outputFolder = outputFolderFO):
    
    print("\n----GENERATING FLAT OVERLAYS----\n")
    
    activeLayerPaths = []

    activeLayerPaths = blocks

    #for each selected layer (blocks)...
    for layer in blocks:
        baseName = os.path.basename(layer).split(".")[0]
        
        layer = str(layer)
        
        #creating output paths for flat rasterized blocks and overlay
        outputPath = outputFolder  + 'flat_raster_' + baseName + '.tif'
        outputPathOverlay = outputFolder  + 'overlay_' + baseName + '.tif'
        
        #create a flat raster based on the waterlevel of each block
        blockFlatRaster = processing.run("gdal:rasterize", {'INPUT':layer,'FIELD':'wl','BURN':0,'USE_Z':False,'UNITS':1,'WIDTH':3,'HEIGHT':3,'EXTENT':None,'NODATA':0,'OPTIONS':None,'DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':outputPath})
        #iface.addRasterLayer(outputPath, 'blockFlatRaster', "gdal")
        
        #subtracting flat rasterized vector from 
        rasterSubtractor(dem, blockFlatRaster['OUTPUT'], outputFolder)
        
        
    print("/nFLAT OVERLAY CREATION COMPLETE!")

#******Generation of domed block overlays****
#vector file must be set up with inner and outer features
#the layer must have a wl set up as the second attribute/column in the table

def domedOverlays(dem = dem, domedBlocks = blocks, outputFolder = outputFolderDO):
    print("\n----GENERATING DOMED OVERLAYS----/n")
    
    #saving sources of clipped domes in order to merge later
    clippedDomes = []
    
    print("\nNumber of blocks to be domed: " + str(len(domedBlocks)) +"/n")
    
    n = 1

    for dome in domedBlocks:
        
        #getting name of vector layer from path
        baseName = os.path.basename(dome).split(".")[0]
        
        #saving the vector in a variable
        domeLayer = QgsVectorLayer(dome, baseName, "ogr")
        
        #checking for validity of layer and skipping if necessary
        if not domeLayer.isValid():
            print("/n" + baseName + " is not valid. /nSkipping.../n")
            continue
        
        #iface.addVectorLayer(domeLayer.source(), baseName, "ogr")
        
        #getting extent of domed block 
        extent = domeLayer.extent()
        
        #setting up path and instructions for TIN interpolation tool
        interpolationData = dome + '::~::0::~::1::~::2::'
        
        #setting outputs for each stage of the overlay
        outputPathRough = outputFolder + 'roughDome_' + baseName + '.tif'
        outputPathResampled =  outputFolder + 'resampledDome' + baseName + '.tif'
        outputPathClipped = outputFolder + 'smoothDome' + baseName + '.tif'
        
        #calculating rough dome and adding to map viewer
        domeRough = processing.run("qgis:tininterpolation", {'INTERPOLATION_DATA':interpolationData,'METHOD':0,'EXTENT':extent,'PIXEL_SIZE':15,'OUTPUT': outputPathRough})
        #iface.addRasterLayer(domeRough["OUTPUT"], 'roughDome_' + baseName)
        
        #calculating smooth dome and adding to map viewer
        domeSmooth = processing.run("grass:r.resamp.filter", {'input':outputPathRough,'filter':[0],'radius':'200','x_radius':'','y_radius':'','-n':False,'output': 'TEMPORARY_OUTPUT','GRASS_REGION_PARAMETER':None,'GRASS_REGION_CELLSIZE_PARAMETER':0,'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':''})
        #iface.addRasterLayer(domeSmooth['output'], 'smoothDome_' + baseName)
        
        
        #clipping dome to block and adding to map viewer
        domeClipped = processing.run("gdal:cliprasterbymasklayer", {'INPUT':domeSmooth['output'],'MASK':dome,'SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':extent,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':outputPathClipped})
        #iface.addRasterLayer(domeClipped['OUTPUT'], 'clippedDome_' + baseName)
        
        #adding final clipped domes to a list
        clippedDomes.append(domeClipped['OUTPUT'])
        
        print("COMPLETED DOME (" + str(n) + "): " + baseName)
        n = n + 1
        
        
    #merging all domes    
    merge = processing.run("gdal:merge", {'INPUT':clippedDomes,'PCT':False,'SEPARATE':False,'NODATA_INPUT':None,'NODATA_OUTPUT':0,'OPTIONS':None,'EXTRA':'','DATA_TYPE':5,'OUTPUT':outputFolder + '/all_domed_merged.tif'})
    
    #adding merged domes to map viewer
    iface.addRasterLayer(merge["OUTPUT"], "merged_domed_rasters", "gdal")
    
    #subtracting merged domes from dem to create overlay for domes
    rasterSubtractor(dem, merge['OUTPUT'], outputFolderDO)
    
    print("\nDOMED OVERLAY CREATION COMPLETED! :)")
    
  
#histogram function takes in a single block and creates overlays and corresponding histograms for a specified range 
def histogram(dem = dem, blocks = blocks, overlayRange = overlayRange):
    print("HEYYYY")
    #clipping dem to block 
    blockDEM = processing.run("gdal:cliprasterbymasklayer", {'INPUT':'C:/Users/KBE/Desktop/pyproj/overlays/overlay(1).tif','MASK':'C:/Users/KBE/Desktop/pyproj/overlays/block.shp','SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
    #getting raster stats of b    asic elevation for the block
    zonalStats = processing.run("native:zonalstatisticsfb", {'INPUT':'C:/Users/KBE/Desktop/pyproj/overlays/block.shp','INPUT_RASTER':'C:/Users/KBE/Desktop/pyproj/overlays/flat_raster(1).tif','RASTER_BAND':1,'COLUMN_PREFIX':'_','STATISTICS':[0,1,2],'OUTPUT':'TEMPORARY_OUTPUT'})
    
    
    for number in overlayRange:
        #keeping track of each different overlay generated
        n = 1
        #adding field to attribute table
        processing.run("native:addfieldtoattributestable", {'INPUT':'memory://MultiPolygon?crs=EPSG:2264&field=id:long(10,0)&field=wl:double(10,3)&field=_count:double(0,0)&field=_sum:double(0,0)&field=_mean:double(0,0)&uid={d255e972-07dd-48d3-ab0a-e863f64dee94}','FIELD_NAME':'wl','FIELD_TYPE':1,'FIELD_LENGTH':10,'FIELD_PRECISION':0,'FIELD_ALIAS':'','FIELD_COMMENT':'','OUTPUT':'TEMPORARY_OUTPUT'})        

    
#-------------EXECUTIONS------------

#if manual mode is active, the file will execute every function set to "True" in the inputs
print("FUNCTION TEST")

if manual == True:
    for f in functions.keys():
        if functions[f] == True:
            if f == "flatOverlays":
                flatOverlays()
            elif f == "domedOverlays":
                domedOverlays()
            elif f == "histogram":
                histogram()


