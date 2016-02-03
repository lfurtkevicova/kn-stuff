# -*- coding: utf-8 -*-
"""
/***************************************************************************
 skkn_tool
                                 A QGIS plugin
 This plugin helps users to use Slovak cadastral data.
                             -------------------
        begin                : 2016-02-03
        copyright            : (C) 2016 by Marcel Dancak, Ludmila Furtkevicova, Peter Hyben, Ivan Mincik
        email                : ludmilafurtkevicov@gmail.com
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
    """Load skkn_tool class from file skkn_tool.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .skkn_tool import skkn_tool
    return skkn_tool(iface)
