from qgis.core import *

def closestpoint(layer, layerPoint):

    # get closest feature
    shortestDistance = float("inf")
    closestFeature = None
    for f in layer.getFeatures():
        if f.geometry():
            dist = f.geometry().distance(QgsGeometry.fromPoint(layerPoint))
            if dist < shortestDistance:
                shortestDistance = dist
                closestFeature = f

    if closestFeature and closestFeature.geometry():
        # get closest segment
        shortestDistance = float("inf")
        closestPointID = None
        polyline = closestFeature.geometry().asPolyline()
        for i in range(len(polyline)):
            point = polyline[i]
            dist = QgsGeometry.fromPoint(point).distance(QgsGeometry.fromPoint(layerPoint))
            if dist < shortestDistance:
                shortestDistance = dist
                closestPointID = i

        return (closestPointID, closestFeature)

    else:
        return (None, None)

def closestsegment(layer, event):
    pass