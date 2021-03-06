# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 20:24:39 2017

@author: pfduc
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 23:40:40 2014

Copyright (C) 10th april 2015 Pierre-Francois Duc
License: see LICENSE.txt file
"""

import sys
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
from types import MethodType
import logging

from LabTools.Display import QtTools

class ConsoleWidget(QtGui.QWidget):
    """This class is a TextEdit with a few extra features"""

    def __init__(self, parent=None):
        super(ConsoleWidget, self).__init__(parent)

        self.consoleTextEdit = QtGui.QTextEdit()
        self.consoleTextEdit.setReadOnly(True)

        self.verticalLayout = QtGui.QVBoxLayout()

        self.verticalLayout.addWidget(self.consoleTextEdit)
        
        self.setLayout(self.verticalLayout)



    def console_text(self, new_text = None):
        """get/set method for the text in the console"""
        
        if new_text == None:
            
            return str((self.consoleTextEdit.toPlainText())).rstrip()
            
        else:
            
            self.consoleTextEdit.setPlainText(new_text)
        

    def automatic_scroll(self):
        """performs an automatic scroll up
        
        the latest text shall always be in view
        """
        sb = self.consoleTextEdit.verticalScrollBar()
        sb.setValue(sb.maximum())


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain
    
    create a QDock widget and store a reference to the widget
    """    

    mywidget = ConsoleWidget(parent = parent)
    
    #create a QDockWidget
    consoleDockWidget = QtGui.QDockWidget("Output Console", parent)
    consoleDockWidget.setObjectName("consoleDockWidget")
    consoleDockWidget.setAllowedAreas(
        QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        | QtCore.Qt.BottomDockWidgetArea)
        
    #fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['ConsoleWidget'] = mywidget
    
    consoleDockWidget.setWidget(mywidget)
    parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, consoleDockWidget)
    
    #Enable the toggle view action
    parent.windowMenu.addAction(consoleDockWidget.toggleViewAction())


    # redirect print statements to show a copy on "console"
    sys.stdout = QtTools.printerceptor(parent)
    
    parent.update_console = MethodType(update_console, parent, parent.__class__)    
    
    parent.connect(parent, QtCore.SIGNAL(
            "print_to_console(PyQt_PyObject)"), parent.update_console) 


def update_console(parent, stri):
  
    MAX_LINES = 50

    stri = str(stri)
    new_text = parent.widgets['ConsoleWidget'].console_text() + '\n' + stri

    line_list = new_text.splitlines()
    N_lines = min(MAX_LINES, len(line_list))

    new_text = '\n'.join(line_list[-N_lines:])
    parent.widgets['ConsoleWidget'].console_text(new_text)
    
    parent.widgets['ConsoleWidget'].automatic_scroll()




if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    ex = ConsoleWidget()
    ex.show()
    sys.exit(app.exec_())
