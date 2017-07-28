
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QColor

from ..addons import QgsPolylineV2

from qgis.core import *
from qgis.gui import *


def pointdistsq(p1, p2):
    x1 = p1.x()
    y1 = p1.y()
    x2 = p2.x()
    y2 = p2.y()

    return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)

class closeGapTool2:
    def __init__(self):
        pass

    def closeGapTool2(self, iface):
        layer = iface.legendInterface().currentLayer()
        if layer.isEditable() and layer.type() == QgsMapLayer.VectorLayer:
            if layer.selectedFeatureCount() == 2:
                f1 = layer.selectedFeatures()[0]
                polyline1 = QgsPolylineV2.QgsPolylineV2()
                polyline1.readGeometry(f1.geometry())

                f2 = layer.selectedFeatures()[1]
                polyline2 = QgsPolylineV2.QgsPolylineV2()
                polyline2.readGeometry(f2.geometry())

                start1 = polyline1.point2DAt(0)
                end1 = polyline1.point2DAt(-1)

                start2 = polyline2.point2DAt(0)
                end2 = polyline2.point2DAt(-1)

                ds1s2 = pointdistsq(start1, start2)
                ds1e2 = pointdistsq(start1, end2)
                de1s2 = pointdistsq(end1, start2)
                de1e2 = pointdistsq(end1, end2)
                mindist = min([ds1s2, ds1e2, de1e2, de1s2])

                if ds1s2 == mindist:
                    polyline1 = QgsPolylineV2.QgsPolylineV2(polyline1[::-1])
                elif ds1e2 == mindist:
                    polyline1 = QgsPolylineV2.QgsPolylineV2(polyline1[::-1])
                    polyline2 = QgsPolylineV2.QgsPolylineV2(polyline2[::-1])
                elif de1s2 == mindist:
                    pass
                elif de1e2 == mindist:
                    polyline2 = QgsPolylineV2.QgsPolylineV2(polyline2[::-1])

                polylineSum = polyline1 + polyline2
                ptsNew = polylineSum
                if len(ptsNew) > 1:  # can be a linestring
                    plNew = ptsNew.toQgsGeometry()
                    layer.changeGeometry(f1.id(), plNew)
                layer.deleteFeature(f2.id())

            elif layer.selectedFeatureCount() == 1:
                f1 = layer.selectedFeatures()[0]
                polyline = QgsPolylineV2.QgsPolylineV2()
                polyline.readGeometry(f1.geometry())
                polyline.addPoint(polyline.startPoint())
                polyline = polyline.toQgsGeometry()
                layer.changeGeometry(f1.id(), polyline)
        iface.mapCanvas().refresh()
        layer.setSelectedFeatures([])