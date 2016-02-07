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
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QMessageBox
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from skkn_tool_dialog import skkn_toolDialog
import os.path
from db_manager.db_plugins import createDbPlugin
import subprocess


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

        # data
        self.dlg.lineData.clear()
        self.dlg.buttonData.clicked.connect(self.select_data)
        
        # database and schema
        self.dlg.comboBox_2.currentIndexChanged.connect(self.db_changed)

        # conversation
        self.dlg.buttonConvert.clicked.connect(self.convertData)
        
        # about message
        self.dlg.buttonAbout.clicked.connect(self.showError)

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

    def select_data(self):
        self.foldername = QFileDialog.getExistingDirectory(self.dlg, "Select data folder (*.vgi data, *.dbf data, outputs)","/home/ludka/Desktop/data")
        self.dlg.lineData.setText(self.foldername)

    def convertData(self):
        #self.dlg.textEditData.setText(self.foldername)

        bashCommand = "source convert.sh"
        os.system(bashCommand)
        
        #subprocess.call('source convert.sh')

    def db_changed(self,index): 
        self.dlg.comboBox_3.clear()
        self.dlg.comboBox_3.addItems(self.db_getSchema(index))

    def db_getSchema(self,index):
        schemas = []        
        c = self.dbconnections[index]        
        c.connect()     
        for schema in c.database().schemas():
                schemas.append(schema.name)
        return schemas

    def showError(self):
        mes = QMessageBox.about(None,"About SKKN Plugin","This tool helps users to use Slovak land \
registry data (cadastral data) in exchange formats created by The Geodesy, Cartography and \
Cadastre Authority of Slovak republic, in QGIS. \nIt is only usefull and dedicated for processing \
in Slovak republic for people having access to Cadastre data. \nThere is no reason to use it for \
other purposes.")

    def run(self):

        # add connections to combobox       
        self.dlg.comboBox_2.clear()        
        dbpluginclass = createDbPlugin('postgis')
        
        connection_list = []
        self.dbconnections = dbpluginclass.connections()
        for c in self.dbconnections:
                connection_list.append(unicode(c.connectionName()))
                c.connect()            
        
        self.dlg.comboBox_2.addItems(connection_list)
        dbpluginclass.typeName()
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
