from qgis.core import *
import ogr

def fromGeometry(geometry):
    instance = QgsPolylineV2()
    wkb = geometry.asWkb()
    geom = ogr.CreateGeometryFromWkb(wkb)
    geomCount = geom.GetPointCount()
    for pointIdx in range(geomCount):
        point = geom.GetPoint(pointIdx)
        instance.addPoint(point)

    return instance

class QgsPolylineV2():
    def __init__(self, list=[]):
        self.list = list

    def __iter__(self):
        return self.list

    def __getitem__(self, item):
        return self.list[item]

    def __setitem__(self, key, value):
        self.list[key] = value

    def __len__(self):
        return len(self.list)

    def __repr__(self):
        return str(self.list)

    def __add__(self, other):
        sumLine = QgsPolylineV2()
        sumLine.list = self.list + other.list
        return sumLine

    def endPoint(self):
        return self.list[-1]

    def addPoint(self, point):
        """

        :param point: QgsPointV2 instance
        :return: none
        """
        self.list.append(point)

    def startPoint(self):
        return self.list[0]

    def readGeometry(self, geometry):
        self.list = []
        wkb = geometry.asWkb()
        geom = ogr.CreateGeometryFromWkb(wkb)
        geomCount = geom.GetPointCount()
        for pointIdx in range(geomCount):
            point = geom.GetPoint(pointIdx)
            self.addPoint(point)

    def point2DAt(self, index):
        return QgsPoint(self.list[index][0], self.list[index][1])

    def toQgsGeometry(self):
        geom = ogr.Geometry(ogr.wkbLineString25D)
        for point in self.list:
            geom.AddPoint(*point)
        geom_wkb = geom.ExportToWkb()
        g = QgsGeometry()
        g.fromWkb(geom_wkb)
        return g