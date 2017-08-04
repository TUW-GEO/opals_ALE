# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ALE
                                 A QGIS plugin
 Adds line editing tools (segment deletion, ...)
                              -------------------
        begin                : 2017-01-18
        git sha              : $Format:%H$
        copyright            : (C) 2017 by lwiniwar/TU Wien
        email                : lukas.winiwarter@geo.tuwien.ac.at
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QVariant
from PyQt4.QtGui import QAction, QIcon, QColor, QCursor, QPixmap, QBitmap

from qgis.core import *
from qgis.gui import *

from tools import rmEdgeTool, rmVertexTool, closeGapTool

# Initialize Qt resources from file resources.py
#import resources


# Import the code for the DockWidget
import os.path



class ALE:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ALE_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        if not QSettings().value('ale/threshold', None):
            QSettings().setValue('ale/threshold', 10)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Advanced Line Editor')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ALE')
        self.toolbar.setObjectName(u'ALE')

        # print "** INITIALIZING ALE"
        self.bm = QBitmap(os.path.join(self.plugin_dir, 'imgs', 'cursor-cross.png'))

        self.pluginIsActive = False
        self.iface.currentLayerChanged.connect(self.currentLayerChanged)
        self.mapLayerRegistry = QgsMapLayerRegistry.instance()
        self.mapLayerRegistry.layersAdded.connect(self.currentLayerChanged)
        # check currently selected layer
        self.currentlayer = None
        self.currentLayerChanged()




    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ALE', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        checkable=False,
        shortcut=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if checkable:
            action.setCheckable(True)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)
        if shortcut:
            action.setShortcut(shortcut)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # self.closeringaction = self.add_action(os.path.join(self.plugin_dir, 'imgs', 'closering.png'),
        #                 'Close selected line to ring',
        #                 self.closering,
        #                 status_tip='Close selected line to ring',
        #                 enabled_flag=False,
        #                 shortcut="1")
        self.splitsegmentaction = self.add_action(os.path.join(self.plugin_dir, 'imgs', 'splitsegment.png'),
                        'Split at segment',
                        self.splitsegment,
                        status_tip='Split at segment',
                        checkable=True,
                        enabled_flag=False,
                        shortcut="Ctrl+1")
        # self.joinlinesaction = self.add_action(os.path.join(self.plugin_dir, 'imgs', 'joinlines.png'),
        #                 'Join lines',
        #                 self.joinlines,
        #                 status_tip='Join lines',
        #                 checkable=True,
        #                 enabled_flag=False,
        #                 shortcut="3")

        self.splitvertexaction = self.add_action(os.path.join(self.plugin_dir, 'imgs', 'rmvertex.png'),
                        'Remove vertex and split',
                        self.splitvertex,
                        status_tip='Remove vertex and split',
                        checkable=True,
                        enabled_flag=False,
                        shortcut="Ctrl+2")

        self.joinlinesaction2 = self.add_action(os.path.join(self.plugin_dir, 'imgs', 'joinlines.png'),
                        'Join lines (noninteractive)',
                        self.joinlines2,
                        status_tip='Join lines(non-interactive)',
                        checkable=False,
                        enabled_flag=False,
                        shortcut="j")


        self.unsureaction = self.add_action(os.path.join(self.plugin_dir, 'imgs', 'markasunsure.png'),
                        'Mark selected line(s) as unsure',
                        self.markAsUnsure,
                        status_tip='Mark selected line(s) as unsure',
                        checkable=False,
                        enabled_flag=False,
                        shortcut="u")

        self.doneaction = self.add_action(os.path.join(self.plugin_dir, 'imgs', 'markasdone.png'),
                        'Mark selected line(s) as done',
                        self.markAsDone,
                        status_tip='Mark selected line(s) as done',
                        checkable=False,
                        enabled_flag=False,
                        shortcut="d")

        self.ununsureaction = self.add_action(os.path.join(self.plugin_dir, 'imgs', 'unmarkasunsure.png'),
                        'Unmark selected line(s)',
                        self.unmarkAsUnsure,
                        status_tip='Unmark selected line(s)',
                        checkable=False,
                        enabled_flag=False,
                        shortcut="r")


    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING ALE"


        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD ALE"

        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Advanced Line Editor'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

        self.iface.currentLayerChanged.disconnect(self.currentLayerChanged)
        self.mapLayerRegistry.layersAdded.disconnect(self.currentLayerChanged)

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

    def closering(self):
        # get selected layer:
        layer = self.iface.legendInterface().currentLayer()
        if layer.isEditable() and layer.type() == QgsMapLayer.VectorLayer:
            if layer.selectedFeatureCount() > 0:
                features = layer.selectedFeatures()
                for feat in features:
                    geom = feat.geometry().asPolyline()
                    geom.append(geom[0])
                    polyline = QgsGeometry.fromPolyline(geom)
                    layer.changeGeometry(feat.id(), polyline)
        self.iface.mapCanvas().refresh()

    def joinlines2(self):
        from tools import closeGapTool2
        tool = closeGapTool2.closeGapTool2()
        tool.closeGapTool2(self.iface)
        tool = None

    def splitsegment(self):
        # get selected layer:
        layer = self.iface.legendInterface().currentLayer()
        if layer.isEditable() and layer.type() == QgsMapLayer.VectorLayer:
            etool = rmEdgeTool(self.iface.mapCanvas(), layer, self.iface, self.splitsegmentaction)
            c = QCursor(self.bm, self.bm)
            self.iface.mapCanvas().setCursor(c)
            self.iface.mapCanvas().setMapTool(etool)

    def splitvertex(self):
        # get selected layer:
        layer = self.iface.legendInterface().currentLayer()
        if layer.isEditable() and layer.type() == QgsMapLayer.VectorLayer:
            vtool = rmVertexTool(self.iface.mapCanvas(), layer, self.iface, self.splitvertexaction)
            c = QCursor(self.bm, self.bm)
            self.iface.mapCanvas().setMapTool(vtool)
            self.iface.mapCanvas().setCursor(c)


    def joinlines(self):
        # get selected layer:
        layer = self.iface.legendInterface().currentLayer()
        if layer.isEditable() and layer.type() == QgsMapLayer.VectorLayer:
            gtool = closeGapTool(self.iface.mapCanvas(), layer, self.iface, self.joinlinesaction)
            self.iface.mapCanvas().setMapTool(gtool)


    def currentLayerChanged(self):
        if self.currentlayer is not None:
            self.currentlayer.editingStarted.disconnect(self.curLayerIsEditable)
            self.currentlayer.editingStopped.disconnect(self.curLayerIsNotEditable)

        layer = self.iface.legendInterface().currentLayer()
        if layer is not None:
            if layer.type() != QgsMapLayer.VectorLayer:
                layer = None
            elif layer.geometryType() != QGis.Line:
                layer = None

        if layer is not None:
            layer.editingStarted.connect(self.curLayerIsEditable)
            layer.editingStopped.connect(self.curLayerIsNotEditable)
            if layer.isEditable():  # in case an editable layer is selected
                self.curLayerIsEditable()
            else:
                self.curLayerIsNotEditable()
        else:
            self.curLayerIsNotEditable()

        self.currentlayer = layer

    def curLayerIsEditable(self):
        for act in self.actions:
            act.setEnabled(True)

    def curLayerIsNotEditable(self):
        self.iface.actionPan().trigger()
        for act in self.actions:
            act.setEnabled(False)

    def markAsUnsure(self):
        layer = self.iface.legendInterface().currentLayer()
        if layer.isEditable() and layer.type() == QgsMapLayer.VectorLayer:
            fields = {field.name(): id for (id, field) in enumerate(layer.dataProvider().fields())}
            if u'Status' not in fields:
                res = layer.dataProvider().addAttributes([QgsField(u'Status', QVariant.Int)])
                fields['Status'] = len(fields)
                layer.updateFields()
            if layer.selectedFeatureCount() > 0:
                features = layer.selectedFeatures()
                for feat in features:
                    id = feat.id()
                    layer.changeAttributeValue(id, fields['Status'], 9)
                layer.removeSelection()
                self.iface.mapCanvas().refresh()


    def unmarkAsUnsure(self):
        layer = self.iface.legendInterface().currentLayer()
        if layer.isEditable() and layer.type() == QgsMapLayer.VectorLayer:
            fields = {field.name(): id for (id, field) in enumerate(layer.dataProvider().fields())}
            if u'Status' not in fields:
                res = layer.dataProvider().addAttributes([QgsField(u'Status', QVariant.Int)])
                fields['Status'] = len(fields)
                layer.updateFields()
            if layer.selectedFeatureCount() > 0:
                features = layer.selectedFeatures()
                for feat in features:
                    id = feat.id()
                    layer.changeAttributeValue(id, fields['Status'], None)
                layer.removeSelection()
                self.iface.mapCanvas().refresh()

    def markAsDone(self):
        layer = self.iface.legendInterface().currentLayer()
        if layer.isEditable() and layer.type() == QgsMapLayer.VectorLayer:
            fields = {field.name(): id for (id, field) in enumerate(layer.dataProvider().fields())}
            if u'Status' not in fields:
                res = layer.dataProvider().addAttributes([QgsField(u'Status', QVariant.Int)])
                fields['Status'] = len(fields)
                layer.updateFields()
            if layer.selectedFeatureCount() > 0:
                features = layer.selectedFeatures()
                for feat in features:
                    id = feat.id()
                    layer.changeAttributeValue(id, fields['Status'], 1)
                layer.removeSelection()
                self.iface.mapCanvas().refresh()
