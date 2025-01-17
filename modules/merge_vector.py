from imports import *

def printer():
    print("Call test")

'''
activeLayers = iface.layerTreeView().selectedLayers()

layersListHolder = [activeLayers]

layersPaths = []

layerNames = ''

for layersList in layersListHolder:
    for layer in layersList:
        layersPaths.append(layer.source())
        layerNames = layerNames + layer.name() + '_'

print(layerNames)


outputPath = 'C:/wfh/per1/overlays/wet/domed/Vectors/Inner+Outer/' + layerNames + '.shp'

processing.run("native:mergevectorlayers", {'LAYERS':layersPaths,'CRS':None,'OUTPUT':outputPath})

iface.addVectorLayer(outputPath, layerNames, "ogr")
'''