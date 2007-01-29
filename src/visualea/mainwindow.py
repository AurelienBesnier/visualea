# -*- python -*-
#
#       OpenAlea.Visualea: OpenAlea graphical user interface
#
#       Copyright or (C) or Copr. 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#
#       Distributed under the GPL License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.gnu.org/licenses/gpl.txt
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
QT4 Main window 
"""

__license__= "GPL"
__revision__=" $Id$ "


from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL

import ui_mainwindow
from pycutext import PyCutExt

from node_treeview import PackageTreeView, PkgModel, CategoryModel

import config

from openalea.core.subgraph import SubGraphFactory


class MainWindow(QtGui.QMainWindow, ui_mainwindow.Ui_MainWindow) :

    def __init__(self, pkgman, session, globals=None, parent=None):
        """
        @param pkgman : the package manager
        @param session : user session
        @param globals : python interpreter globals
        @param parent : parent window
        """

        QtGui.QMainWindow.__init__(self, parent)
        ui_mainwindow.Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.pkgmanager = pkgman

        # Array to map tab index with node widget
        self.index_nodewidget = []

        self.tabWorkspace.removeTab(0)

        # python interpreter
        self.interpreterWidget = PyCutExt(locals=globals, parent=self.splitter)

        # package tree view
        self.pkg_model = PkgModel(pkgman)
        self.packageTreeView = PackageTreeView(self, self.packageview)
        self.packageTreeView.setModel(self.pkg_model)
        self.vboxlayout.addWidget(self.packageTreeView)

        # category tree view
        self.cat_model = CategoryModel(pkgman)
        self.categoryTreeView = PackageTreeView(self, self.categoryview)
        self.categoryTreeView.setModel(self.cat_model)
        self.vboxlayout1.addWidget(self.categoryTreeView)

        # menu callbacks
        self.connect(self.action_About, SIGNAL("activated()"), self.about)
        self.connect(self.actionOpenAlea_Web, SIGNAL("activated()"), self.web)
        self.connect(self.action_Help, SIGNAL("activated()"), self.help)
        self.connect(self.action_Quit, SIGNAL("activated()"), self.quit)
        self.connect(self.action_Close_current_workspace, SIGNAL("activated()"),
                     self.close_workspace)
        self.connect(self.action_Auto_Search, SIGNAL("activated()"), self.find_wralea)
        self.connect(self.action_Add_File, SIGNAL("activated()"), self.add_wralea)
        self.connect(self.action_Run, SIGNAL("activated()"), self.run)
        self.connect(self.tabWorkspace, SIGNAL("contextMenuEvent(QContextMenuEvent)"),
                     self.contextMenuEvent)
        self.connect(self.action_Execute_script, SIGNAL("activated()"),
                     self.exec_python_script)
        self.connect(self.action_New_Network, SIGNAL("activated()"),
                     self.new_graph)

        self.connect(self.action_New_Session, SIGNAL("activated()"), self.new_session)
        self.connect(self.action_Open_Session, SIGNAL("activated()"), self.open_session)
        self.connect(self.action_Save_Session, SIGNAL("activated()"), self.save_session)
        self.connect(self.actionSave_as, SIGNAL("activated()"), self.save_as)


        # final init
        self.session = session
        workspace_factory = self.session.user_pkg['Workspace']
        node = self.session.add_workspace(workspace_factory)
        self.open_widget_tab(workspace_factory, node)


    def about(self):
        """ Display About Dialog """
        
        mess = QtGui.QMessageBox.about(self, "About Visualea",
                                       "Version %s\n\n"%(config.version) +
                                       "VisuAlea is part of the OpenAlea framework.\n"+
                                       u"Copyright \xa9  2006 INRIA - CIRAD - INRA\n"+
                                       "This Software is distributed under the GPL License.\n\n"+
                                       
                                       "Visit http://openalea.gforge.inria.fr\n\n"
                                       )

    def help(self):
        """ Display help """
        self.web()

    def web(self):
        """ Open OpenAlea website """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(config.url))


    def quit(self):
        """ Quit Application """

        self.close()
        

    def closeEvent(self, event):
        """ Close All subwindows """
        
        for i in range(self.tabWorkspace.count()):
            w = self.tabWorkspace.widget(i)
            w.close()
        event.accept()


    def reinit_treeview(self):
        """ Reinitialise package and category views """

        self.cat_model.reset()
        self.pkg_model.reset()
        

    def close_workspace(self):
        """ Close current workspace """

        cindex = self.tabWorkspace.currentIndex()
        # Update session
        factory = self.index_nodewidget[cindex].node.factory
        self.session.close_workspace(factory)

        self.close_tab_workspace(cindex)
        

    def close_tab_workspace(self, cindex):
        """ Close workspace indexed by cindex cindex is Node"""
        
        w = self.tabWorkspace.widget(cindex)
        self.tabWorkspace.removeTab( cindex )
        w.close()
        w.emit(QtCore.SIGNAL("close()"))
        
        self.index_nodewidget[cindex].release_listeners()
        del(self.index_nodewidget[cindex])


    def update_tabwidget(self):
        """ open tab widget """

        # open tab widgets
        for (factory, node) in self.session.workspaces.items():
            self.open_widget_tab(factory, node)

        # Close unnecessary tab
        for i in range(len(self.index_nodewidget)-1, -1, -1):
            widget = self.index_nodewidget[i]
            f = widget.node.factory
            if(not self.session.workspaces.has_key(f)):
                self.close_tab_workspace(i)



    def open_widget_tab(self, factory, node = None, caption=None):
        """
        Open a widget in a tab giving the factory and an instance
        if node is null, a new instance is allocated
        caption is append to the tab title
        """
        
        # Test if the node is already opened
        for i in range(len(self.index_nodewidget)):
            widget = self.index_nodewidget[i]
            f = widget.node.factory
            if(factory == f):
                self.tabWorkspace.setCurrentIndex(i)
                return

        container = QtGui.QWidget(self)
        container.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        widget = factory.instantiate_widget(node, parent=container, edit=True)
        widget.wcaption = caption
        widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        vboxlayout = QtGui.QVBoxLayout(container)
        vboxlayout.addWidget(widget)

        if(not caption) : caption = factory.get_id()
        
        index = self.tabWorkspace.addTab(container, caption)
        self.tabWorkspace.setCurrentIndex(index)
        self.index_nodewidget.append(widget)

        return index
        

    def add_wralea(self):

        filename = QtGui.QFileDialog.getOpenFileName(self, "Add Wralea")
        self.pkgmanager.add_wralea(str(filename))
        self.reinit_treeview()

    
    def find_wralea(self):

        self.pkgmanager.find_and_register_packages()
        self.reinit_treeview()

    
    def run(self):
        """ Run the active workspace """

        cindex = self.tabWorkspace.currentIndex()
        w = self.tabWorkspace.widget(cindex)

        self.index_nodewidget[cindex].node.eval()


    def contextMenuEvent(self, event):
        """ Context menu event : Display the menu"""

        pos = self.tabWorkspace.mapFromGlobal(event.globalPos())
        
        tabBar = self.tabWorkspace.tabBar()
        count = tabBar.count()

        index = -1
        for i in range(count):
            if(tabBar.tabRect(i).contains(pos)):
                index = i
                break

        # if no bar was hit, return
        if (index<0) :  return 

        # set hitted bar to front
        self.tabWorkspace.setCurrentIndex(index)
        
        menu = QtGui.QMenu(self)

        action = menu.addAction("Close")
        self.connect(action, SIGNAL("activated()"), self.close_workspace)

        menu.move(event.globalPos())
        menu.show()


    def new_graph(self):
        """ Create a new graph """

        # Get default package
        pkg = self.session.user_pkg

        dialog = NewGraph(pkg)
        ret = dialog.exec_()

        if(ret>0):
            (name, nin, nout, cat, desc) = dialog.get_data()

            newfactory = SubGraphFactory(self.pkgmanager, name=name,
                                         description= desc,
                                         category = cat,
                                         documentation = ""
                                         )
            
            newfactory.set_numinput(nin)
            newfactory.set_numoutput(nout)
            
            pkg.add_factory(newfactory)
            self.pkgmanager.add_package(pkg)

            self.reinit_treeview()

            node = self.session.add_workspace(newfactory)
            self.open_widget_tab(newfactory, node)
        

    def exec_python_script(self):
        """ Choose a python source and execute it """
            
        filename = QtGui.QFileDialog.getOpenFileName(
            self, "Python Script", "Python script (*.py)")

        filename = str(filename)
        if(not filename) : return
        
        file = open(filename, 'r')
        sources = file.read()
        self.interpreterWidget.get_interpreter().runsource(sources, str(filename))


    def new_session(self):

        self.session.clear()
        self.session.add_workspace(self.session.user_pkg['Workspace'])
        self.update_tabwidget()
        self.reinit_treeview()

        
    def open_session(self):

        filename = QtGui.QFileDialog.getOpenFileName(
            self, "OpenAlea Session", QtCore.QDir.homePath(), "XML file (*.xml)")

        filename = str(filename)
        if(not filename) : return

        self.session.load(filename)
        self.update_tabwidget()
        self.reinit_treeview()

        
    def save_session(self):

        if(not self.session.session_filename):
            self.save_as()
        self.session.save(self.session.session_filename)

        
    def save_as(self):

        filename = QtGui.QFileDialog.getSaveFileName(
            self, "OpenAlea Session",  QtCore.QDir.homePath(), "XML file (*.xml)")

        filename = str(filename)
        if(not filename) : return

        self.session.save(filename)


        
       

import ui_newgraph

class NewGraph(  QtGui.QDialog, ui_newgraph.Ui_NewGraphDialog) :
    """ New network dialog """
    
    def __init__(self, package, parent=None):
        """
        Constructor
        @param pacakge : the package the graph will be added to
        """

        QtGui.QDialog.__init__(self, parent)
        ui_newgraph.Ui_NewGraphDialog.__init__(self)
        self.setupUi(self)

        self.package = package

    def accept(self):

        # Test if name is correct
        name = str(self.nameEdit.text())
        if(self.package.has_key(name)):
            mess = QtGui.QMessageBox.warning(self, "Error",
                                            "The Name is already use")
            return

        
        QtGui.QDialog.accept(self)


    def get_data(self):
        """
        Return the dialog data in a tuple
        (name, nin, nout, category, description)
        """

        name = str(self.nameEdit.text())
        category = str(self.categoryEdit.text().toAscii())
        description = str(self.categoryEdit.text().toAscii())

        return (name, self.inBox.value(), self.outBox.value(), category, description)
    
        


