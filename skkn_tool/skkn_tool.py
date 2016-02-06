# -*- coding: utf-8 -*-
"""
/***************************************************************************
 skkn_tool
                                 A QGIS plugin
 This plugin helps users to use Slovak cadastral data.
                              -------------------
        begin                : 2016-02-03
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Marcel Dancak, Ludmila Furtkevicova, Peter Hyben, Ivan Mincik
        email                : ludmilafurtkevicov@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from skkn_tool_dialog import skkn_toolDialog
import os.path

from qgis.core import *
from db_manager.db_plugins import createDbPlugin
from db_manager.dlg_db_error import DlgDbError


class skkn_tool:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'skkn_tool_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = skkn_toolDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&SKKN tool')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'skkn_tool')
        self.toolbar.setObjectName(u'skkn_tool')

        # SGI
        self.dlg.lineSGI.clear()
        self.dlg.buttonSGI.clicked.connect(self.select_SGI)
        
        # SGI
        self.dlg.lineSPI.clear()
        self.dlg.buttonSPI.clicked.connect(self.select_SPI)

        # vystup
        self.dlg.lineEdit.clear()
        self.dlg.toolButton.clicked.connect(self.select_output_folder)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('skkn_tool', message)


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
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/skkn_tool/icons/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'SKKN tool'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&SKKN tool'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_SGI(self):
        foldername = QFileDialog.getExistingDirectory(self.dlg, "Select folder with SGI data","")
        self.dlg.lineSGI.setText(foldername)
        
    def select_SPI(self):
        foldername = QFileDialog.getExistingDirectory(self.dlg, "Select folder with SPI data","")
        self.dlg.lineSPI.setText(foldername)

    def select_output_folder(self):
        foldername = QFileDialog.getExistingDirectory(self.dlg, "Select output folder ","")
        self.dlg.lineEdit.setText(foldername)

    def run(self):

        # add connections to combobox       
        dbpluginclass = createDbPlugin('postgis')
        connection_list = []
        for c in dbpluginclass.connections():
                connection_list.append(unicode(c.connectionName()))
        self.dlg.comboBox_2.addItems(connection_list)
        
#        db = unicode(self.dlg.comboBox_2.currentText())
#        schema_list = []
#        for s in db.schema():
#            schema_list.append(unicode(s.schemaName()))                     
#        self.dlg.comboBox_3.addItems(schema_list)
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
