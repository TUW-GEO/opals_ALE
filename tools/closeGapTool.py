
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QColor

from qgis.core import *
from qgis.gui import *

import finder

class closeGapTool(QgsMapTool):
    def __init__(self, canvas, layer, iface, action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.layer = layer
        self.iface = iface
        self.action = action
        self.rb = None
        self.vx = None
        self.p1 = None
        self.f1 = None
        self.p2 = None
        self.f2 = None
        self.threshold = QSettings().value('ale/threshold')

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        if self.rb:
            self.canvas.scene().removeItem(self.rb)
        if self.vx:
            self.canvas.scene().removeItem(self.vx)

        layerPoint = self.toLayerCoordinates(self.layer, event.pos())
        (closestPointID, closestFeature) = finder.closestpoint(self.layer, layerPoint)
        polyline = closestFeature.geometry().asPolyline()
        shortestDistance = QgsGeometry.fromPoint(polyline[closestPointID]).distance(QgsGeometry.fromPoint(layerPoint))
        if closestPointID is not None and shortestDistance < self.threshold and (closestPointID == 0 or closestPointID == len(polyline)-1):
                self.vx = QgsVertexMarker(self.canvas)
                self.vx.setCenter(QgsPoint(polyline[closestPointID]))
                self.vx.setColor(QColor(0, 255, 0))
                self.vx.setIconSize(5)
                self.vx.setIconType(QgsVertexMarker.ICON_X)# or ICON_CROSS, ICON_BOX
                self.vx.setPenWidth(3)
                if self.p1:
                    self.rb = QgsRubberBand(self.canvas, False)
                    linePart = [self.p1, polyline[closestPointID]]
                    self.rb.setToGeometry(QgsGeometry.fromPolyline(linePart), None)
                    self.rb.setColor(QColor(0, 0, 255))
                    self.rb.setWidth(3)


    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton: # right click
            self.p1 = None
            self.p2 = None
            self.f1 = None
            self.f2 = None
            if self.rb:
                self.canvas.scene().removeItem(self.rb)
            if self.vx:
                self.canvas.scene().removeItem(self.vx)

        elif event.button() == Qt.LeftButton: #left click
            layerPoint = self.toLayerCoordinates(self.layer, event.pos())
            (closestPointID, closestFeature) = finder.closestpoint(self.layer, layerPoint)
            polyline = closestFeature.geometry().asPolyline()
            shortestDistance = QgsGeometry.fromPoint(polyline[closestPointID]).distance(QgsGeometry.fromPoint(layerPoint))
            if closestPointID is not None and shortestDistance < self.threshold and (closestPointID == 0 or closestPointID == len(polyline)-1):
                if not self.p1:
                    self.p1 = polyline[closestPointID]
                    self.f1 = closestFeature
                else:
                    self.p2 = polyline[closestPointID]
                    self.f2 = closestFeature
                    polyline1 = self.f1.geometry().asPolyline()
                    polyline2 = polyline
                    if self.p1 == polyline1[0]:
                        polyline1 = polyline1[::-1]
                    if self.p2 == polyline2[-1]:
                        polyline2 = polyline2[::-1]

                    polylineSum = polyline1 + polyline2
                    ftNew = QgsFeature()
                    ptsNew = polylineSum
                    if len(ptsNew) > 1: # can be a linestring
                        plNew = QgsGeometry.fromPolyline(ptsNew)
                        ftNew.setGeometry(plNew)
                        pr = self.layer.dataProvider()
                        pr.addFeatures([ftNew])
                    self.layer.deleteFeature(self.f1.id())
                    self.layer.deleteFeature(self.f2.id())
                    self.p1 = None
                    self.f1 = None
                    self.p2 = None
                    self.f2 = None

                if self.rb:
                    self.canvas.scene().removeItem(self.rb)
                if self.vx:
                    self.canvas.scene().removeItem(self.vx)
                self.iface.mapCanvas().refresh()

    def activate(self):
        self.action.setChecked(True)

    def deactivate(self):
        if self.rb:
            self.canvas.scene().removeItem(self.rb)
        if self.vx:
            self.canvas.scene().removeItem(self.vx)
        self.action.setChecked(False)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True