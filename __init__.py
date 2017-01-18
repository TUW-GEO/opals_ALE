# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ALE
                                 A QGIS plugin
 Adds line editing tools (segment deletion, ...)
                             -------------------
        begin                : 2017-01-18
        copyright            : (C) 2017 by lwiniwar/TU Wien
        email                : lukas.winiwarter@geo.tuwien.ac.at
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ALE class from file ALE.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .advanced_line_editor import ALE
    return ALE(iface)
