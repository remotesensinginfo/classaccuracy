# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ClassAccuracyMain
                                 A QGIS plugin
 Manually review the accuracy of a classification
                             -------------------
        begin                : 2015-08-15
        copyright            : (C) 2015 by Pete Bunting
        email                : pfb@aber.ac.uk
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
    """Load ClassAccuracyMain class from file ClassAccuracyMain.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .rsgisclassacc import ClassAccuracyMain
    return ClassAccuracyMain(iface)
