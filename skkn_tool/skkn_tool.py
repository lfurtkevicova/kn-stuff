# -*- coding: utf-8 -*-
"""
/***************************************************************************
 skkn_tool
                                 A QGIS plugin
 This plugin helps users to use Slovak cadastral data.
                              -------------------
        begin                : 2016-02-03
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Ludmila Furtkevicova
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QProcess, QTimer
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QMessageBox
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from skkn_tool_dialog import skkn_toolDialog
import os.path
from db_manager.db_plugins import createDbPlugin
from db_manager.db_plugins.plugin import DbError
from subprocess import call
import sys, time


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
        self.dlg.buttonConvert.setEnabled(False)        
        self.dlg.lineData.clear()
        self.dlg.buttonData.clicked.connect(self.select_data)
        
        
        # database and schema
        # self.dlg.dataBase.setEnabled(False)
        self.dlg.comboBox_2.currentIndexChanged.connect(self.db_changed)

        # conversation
        self.dlg.progressBarData.setMinimum(0)
        self.dlg.progressBarData.setMaximum(100)
        self._active = False
        self.dlg.buttonConvert.clicked.connect(self.convertData)
               
        # ukoncenie konverzie
        self.dlg.buttonKill.clicked.connect(self.stopConvert) 
        self.dlg.buttonKill.setEnabled(False)
        
        # about message
        self.dlg.buttonAbout.clicked.connect(self.showError)
        
        self.dlg.buttonClear.clicked.connect(self.clear)
        
        # nieco ako Popen, nativne pre Qt
        self.process = QProcess(self.dlg)
        self.process.readyRead.connect(self.writeData)
        
        # vytvorenie schemy
        self.dlg.buttonCreateSchema.clicked.connect(self.db_createSchema) 
        
        # vymazanie schemy
        self.dlg.buttonDelete.clicked.connect(self.db_deleteSchema)

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
        # remove the toolbarself.dlg.dataBase.setEnabled(False)
        del self.toolbar

    def select_data(self):
        self.foldername = QFileDialog.getExistingDirectory(self.dlg, "Select data folder (*.vgi data, *.dbf data, outputs)","/home/ludka/Desktop")
        self.dlg.lineData.setText(self.foldername)
        self.buttonConvertName()
        self.dlg.buttonConvert.setEnabled(True)
        self.dlg.progressBarData.setValue(0)
        #self.dlg.dataBase.setEnabled(False)
        self.clear()

    def convertData(self):
        #self.dlg.textEditData.setText(self.foldername)      
        ## spustenie pomocou call a Popen     
        # subprocess.call([os.path.join(self.plugin_dir,'kataster-import','kt-sql'),self.foldername])
        # subprocess.Popen([os.path.join(self.plugin_dir,'kataster-import','kt-sql'),self.foldername],shell = True)
        self.clear()
        self.process.start(os.path.join(self.plugin_dir,'kataster-import','kt-sql'),[self.foldername])
        self.dlg.buttonConvert.setText('Converting ...')
        self.dlg.buttonKill.setEnabled(True)
       
    #funkcia na zapisovanie do GUI okna, vola funkciu insertText    
    def writeData(self):
        text=str(self.process.readAll())
        for line in text.splitlines(): 
            if len(line)==0:
                continue
            if not line.startswith('PROGRESS'):            
                self.insertText(line + os.linesep)
            else:
                try:                
                    self.pvalue=int(line.split(':',1)[1].strip())
                except:
                    return                    
                self.dlg.progressBarData.setValue(self.pvalue)
            if self.pvalue==100:
                self.dlg.buttonConvert.setText('Conversation successfully completed')
                self.dlg.buttonConvert.setEnabled(False)                
                self.dlg.buttonKill.setEnabled(False)
                self.dlg.dataBase.setEnabled(True)
                      
    def insertText(self,text):
        cursor = self.dlg.textEditData.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.dlg.textEditData.ensureCursorVisible()

    def stopConvert(self):
        self.process.kill()
        self.clear()
        self.insertText('Conversation interrupted!')
        self.buttonConvertName()        
        self.dlg.buttonKill.setEnabled(False)
        self.dlg.progressBarData.setValue(0)

    def buttonConvertName(self):
        self.dlg.buttonConvert.setText('Convert all data')

    def db_changed(self,index): 
        self.dlg.comboBox_3.clear()
        self.clear()
        self.dlg.comboBox_3.addItems(self.db_getSchema(index))

    # naplnenie comboboxu schemami
    def db_getSchema(self,index):
        schemas = []        
        self.dbconn = self.dbconnections[index]        
        self.dbconn.connect() 
        
        # zabraniene zobrazeniu schem public a topology
        for schema in self.dbconn.database().schemas():
            if schema.name in ('public','topology'):
                continue
            schemas.append(schema.name)
        return schemas
    
    # vytvorenie novej schemy kataster
    def db_createSchema(self):
        self.clear()        
        db = self.dlg.comboBox_2.currentText() 
        sch = self.dlg.comboBox_3.currentText()
        if not sch =='kataster': 
            s = os.path.join(self.plugin_dir,'kataster-import','kt-vytvor_db')+' | '+'psql'+ ' ' +db        
            g_u = os.path.join(self.foldername,'sql','graficke_udaje.sql')
            p_u = os.path.join(self.foldername,'sql','popisne_udaje.sql')
            glogdir = os.path.join(self.plugin_dir,'kataster-import','info_g.log')
            plogdir = os.path.join(self.plugin_dir,'kataster-import','info_p.log')         
            gslog = os.path.join(self.plugin_dir,'kataster-import','PGOPTIONS="-c search_path=kataster,public" psql kataster -f ' + g_u + '2>' + glogdir)
            pslog = os.path.join(self.plugin_dir,'kataster-import','PGOPTIONS="-c search_path=kataster,public" psql kataster -f '+ p_u + '2>' + plogdir)        
            testdir = os.path.join(self.plugin_dir,'kataster-import','katastertools','sql','test-import.sql')                     
            test = os.path.join(self.plugin_dir,'kataster-import','PGOPTIONS="-c search_path=kataster,public" psql kataster -f ' + testdir)             
            call(s,shell=True)
            call(gslog,shell=True)
            call(pslog,shell=True)
            call(test,shell=True)
            self.writeLog()
        else:
            self.insertText('Schema already exists.')
        
    #funkcia na výpis log do GUI pri tvorbe schemy   
    def writeLog(self):
        gfilelog =  os.path.join(self.plugin_dir,'kataster-import','info_g.log')
        gtext=open(gfilelog).read()
        pfilelog =  os.path.join(self.plugin_dir,'kataster-import','info_p.log')
        ptext=open(pfilelog).read()
        
        self.insertText('New schema "kataster" and related SQL statements has been created successfully. To see schema in combo box refresh database connection!\n\n')
        self.insertText('GRAPHICAL DATA LOG:\n**********************\n')
        for line in gtext.splitlines(): 
            if len(line)==0:
                self.insertText('No message.')
            else:
                self.insertText(line + os.linesep)
        self.insertText('\nATTRIBUTIVE DATA LOG:\n************************\n')
        for line in ptext.splitlines(): 
            if len(line)==0:
                self.insertText('No message.')
            else:
                self.insertText(line + os.linesep)
       
    # vymazanie schemy    
    def db_deleteSchema(self):
        index = self.dlg.comboBox_3.currentIndex()   
        schema = self.dlg.comboBox_3.currentText()  
        db = self.dbconn.database()

        # vlozenie chybovej hlasky v pripade problemu
        try:    
            db.sqlResultModel('DROP schema {0} CASCADE'.format(schema), db)
        except DbError as e:
            self.insertText(str(e))
        # vymazanie z comboboxu
        self.dlg.comboBox_3.removeItem(index)
        
    def showError(self):
        QMessageBox.about(None,"About SKKN Plugin","This tool helps users to use Slovak land \
registry data (cadastral data) in exchange formats created by The Geodesy, Cartography and \
Cadastre Authority of Slovak republic, in QGIS. \nIt is only usefull and dedicated for processing \
in Slovak republic for people having access to Cadastre data. \nThere is no reason to use it for \
other purposes.")

    def clear(self): 
            self.dlg.textEditData.clear()

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
