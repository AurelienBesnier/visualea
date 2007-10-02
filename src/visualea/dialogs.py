# -*- python -*-
#
#       OpenAlea.Visualea: OpenAlea graphical user interface
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#
#       Distributed under the CeCILL v2 License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
QT4 Main window 
"""

__license__= "CeCILL v2"
__revision__=" $Id$ "


from PyQt4 import QtCore, QtGui
from openalea.core.compositenode import CompositeNodeFactory
from openalea.core.pkgmanager import PackageManager
from openalea.core.settings import Settings, get_userpkg_dir
from openalea.core.interface import *
from openalea.core.session import Session

import ui_newgraph
import os
import ui_tofactory
import ui_newpackage
import ui_preferences
import ui_ioconfig
import ui_tableedit



class NewGraph(QtGui.QDialog, ui_newgraph.Ui_NewGraphDialog) :
    """ New network dialog """
    
    def __init__(self, title, pmanager, parent=None,
                 factory=None, io=True, inputs=(), outputs=()):
        """
        Constructor
        pmanager : the package manager
        factory : if not None, activate edition mode
        io : provide io config
        inputs and output are default inputs and output
        """
        
        QtGui.QDialog.__init__(self, parent)
        ui_newgraph.Ui_NewGraphDialog.__init__(self)
        self.setWindowTitle(title)

        self.setupUi(self)

        self.factory = factory # edition mode

        packages = pmanager.get_user_packages()

        pkgstr = []
        self.pkgmap = {}
        
        for p in packages:
            pkgstr.append(p.name)
            self.pkgmap[p.name] = p

        
        if(factory): # Edition mode
            self.packageBox.addItem(factory.package.name)
            self.packageBox.setEnabled(False)
            self.inputs = factory.inputs
            self.outputs = factory.outputs
            self.nameEdit.setText(factory.name)
            self.descriptionEdit.setText(factory.description)

        else:
            self.packageBox.addItems(pkgstr)

            self.inputs = inputs
            self.outputs = outputs

                
        self.categoryEdit.addItems(pmanager.category.keys())
        self.ioButton.setVisible(io)
        self.connect(self.ioButton, QtCore.SIGNAL("clicked()"), self.edit_io)

        

    def accept(self):
        
        # Test if name is correct
        name = str(self.nameEdit.text())
        if(not name or
           (not self.factory and self.get_package().has_key(name)) or
           (self.factory and self.factory.name != name and 
            self.get_package().has_key(name))
           ):
            mess = QtGui.QMessageBox.warning(self, "Error",
                                            "The Name is already use")
            return
        
        QtGui.QDialog.accept(self)


    def edit_io(self):
        """ Open IO Config Dialog """

        dialog = IOConfigDialog(self.inputs, self.outputs, parent=self)
        ret = dialog.exec_()

        if(ret):
            self.inputs = dialog.inputs
            self.outputs = dialog.outputs
            

    def get_package(self):
        """ Return the selected package """

        pkgstr = str(self.packageBox.currentText().toAscii())
        return self.pkgmap[pkgstr]


    def get_data(self):
        """
        Return the dialog data in a tuple
        (name, nin, nout, category, description)
        """

        name = str(self.nameEdit.text())
        category = str(self.categoryEdit.currentText().toAscii())
        description = str(self.descriptionEdit.text().toAscii())
        
        return (name, self.get_package(), category, description)



    def create_cnfactory(self, pkgmanager):
        """ Create, register and return a new CompositeNodeFactory """
        
        (name, pkg, cat, desc) = self.get_data()

        newfactory = pkg.create_user_compositenode( name=name,
                                                    description= desc,
                                                    category = cat,
                                                    inputs=self.inputs,
                                                    outputs=self.outputs,
                                                    )
                
        pkgmanager.add_package(pkg)

        return newfactory


    def create_nodefactory(self, pkgmanager):
        """ Create, register and return a NodeFactory """

        (name, pkg, cat, desc) = self.get_data()

        ret = pkg.create_user_node(name=name,
                                   description=desc,
                                   category=cat,
                                   inputs=self.inputs,
                                   outputs=self.outputs,
                                   )
            
        pkgmanager.add_package(pkg)

        return ret


    def update_factory(self):
        """ Update factory with value """
        (name, pkg, cat, desc) = self.get_data()

        factory = self.factory
        if(not factory) : return
        
        oldname = factory.name
        factory.name = name
        factory.category = cat
        factory.description = desc
        factory.inputs = self.inputs
        factory.outputs = self.outputs
        
        factory.package.update_factory(oldname, factory)
    




class NewPackage(QtGui.QDialog, ui_newpackage.Ui_NewPackageDialog) :
    """ New package dialog """
    
    def __init__(self, pkgs, name="", parent=None):
        """ pkgs : list of existing package name """
        
        QtGui.QDialog.__init__(self, parent)
        ui_newpackage.Ui_NewPackageDialog.__init__(self)
        self.setupUi(self)

        self.pkgs = pkgs
        self.connect(self.pathButton, QtCore.SIGNAL("clicked()"), self.path_clicked)

        #self.pathEdit.setText(get_userpkg_dir())


    def path_clicked(self):

        # Test Path
        path = str(self.pathEdit.text())
        result = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory", path)
    
        if(result):
            self.pathEdit.setText(result)
        

    def accept(self):

        # Test if name is correct
        name = str(self.nameEdit.text())
        if(not name or name in self.pkgs):
            mess = QtGui.QMessageBox.warning(self, "Error",
                                            "The Name is already use")
            return

        # Test Path
        path = str(self.pathEdit.text())
        if(path and not os.path.isdir(path)):
            mess = QtGui.QMessageBox.warning(self, "Error",
                                             "Invalid Path")
            return

        QtGui.QDialog.accept(self)


    def get_data(self):
        """
        Return a tuple (name, metainfo, path)
        metainfo is a dictionnary
        """
        name = str(self.nameEdit.text())
        path = str(self.pathEdit.text())
        metainfo = dict(
            description=str(self.descriptionEdit.text()),
            version=str(self.versionEdit.text()),
            license=str(self.licenseEdit.text()),
            authors=str(self.authorsEdit.text()),
            institutes=str(self.institutesEdit.text()),
            url=str(self.urlEdit.text()),
            )
        
        return (name, metainfo, path)



class EditPackage(QtGui.QDialog, ui_newpackage.Ui_NewPackageDialog) :
    """ Edit package dialog """
    
    def __init__(self, package, parent=None):
        """ package : package object to edit """
        
        QtGui.QDialog.__init__(self, parent)
        ui_newpackage.Ui_NewPackageDialog.__init__(self)
        self.setupUi(self)

        path = None
        if(hasattr(package, "path")):
           path = package.path
         
        self.pathButton.setVisible(False)
        self.nameEdit.setEnabled(False)
        self.pathEdit.setEnabled(False)
        
        self.set_data(package.name, path, package.metainfo)
        self.package = package
        

    def accept(self):

        metainfo = dict(
            description=str(self.descriptionEdit.text()),
            version=str(self.versionEdit.text()),
            license=str(self.licenseEdit.text()),
            authors=str(self.authorsEdit.text()),
            institutes=str(self.institutesEdit.text()),
            url=str(self.urlEdit.text()),
            )
        
        self.package.metainfo.update(metainfo)
        if(hasattr(self.package, 'write')):
           self.package.write()           
        
        QtGui.QDialog.accept(self)


    def set_data(self, name, path, metainfo):
        """ Set the dialog data """

        self.nameEdit.setText(name)
        if(path):
            self.pathEdit.setText(path)
        
        self.descriptionEdit.setText(metainfo.get('description', ''))
        self.versionEdit.setText(metainfo.get('version', ''))
        self.licenseEdit.setText(metainfo.get('license', ''))
        self.authorsEdit.setText(metainfo.get('authors', ''))
        self.institutesEdit.setText(metainfo.get('institutes', ''))
        self.urlEdit.setText(metainfo.get('url', ''))
               


class FactorySelector(QtGui.QDialog, ui_tofactory.Ui_FactorySelector) :
    """ New package dialog """
    
    def __init__(self, default_factory=None, parent=None):
        """
        default_factory : default choice
        """
        
        QtGui.QDialog.__init__(self, parent)
        ui_tofactory.Ui_FactorySelector.__init__(self)
        self.setupUi(self)

        self.pkgmanager = PackageManager()
        self.factorymap = {}
        
        cfactories = []
        # Get all composite node factories in writable packages
        for pkg in self.pkgmanager.get_user_packages():
            for f in pkg.values():
                if(isinstance(f, CompositeNodeFactory)):
                   cfactories.append(f.name)
                   self.factorymap[f.name] = f

        self.comboBox.addItems(cfactories)

        if(default_factory):
            i = self.comboBox.findText(default_factory.name)
            self.comboBox.setCurrentIndex(i)

        self.connect(self.newFactoryButton, QtCore.SIGNAL("clicked()"), self.new_factory)


    def accept(self):

        # Test if name is correct
        text = self.comboBox.currentText()
        if(not text):
            mess = QtGui.QMessageBox.warning(self, "Error",
                                            "Invalid Choice.")
            return

        QtGui.QDialog.accept(self)


    def new_factory(self):

        dialog = NewGraph("New Composite Node", self.pkgmanager, self, io=False)
        ret = dialog.exec_()

        if(ret>0):
            newfactory = dialog.create_cnfactory(self.pkgmanager)
            self.comboBox.addItem(newfactory.name)
            self.factorymap[newfactory.name] = newfactory
            i = self.comboBox.findText(newfactory.name)
            self.comboBox.setCurrentIndex(i)
        

    def get_factory(self):
        """ Return the selected factory """

        text = self.comboBox.currentText()
        return self.factorymap[str(text)]

        
   


class PreferencesDialog(QtGui.QDialog, ui_preferences.Ui_Preferences) :
    """ Preferences dialog """
    
    def __init__(self, parent):
        
        QtGui.QDialog.__init__(self, parent)
        ui_preferences.Ui_Preferences.__init__(self)
        self.setupUi(self)

        # Read config
        config = Settings()
        self.session = parent.session

        # pkgmanager
        try:
            str = config.get("pkgmanager", "path")
            l = eval(str)
            
            for p in l:
                self.pathList.addItem(p)
        except:
            pass

        # UI
        try:
            str = config.get("UI", "DoubleClick")
            l = eval(str)
            if("run" in l and "open" in l):
                self.dbclickBox.setCurrentIndex(0)
            elif("run" in l):
                self.dbclickBox.setCurrentIndex(1)
            elif("open" in l):
                self.dbclickBox.setCurrentIndex(2)
        except:
            pass

        try:
            self.edge_style = config.get("UI", "EdgeStyle")
            if(self.edge_style == "Line"):
                self.comboBox.setCurrentIndex(0)
            elif(self.edge_style == "Polyline"):
                self.comboBox.setCurrentIndex(1)
            elif(self.edge_style == "Spline"):
                self.comboBox.setCurrentIndex(2)
        except:
            self.edge_style = "Line"

        # Dataflow
        try:
            str = config.get("eval", "type")
            str = str.strip('"')
            eval_algo = str.strip("'")
        except:
            eval_algo = "SelectiveEvaluation"

        self.update_eval_algo(eval_algo)

        self.connect(self.addButton, QtCore.SIGNAL("clicked()"), self.add_search_path)
        self.connect(self.removeButton, QtCore.SIGNAL("clicked()"), self.remove_search_path)


    def add_search_path(self):
        """ Package Manager : Add a path in the list """
        result = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory")
    
        if(result):
            self.pathList.addItem(result)


    def update_eval_algo(self, algo_str):
        """ Search available evaluation algorithm
        and select algo_str """

        import openalea.core.algo.dataflow_evaluation as evalmodule
        
        # Search class obj in module
        l = lambda x: isinstance(x, type) and evalmodule.AbstractEvaluation in x.mro()
        classlist = filter(l, evalmodule.__dict__.values())
        classlist.remove(evalmodule.AbstractEvaluation)
        
        selectitem = None
        for c in classlist:
            try:
                item = QtGui.QListWidgetItem(c.__name__)
                self.listAlgo.addItem(item)
                if(c.__name__ == algo_str):
                    selectitem = item
            except:
                pass
            
        if(selectitem):
            self.listAlgo.setCurrentItem(selectitem)


    def remove_search_path(self):
        """ Package Manager : Remove a path in the list """

        row = self.pathList.currentRow()
        self.pathList.takeItem(row)
        

    def valid_search_path(self):
        """ Set the search path in the package manager """

        pkgmanager = PackageManager()
        pkgmanager.set_default_wraleapath()
        for i in xrange(self.pathList.count()):
            path = self.pathList.item(i).text()
            pkgmanager.add_wraleapath(os.path.abspath(str(path)))

        pkgmanager.write_config()


    def valid_ui(self):
        """ Valid UI Parameters """

        d = [["run", "open"], ["run"], ["open"],]
        index = self.dbclickBox.currentIndex()

        styles = ["Line", "Polyline", "Spline"]
        edge_style_index = self.comboBox.currentIndex()
        edge_style = styles[edge_style_index]
        
        config = Settings()
        config.set("UI", "DoubleClick", repr(d[index]))
        config.set("UI", "EdgeStyle", edge_style)
        config.write_to_disk()

        if edge_style != self.edge_style:
            self.edge_style = edge_style
            session = self.session
            session.notify_listeners()
            ws = session.workspaces
            for cn in ws:
                cn.notify_listeners(('graph_modified',))


    def valid_dataflow(self):

        item = self.listAlgo.currentItem()
        if(item):
            algostr = str(item.text())
        
            config = Settings()
            config.set("eval", "type", algostr)
            config.write_to_disk()
          

    def accept(self):

        self.valid_search_path()
        self.valid_ui()
        self.valid_dataflow()
        QtGui.QDialog.accept(self)



class ComboDelegate(QtGui.QItemDelegate):


    def get_interfaces(self):
        """ Return the list of availble interfaces """

        x =  [k.__name__ for k in IInterfaceMetaClass.all]
        x.append('None')
        return x
        

    
    def createEditor(self, parent, option, index):
        """ Create the editor """
        if index.column() == 1:
            editor = QtGui.QComboBox(parent)
            editor.addItems(self.get_interfaces())
            return editor

        return QtGui.QItemDelegate.createEditor(self, parent, option, index)

    
    def setEditorData(self ,editor, index):
        """ Accessor """
        value = str(index.data().toString())
        i = editor.findText(value)
        editor.setCurrentIndex (i)


    def setModelData(self, editor, model, index):
        """ Accessor """
        value = editor.currentText()
        model.setItem(index.row(), index.column(),
                      QtGui.QStandardItem(str(value)))


class IOConfigDialog(QtGui.QDialog, ui_ioconfig.Ui_IOConfig) :
    """ IO Configuration dialog """
    
    def __init__(self, inputs=(), outputs=(), parent=None):
        """ node : the node IO to edit """
        
        QtGui.QDialog.__init__(self, parent)
        ui_ioconfig.Ui_IOConfig.__init__(self)
        self.setupUi(self)
        delegate = ComboDelegate()
        self.__delegate = delegate

        self.inputs = inputs
        self.outputs = outputs
        
        self.inModel = QtGui.QStandardItemModel(len(inputs), 2)
        self.inModel.setHorizontalHeaderLabels(["Name", "Interface"])
        self.inTable.setModel(self.inModel)

        self.inTable.setItemDelegate(delegate)

        self.outModel = QtGui.QStandardItemModel(len(outputs), 2)
        self.outModel.setHorizontalHeaderLabels(["Name", "Interface"])
        self.outTable.setModel(self.outModel)
        
        self.outTable.setItemDelegate(delegate)

        #self.inTable.setItemDelegateForColumn(1, ComboBoxDeletegate())
                                                      
        for i, d in enumerate(inputs):
            self.inModel.setItem(i, 0, QtGui.QStandardItem(str(d['name'])))
            self.inModel.setItem(i, 1, QtGui.QStandardItem(str(d['interface'])))


        for i, d in enumerate(outputs):
            self.outModel.setItem(i, 0, QtGui.QStandardItem(str(d['name'])))
            self.outModel.setItem(i, 1, QtGui.QStandardItem(str(d['interface'])))


        self.connect(self.addInput, QtCore.SIGNAL("clicked()"), self.add_input)
        self.connect(self.delInput, QtCore.SIGNAL("clicked()"), self.del_input)
        self.connect(self.addOutput, QtCore.SIGNAL("clicked()"), self.add_output)
        self.connect(self.delOutput, QtCore.SIGNAL("clicked()"), self.del_output)


    def accept(self):
        """ Valid IO """

        # build input dict
        self.inputs = []
        c = self.inModel.rowCount()
        for i in xrange(c):
            name = str(self.inModel.item(i,0).text())
            interface_str = str(self.inModel.item(i,1).text())

            try:
                interface = eval(interface_str)
            except:
                interface = None
            self.inputs.append(dict(name=name, interface=interface))
            

        # build output dict
        self.outputs = []
        c = self.outModel.rowCount()
        for i in xrange(c):
            name = str(self.outModel.item(i,0).text())
            interface_str = str(self.outModel.item(i,1).text())
            try:
                interface = eval(interface_str)
            except:
                interface = None
            self.outputs.append(dict(name=name, interface=interface))
        
        QtGui.QDialog.accept(self)


    def add_input(self):
        c = self.inModel.rowCount()
        self.inModel.appendRow([QtGui.QStandardItem('IN%i'%(c+1,)),
                                QtGui.QStandardItem('None')])


    def add_output(self):
        c = self.outModel.rowCount()
        self.outModel.appendRow([QtGui.QStandardItem('OUT%i'%(c+1,)),
                                QtGui.QStandardItem('None')])

        
    def del_input(self):
        c = self.inModel.rowCount()
        self.inModel.takeRow(c-1)


    def del_output(self):
        c = self.outModel.rowCount()
        self.outModel.takeRow(c-1)
        

class DictEditor(QtGui.QDialog, ui_tableedit.Ui_TableEditor):
    """
    Dictionnary editor (used for node internals)
    If accepted :
      self.pdict contains the modified dictionary
      self.modified_key  contains the list of modified key
    """
    
    def __init__(self, pdict, parent):

        QtGui.QDialog.__init__(self, parent)
        ui_tableedit.Ui_TableEditor.__init__(self)
        self.setupUi(self)

        self.pdict = pdict.copy() # copy the dictionary
        self.modified_key = [] # list of modified key

        # Fill the table
        self.tableWidget.setRowCount(len(pdict.keys()))
        for (i, (k,v)) in enumerate(pdict.items()):

            item = QtGui.QTableWidgetItem(str(k))
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(i, 0, item)
            self.tableWidget.setItem(i, 1, QtGui.QTableWidgetItem(str(v)))
        
        
    def accept(self):

        # Check for modification in each row
        for (i, (k,v)) in enumerate(self.pdict.items()):
            keyitem = self.tableWidget.item(i, 0)
            valueitem = self.tableWidget.item(i, 1)

            if(str(keyitem.text()) != str(k)): continue
            s = str(valueitem.text())
            if(s != str(v)):
                
                self.modified_key.append(k)
                try:
                    self.pdict[k] = eval(s)
                except:
                    self.pdict[k] = s
                    
        QtGui.QDialog.accept(self)


class ShowPortDialog(QtGui.QWidget):
    """
    Port show status onfiguration dialog
    """


   
