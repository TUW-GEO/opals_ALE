

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QColor

from qgis.core import *
from qgis.gui import *

class rmEdgeTool(QgsMapTool):
    def __init__(self, canvas, layer, iface, action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.layer = layer
        self.iface = iface
        self.action = action
        self.rb = None
        self.threshold = QSettings().value('ale/threshold')

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        if self.rb:
            self.canvas.scene().removeItem(self.rb)
        layerPoint = self.toLayerCoordinates(self.layer, event.pos())
        # get closest feature
        shortestDistance = float("inf")
        closestFeature = None
        for f in self.layer.getFeatures():
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
            for i in range(len(polyline) - 1):
                linePart = polyline[i:i + 2]
                dist = QgsGeometry.fromPolyline(linePart).distance(QgsGeometry.fromPoint(layerPoint))
                if dist < shortestDistance:
                    shortestDistance = dist
                    closestPointID = i
            if closestPointID is not None and shortestDistance < self.threshold:
                self.rb = QgsRubberBand(self.canvas, False)
                # False = not a polygon
                points = polyline[closestPointID:closestPointID+2]
                self.rb.setToGeometry(QgsGeometry.fromPolyline(points), None)
                self.rb.setColor(QColor(0, 0, 255))
                self.rb.setWidth(3)


    def canvasReleaseEvent(self, event):
        layerPoint = self.toLayerCoordinates(self.layer, event.pos())
        # get closest feature
        shortestDistance = float("inf")
        closestFeature = None
        for f in self.layer.getFeatures():
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
            for i in range(len(polyline)-1):
                linePart = polyline[i:i+2]
                dist = QgsGeometry.fromPolyline(linePart).distance(QgsGeometry.fromPoint(layerPoint))
                if dist < shortestDistance:
                    shortestDistance = dist
                    closestPointID = i
            if closestPointID is not None and shortestDistance < self.threshold:
                ftNew = QgsFeature()
                ptsNew = polyline[closestPointID+1:]
                if len(ptsNew) > 1: # can be a linestring
                    plNew = QgsGeometry.fromPolyline(ptsNew)
                    ftNew.setGeometry(plNew)
                    pr = self.layer.dataProvider()
                    pr.addFeatures([ftNew])
                ptsOld = polyline[:closestPointID+1]
                if len(ptsOld) > 1: # can be a linestring
                    plOld = QgsGeometry.fromPolyline(ptsOld)
                    self.layer.changeGeometry(closestFeature.id(), plOld)
                else:
                    self.layer.deleteFeature(closestFeature.id())

        if self.rb:
            self.canvas.scene().removeItem(self.rb)
        self.iface.mapCanvas().refresh()

    def activate(self):
        self.action.setChecked(True)

    def deactivate(self):
        if self.rb:
            self.canvas.scene().removeItem(self.rb)
        self.action.setChecked(False)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True