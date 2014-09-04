# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 14:45:30 2012

@author: rueffer
"""
import time
import numpy as np
#import cv2 as cv
from cv2 import imread
from matplotlib import pylab as plt
from matplotlib.patches import Rectangle,Ellipse,PathPatch
from matplotlib.patches import Path as MPLPath
from matplotlib import transforms as MPLTransforms
from copy import deepcopy
from string import atof,atoi
import autoContact

#===============================================================================
# From there the GUI starts
#===============================================================================

import sys, os
from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import Formatter,NullLocator
from matplotlib.widgets import Cursor
from matplotlib.axes import Axes
import matplotlib.axis as maxis

progname = "APaGe ROM"
progversion = "0.983"
latest_changes="""
0.983  Name changed
"""
#===============================================================================
# ##TODO:
# generally use types of tables to avoid incorrect display    
#     
#===============================================================================
class MyCursor(Cursor):
    def __init__(self,ax,pos,statusBar,transForm,**kwargs):
        Cursor.__init__(self,ax,**kwargs)
        self.statusBar=statusBar
        self.pos=pos
        self.transForm=transForm
        self.statusBar.showMessage("Cell: " +"%d,"%self.pos[0]+"%d"%self.pos[1])
        
    def onmove(self,event):
        if event.inaxes != self.ax:
            self.statusBar.showMessage("Cell: " +"%d,"%self.pos[0]+
                                        "%d"%self.pos[1])
            return
        xy=self.transFunc(np.array([event.xdata, event.ydata]))
        self.statusBar.showMessage("Cell: " +"%d,"%self.pos[0]+"%d"%self.pos[1] +
                                    ", cursor at (rel. cell 0): %.2f,"%xy[0]+"%.2f"%xy[1])

class MPLCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
#    def __init__(self, imageObject, parent=None, width=5, height=4, dpi=100):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.001,right=0.999,top=0.999,bottom=0.001)
        self.axes.xaxis.set_major_locator(NullLocator())
        self.axes.yaxis.set_major_locator(NullLocator())

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    
class endSelector:
    epsilon = 5 # max pixel distance to count as a vertex hit
    
    def __init__(self,parent,index):
        self.parent=parent
        self.canvas = parent.canvas
        self.press=None
        self.p=[]
        invTransForm=self.parent.project.createInverseTransformFunc(index)
        end1=invTransForm(self.parent.project.settings[index]["end1"])
        end2=invTransForm(self.parent.project.settings[index]["end2"])
        pa1=MPLPath([(end1[0],end1[1]),
                     (end1[0]-25,end1[1]),(end1[0],end1[1]),(end1[0]-5,end1[1]),
                     (end1[0],end1[1]+5),(end1[0],end1[1]+25),(end1[0],end1[1]),(end1[0],end1[1]+5),
                     (end1[0]+5,end1[1]),(end1[0]+25,end1[1]),(end1[0],end1[1]),(end1[0]+5,end1[1]),
                     (end1[0],end1[1]-5),(end1[0],end1[1]-25),(end1[0],end1[1]),(end1[0],end1[1]-5),
                     (end1[0]-5,end1[1])])
        p1=PathPatch(pa1,fill=False,zorder=10,lw=1)
        pa2=MPLPath([(end2[0],end2[1]),
                     (end2[0]-25,end2[1]),(end2[0],end2[1]),(end2[0]-5,end2[1]),
                     (end2[0],end2[1]+5),(end2[0],end2[1]+25),(end2[0],end2[1]),(end2[0],end2[1]+5),
                     (end2[0]+5,end2[1]),(end2[0]+25,end2[1]),(end2[0],end2[1]),(end2[0]+5,end2[1]),
                     (end2[0],end2[1]-5),(end2[0],end2[1]-25),(end2[0],end2[1]),(end2[0],end2[1]-5),
                     (end2[0]-5,end2[1])])
        p2=PathPatch(pa2,fill=False,zorder=10,lw=1)
        self.p.append(p1)
        self.p.append(p2)
        self.canvas.axes.add_patch(p1)
        self.canvas.axes.add_patch(p2)
        self.connect()
        
    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
            
    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.canvas.axes: return

        contains0, attrd = self.p[0].contains(event)
        contains1, attrd = self.p[1].contains(event)
        self.background=self.canvas.copy_from_bbox(self.canvas.axes.bbox)
        
        if contains0:
            self.press=0,self.p[0].get_path().vertices,event.xdata,event.ydata
        elif contains1:
            self.press=1,self.p[1].get_path().vertices,event.xdata,event.ydata
        else:
            return
        
    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.press is None: return
        if event.inaxes != self.canvas.axes: return
        ind, vertices, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress 
        self.canvas.restore_region(self.background) 
        self.p[ind].get_path().vertices=vertices+np.array([dx,dy]) 
        self.canvas.axes.draw_artist(self.p[ind])
        self.canvas.blit(self.canvas.axes.bbox)
        
    def on_release(self, event):
        'on release we reset the press data'
        if self.press is None: return
        ind=self.press[0]
        self.parent.endsMoved(ind,self.p[ind].get_path().vertices[0])
        self.press = None

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.canvas.mpl_disconnect(self.cidpress)
        self.canvas.mpl_disconnect(self.cidrelease)
        self.canvas.mpl_disconnect(self.cidmotion)
        for i in range(len(self.p)):
            self.p.pop(-1).remove()
            
class myFileList(QtGui.QTreeWidget):
    def __init__(self, *args,**kwargs):
        super(myFileList,self).__init__(*args,**kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.emit(QtCore.SIGNAL("dropped"), links)
        else:
            event.ignore()

class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.lastImage=None ##TODO: change?
        self.copyContent = None
        self.imageAnnotations=[]
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("%s %s - new project"%((progname,progversion)))
        self.iconObj=QtGui.QIcon('images/mainIcon.png')
        self.setWindowIcon(self.iconObj)
        self.createActions()
        self.createMenus()
        self.createStatusBar()
        self.createDockWindows()
        self.createToolBars()
        self.newProject()
        self.previewCheck.setChecked(True)
        self.posPatches=[]
        self.endSelector=None
        
    def raiseError(self,ex):
        msgBox=QtGui.QMessageBox()
        msgBox.setInformativeText(str(ex))
        msgBox.setText("Error")
        msgBox.exec_()
        self.updateAll()
        raise ex
    
    def appendToLog(self,string):
        tstr=time.strftime("%H:%m:%S")
        self.Log.append(tstr+" "+string)
        
        
    def newProject(self):
        self.project=autoContact.ContactProject()
        self.setWindowTitle("%s %s - new project"%((progname,progversion)))
        self.fileList.clear()
        self.fileName=""
        
    def save(self):
        if self.project.filename==None:
            self.saveAs()
#        try:
        fileName=self.project.filename
        self.project.save(fileName)
        self.fileName=fileName
        self.statusBar().showMessage("Saved '%s'" % fileName)
        self.appendToLog("Saves '%s'\n" % fileName)
        self.setWindowTitle("%s %s - %s"%((progname,progversion,os.path.basename(fileName))))
#        except Exception as exception:
#            self.statusBar().showMessage("Error '%s'" % exception, 10000)
            
    def saveAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                "Choose a file name", '*.nwcpr', "NW Contact Project (*.nwcpr)")
        if fileName:
#            try:
            self.fileName=fileName
            self.project.save(str(fileName))
            self.statusBar().showMessage("Saved '%s'" % fileName)
            self.appendToLog("Saved '%s'" % fileName)
            self.setWindowTitle("%s %s - %s"%((progname,progversion,os.path.basename(str(fileName)))))
#            except Exception as exception:
#                self.statusBar().showMessage("Error '%s'" % exception, 10000)    

    def open(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                "Choose a file ", '*.nwcpr', "NW Contact Project (*.nwcpr)")
        if fileName:
#            try:
            self.fileName=fileName
            self.project.load(str(fileName))
            print self.project.version
            print autoContact.version
            if self.project.version == "<0.970" or float(self.project.version) < float(autoContact.version):
                QtGui.QMessageBox.about(self, "Warning","Project file with version to old\n"+\
                                              "It is incompatible with the current version\n"+\
                                              "and will most likely not work.")
                                    
            files=self.project.paths
            self.fileList.clear()
            self.__addItems__(files)
            self.updateAll()
            self.statusBar().showMessage("Loaded '%s'" % fileName)
            self.appendToLog("Loaded '%s'" % fileName)
            self.setWindowTitle("%s %s - %s"%((progname,progversion,os.path.basename(str(fileName)))))
#            except Exception as exception:
#                self.statusBar().showMessage("Error '%s'" % exception, 10000)
                
    def exportGDS(self):
        indices=self.getIndices()
        self.export(indices,fileType="GDS")
        
    def exportCATS(self):
        indices=None
        self.export(indices,fileType="CATS")
    
    def exportSettings(self):
        filt="*.txt"
        inf="Text file (*.txt)"
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                "Choose a file name", filt, inf )
        if fileName:
            indices=self.getIndices()
            self.project.exportSettings(str(fileName),indices)
            self.statusBar().showMessage("Exported to '%s'" % fileName)
            self.appendToLog("Exported to '%s'" % fileName)
        
    def autoExport(self):
        filt="*.gds"
        inf="GDSII file"
        indices=self.getIndices()
        fileName = r"C:\Users\rueffer\Desktop\test.gds"
        if fileName:
            fn=str(fileName)
            self.project.export(fn,indices,fileType="GDS")
            self.statusBar().showMessage("Exported to '%s'" % fileName)
            self.appendToLog("Exported to '%s'" % fileName)
            
    def export(self,indices,fileType):
        if fileType == "GDS":
            filt="*.gds"
            inf="GDSII file"
        elif fileType == "CATS":
            filt="*.nwco"
            inf="NW Contact Output (*.nwco)"
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                "Choose a file name", filt, inf )
        if fileName:
            fn=str(fileName)
            self.project.export(fn,indices,fileType=fileType)
            self.statusBar().showMessage("Exported to '%s'" % fileName)
            self.appendToLog("Exported to '%s'" % fileName)

    def __addItems__(self,strings):
        if not (isinstance(strings,list) or isinstance(strings,QtCore.QStringList)):
            strings=[strings]
        items=[]
        for string in strings:
            item=QtGui.QTreeWidgetItem(self.fileList)
            item.setText(0,string)
            item.setText(4,self.project.defaultPattern)
#            item.setCheckState(0,QtCore.Qt.Unchecked)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            items.append(item)
        self.fileList.addTopLevelItems(items)
        
    def endsMoved(self,i,new):
        index=self.getIndices()[0]
        transForm=self.project.createTransformFunc(index)
        new=transForm(new)
        if i == 0:
            name = "end1"
        elif i == 1:
            name = "end2"
        else:
            raise ValueError("this should not happen")
        self.project.setEnd(index,name,new)
        self.updateAll()
        

    def filesDropped(self, l):
        self.__addFiles__(l)    
        
    def __addFiles__(self,fileNames):
        if fileNames:
            try:
                append=[]
                allItems=[self.fileList.topLevelItem(i).text(0) for i in range(self.fileList.topLevelItemCount())]
                for n,fileName in enumerate(fileNames):
                    self.statusBar().showMessage("Loading... %.1f" %(n*100./len(fileNames))+r"%")
                    if fileName not in allItems:
                        self.project.addImage(str(fileName))
                        append.append(fileName)
                        QtGui.QApplication.processEvents()
                self.__addItems__(append)
                self.updateAll()
                if len(fileNames) == 1:
                    self.statusBar().showMessage("Added '%s'" % fileNames[0])
                    self.appendToLog("Added '%s'" % fileNames[0])
                else:
                    self.statusBar().showMessage("Added %d files" % len(fileNames))
                    self.appendToLog("Added %d files" % len(fileNames))
            except Exception as exception:
                self.raiseError(exception)
                    
    def addFiles(self):
        fileNames = QtGui.QFileDialog.getOpenFileNames(self,
                "Choose files ", '*.jpg', "image files")
        self.__addFiles__(fileNames)
        
    def refitImages(self):
        indices=self.getIndices()
        if indices:
            for n,index in enumerate(indices):
                self.project.refitImages(index)
                self.statusBar().showMessage("Fitting... %.1f" %(n*100./len(indices))+r"%")
            self.statusBar().showMessage("Refitted %d image(s)" % len(indices))
            self.appendToLog("Refitted %d image(s)" % len(indices))
            self.lastImage=None
            self.updateAll()
    
    def removeFiles(self):
        indices=self.getIndices()
        if indices:
            self.project.removeImages(indices)
            if len(indices) == 1:
                f= self.fileList.takeTopLevelItem(indices[0])
                self.statusBar().showMessage("Removed '%s'" % f.text(0))
                self.appendToLog("Removed '%s'" % f.text(0))
            else:
                self.fileList.itemSelectionChanged.disconnect(self.fileSelectionChanged)
                for index in sorted(indices)[::-1]:
                    self.fileList.takeTopLevelItem(index)
                self.statusBar().showMessage("Removed %d files" % len(indices))
                self.appendToLog("Removed %d files" % len(indices))
                self.fileList.itemSelectionChanged.connect(self.fileSelectionChanged)
            self.updateAll()
                
    def getIndices(self):
        items=self.fileList.selectedItems()
        indices=[self.fileList.indexOfTopLevelItem(i) for i in items]
        return indices
        
    def updateFitLogs(self):
        items=self.fileList.selectedItems()
        if not items:
            self.fitLog.clear()
            return
        index=self.fileList.indexOfTopLevelItem(items[0])
        string=self.project.fitLogs[index]
        self.fitLog.setText(string)
        
    
    def updateProperties(self):
        items=self.fileList.selectedItems()
        if not items:
            return
        index=self.fileList.indexOfTopLevelItem(items[0])
        keys=self.project.settings[index].keys()
        if "wires" in keys:
            keys.remove("wires")
            wires=self.project.settings[index]["wires"]
        else:
            wires=[]
        self.propertiesDisplay.setRowCount(len(keys)+len(wires))
        for n,key in enumerate(sorted(keys)):
            item=QtGui.QTableWidgetItem()
            item.setText(key)
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.propertiesDisplay.setItem(n,0,item)
            item=QtGui.QTableWidgetItem()
            data=self.project.settings[index][key]
            if isinstance(data,np.ndarray) or isinstance(data,list):
                if isinstance(data[0],float) or isinstance(data[0],np.float):
                    string="("
                    for i in data:
                        string=string+"%.4f,"%i
                    string=string[:-1]+")"
                else:
                    string = str(data)
            elif isinstance(data,float):
                string="%.4f"%data
            else:
                string =str(data)
            item.setText(string)
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.propertiesDisplay.setItem(n,1,item)
        for m,wire in enumerate(wires):
            item=QtGui.QTableWidgetItem()
            item.setText("wire_%d"%m)
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.propertiesDisplay.setItem(n+m+1,0,item)
            item=QtGui.QTableWidgetItem()
            item.setText("[(%.4f;%.4f),(%.4f,%.4f)]"%((wire["end1"][0],wire["end1"][1],wire["end2"][0],wire["end2"][1])))
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.propertiesDisplay.setItem(n+m+1,1,item)
            
        
    def updateAll(self):
        t0=time.time()
        self.updateProperties()
        self.updateWireOptions()
        self.updateList()
        self.updateContactsOption()
        self.updateExposureOptions()
        self.updateFitLogs()
        indices=self.getIndices()
        if len(indices)==0:
            self.copyAct.setEnabled(False)
            self.pasteAct.setEnabled(False)
        elif len(indices)==1:
            self.copyAct.setEnabled(True)
            if self.copyContent == None:
                self.pasteAct.setEnabled(False)
            else:
                self.pasteAct.setEnabled(True)
        else:
            self.copyAct.setEnabled(True)
            self.pasteAct.setEnabled(True)
#        t1=time.time()
#        print "rest: %.3f"%((t1-t0)*1000)
        self.updateImage()
#        t2=time.time()
#        print "image: %.3f"%((t2-t1)*1000)
    
    def previewCheckBoxChanged(self,i):
        self.updateImage()
    
    def fillWireCombo(self,index):
        self.wireCombo.clear()
        items=[]
        for wire in range(len(self.project.settings[index]["wires"])):
            items.append("Wire %d"%wire)
        self.wireCombo.insertItems(0,items)
        self.wireCombo.setCurrentIndex(self.project.getWireNo(index))
#        
    def updateExposureOptions(self):
        layers=list(self.project.getLayers())
        length=len(layers)
        if length < 1:
            self.exposureOptions.setEnabled(False)
            self.exposureCombo.setEnabled(False)
            self.exposureOptions.setRowCount(0)
            return         
        self.exposureCombo.setEnabled(True)
        self.exposureOptions.setEnabled(True)
#        print layers
        index=self.exposureCombo.currentIndex()
        self.exposureCombo.clear()        
        for layer in layers[::-1]:
            self.exposureCombo.insertItem(0,"Layer %d"%layer)
        if not index < len(layers):
            index=0
        if index < 0:
            index = 0
        self.exposureCombo.setCurrentIndex(index)
            
#        print "index: "+str(index)
        if index == -1:
            return
#        self.exposureCombo.setCurrentIndex(layers[0])
#        print self.project.exposureSettings
        optionDict=self.project.getExposureSettings(index)
        options=optionDict.keys()
#        print optionDict
        self.exposureOptions.setRowCount(len(options))
        try:
            self.exposureOptions.cellChanged.disconnect(self.exposureOptionsChanged)
        except:
            pass
        for n,key in enumerate(sorted(options)):
            item=QtGui.QTableWidgetItem()
            item.setText(key)
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.exposureOptions.setItem(n,0,item)
            if optionDict.has_key(key):
                if isinstance(optionDict[key],float) or isinstance(optionDict[key],np.float):
                    value="%.3f"%optionDict[key]
                else:
                    value=str(optionDict[key])
            else:
                print key," not found"
                value="%.3f"%options[key]
                self.project.changeSingleContactOptions(index,key,value)
            item=QtGui.QTableWidgetItem()
            if length == 1:
                item.setText(value)
            else:
                item.setText(value)
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled |  QtCore.Qt.ItemIsEditable )
            self.exposureOptions.setItem(n,1,item)
        self.exposureOptions.cellChanged.connect(self.exposureOptionsChanged)
        
        
    def exposureOptionsChanged(self,row,column):
        try:
            index=self.exposureCombo.currentIndex()
            key=str(self.exposureOptions.item(row,0).text())
            value=str(self.exposureOptions.item(row,1).text())
#            if not key in ["beam"]:
#                value=atof(value)
            self.project.changeExposureSetting(key,index,value)
            self.updateAll()
        except Exception as exception:
            self.raiseError(exception)

    def updateWireOptions(self):
        items=self.fileList.selectedItems()
        if not items:
            self.modeCombo.setEnabled(False)
            self.wireCombo.setEnabled(False)
            return
        index=self.fileList.indexOfTopLevelItem(items[0])
        if not self.project.settings[index]["fit"]:
            self.modeCombo.setEnabled(False)
            self.wireCombo.setEnabled(False)
            return            
        mode=self.project.settings[index]["mode"]
        self.modeCombo.setEnabled(True)
        if mode == "auto":
            self.wireCombo.setEnabled(False)
            self.modeCombo.setCurrentIndex(0)
            self.wireCombo.clear()
        elif mode == "select":
            self.wireCombo.setEnabled(True)
            self.modeCombo.setCurrentIndex(1)
            self.fillWireCombo(index)
        else:
            self.wireCombo.setEnabled(False)
            self.modeCombo.setCurrentIndex(2)
            self.wireCombo.clear()
    
    def updateContactsOption(self):
        items=self.fileList.selectedItems()
        length=len(items)
        if length < 1:
            self.contactsOptions.setEnabled(False)
            self.contactsCombo.setEnabled(False)
            self.contactsOptions.setRowCount(0)
            return         
        contactName0=self.project.settings[self.fileList.indexOfTopLevelItem(items[0])]["contact"]
        for item in items:
            index=self.fileList.indexOfTopLevelItem(item)
            if not self.project.settings[index]["fit"] or self.project.settings[index]["contact"] != contactName0:
                self.contactsOptions.setEnabled(False)
                self.contactsCombo.setEnabled(False)
                self.contactsOptions.setRowCount(0)
                return   
        self.contactsCombo.setEnabled(True)
        self.contactsOptions.setEnabled(True)
        allItems = [self.contactsCombo.itemText(i) for i in range(self.contactsCombo.count())]
        contactName=self.project.settings[index]["contact"]
        i=allItems.index(contactName)
        self.contactsCombo.setCurrentIndex(i)
        options=self.project.getContactOptions(contactName)
        optionDict=self.project.settings[index]["contactOptions"]
        self.contactsOptions.setRowCount(len(options))
#        print options
#        print optionDict
        try:
            self.contactsOptions.cellChanged.disconnect(self.contactsOptionsChanged)
        except:
            pass
        for n,key in enumerate(sorted(options.keys())):
            item=QtGui.QTableWidgetItem()
            item.setText(key)
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.contactsOptions.setItem(n,0,item)
            found=True
            if not optionDict.has_key(key):
                value=None
                found=False
                self.project.changeSingleContactOptions(index,key,value)
                options=self.project.getContactOptions(contactName)
                value="%.3f"%options[key]
            if isinstance(optionDict[key],float) or isinstance(optionDict[key],np.float):
                value="%.3f"%optionDict[key]
            else:
                value=str(optionDict[key])
            if not found:
                self.statusBar().showMessage("%s not found, using default: %s"%((key,value)))
                self.appendToLog("%s not found, using default: %s"%((key,value)))
            item=QtGui.QTableWidgetItem()
            if length == 1:
                item.setText(value)
            else:
                it=True
                for index in [self.fileList.indexOfTopLevelItem(im) for im in items]:
                    if not self.project.settings[index]["contactOptions"].has_key(key):
                        it=False
                        break
                    elif self.project.settings[index]["contactOptions"][key] != optionDict[key]:
                        it=False
                        break
                if it:
                    item.setText(value)
                else:
                    item.setText("--")
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled |  QtCore.Qt.ItemIsEditable )
            self.contactsOptions.setItem(n,1,item)
        self.contactsOptions.cellChanged.connect(self.contactsOptionsChanged)
        
    def contactsOptionsChanged(self,row,column):
        try:
            indices=self.getIndices()
            key=str(self.contactsOptions.item(row,0).text())
            value=str(self.contactsOptions.item(row,1).text())
            print value
            self.project.changeSingleContactOptions(indices,key,value)
            self.updateAll()
        except Exception as exception:
            self.raiseError(exception)

    def contactNameChange(self,index):   
        try:
            contactName=str(self.contactsCombo.currentText())
            indices=self.getIndices()
            self.project.changeContactType(indices,contactName)
            self.updateAll()
        except Exception as exception:
            self.raiseError(exception)
        
    def exposureLayerChange(self,index):
        try:
            self.updateAll()
        except Exception as exception:
            self.raiseError(exception)
    
    def modeChanged(self,index):
        try:
            mode=str(self.modeCombo.currentText())
            indices=self.getIndices()
            self.project.changeMode(indices,mode)
            self.updateAll()
        except Exception as exception:
            self.raiseError(exception)
        
    def wireChanged(self,index):
        try:
            indices=self.getIndices()
            self.project.changeWire(indices[0],index)
            self.updateAll()
        except Exception as exception:
            self.raiseError(exception)
            
    def copySettings(self):
        indices=self.getIndices()
        if not indices:
            return
        index=indices[0]
        self.copyContent={"contact":self.project.settings[index]["contact"],
                          "contactOptions":self.project.settings[index]["contactOptions"]}
    def pasteSettings(self):
        try:
            indices=self.getIndices()
            if not indices or self.copyContent == None:
                return
            self.project.changeContactOptions(indices,self.copyContent["contact"],self.copyContent["contactOptions"])
            #self.copyContent=None
            self.updateAll()
        except Exception as exception:
            self.raiseError(exception)
                
    def fileListPopup(self,pos):
        contextMenu=QtGui.QMenu()
        contextMenu.addAction(self.addFilesAct)
        contextMenu.addAction(self.removeFilesAct)
        contextMenu.addAction(self.refitImagesAct)
        contextMenu.addSeparator()
        contextMenu.addAction(self.selectAllAct)
        contextMenu.addAction(self.copyAct)
        contextMenu.addAction(self.pasteAct)
        contextMenu.addSeparator()
        contextMenu.addAction(self.exportGDSAct)
        contextMenu.addAction(self.exportSettingsAct)
        action = contextMenu.exec_(self.fileList.mapToGlobal(pos))
        if action:
            action.trigger()

    def updateList(self):
        for n in range(self.fileList.topLevelItemCount ()):
            item = self.fileList.topLevelItem(n)
#            print "Toplevelitemcount: "+str(n)
            try:
                if self.project.settings[n]["fit"]:
    #                    item.setCheckState(0,QtCore.Qt.Checked)
                    cell=self.project.settings[n]["cell"]
                    cellstring="%d,%d"%(tuple(cell))
                    block=self.project.descriptor.getBlockNo(cell)
                    blockstring="%d,%d"%(tuple(block))
                    mode=self.project.settings[n]["mode"]
                    item.setText(1,cellstring)
                    item.setText(2,blockstring)
                    item.setText(3,mode)
                else:
    #                    item.setCheckState(0,QtCore.Qt.Unchecked)
                    item.setText(1,"")
                    item.setText(2,"")
                    item.setText(3,"")
                contact=self.project.settings[n]["contact"]
                item.setText(4,contact)
            except IndexError:
                pass #TODO: uggly hack here, solve in a better way
            except Exception as exception:
                self.raiseError(exception)
         
                
    def updateImage(self):
        items=self.fileList.selectedItems()
        if not items:
            for i in range(len(self.imageAnnotations)):
                self.imageAnnotations.pop(0).remove()
            for i in range(len(self.canvas.axes.images)):
                self.canvas.axes.images[i].remove()
            try:
                self.endSelector.disconnect()
            except:
                pass
            self.endSelector = None
            self.lastImage=None
            self.canvas.draw()
            return
        index=self.fileList.indexOfTopLevelItem(items[0])
        for i in range(len(self.imageAnnotations)):
            self.imageAnnotations.pop(0).remove()
#        self.canvas.axes.clear()
            ##  TODO: get directly from axes, avoid the list
        if index >= 0:
            if self.lastImage!=self.project.paths[index]:
                for i in range(len(self.canvas.axes.images)):
                    self.canvas.axes.images[i].remove()
#                print imread(self.project.paths[index])
                self.canvas.axes.imshow(imread(self.project.paths[index]),interpolation="None")
                self.lastImage=self.project.paths[index]
#            if items[0].checkState(0):
            if self.project.settings[index]["cell"]==None:
                self.canvas.draw()
                return
            for pos in self.project.settings[index]["markers"]:
                p=plt.Line2D([pos[0]],[pos[1]],color=[1,0,0],marker="+",ms=5)
                self.canvas.axes.add_artist(p)
                self.imageAnnotations.append(p)
            pos=self.project.settings[index]["center"]
            p=plt.Line2D([pos[0]],[pos[1]],color=[1,0,0],marker="+",ms=10)
            self.canvas.axes.add_artist(p)
            self.imageAnnotations.append(p)
            px,py,tx,ty=self.project.descriptor.getBits(self.project.settings[index]["cell"])
            invTransForm=self.project.createInverseTransformFunc(index)
            scale=self.project.settings[index]["scale"]
            angle=self.project.settings[index]["angle"]
            truth=np.hstack((tx,ty))
            for i,pos in enumerate(np.vstack((px,py))):
                if truth[i]:
                    fc="r"
                else:
                    fc="none"
                xy=invTransForm([(pos[0]-self.project.descriptor.markerSize*2.),(pos[1]-self.project.descriptor.markerSize*2.)])
                p = Rectangle(xy,width=self.project.descriptor.bitDistance/scale,height=-self.project.descriptor.bitDistance/scale,
                              fc=fc,lw=1,alpha=0.3)
                t = MPLTransforms.Affine2D().rotate_around(xy[0],xy[1],-angle/180.*np.pi) + self.canvas.axes.transData
                p.set_transform(t)
                self.canvas.axes.add_artist(p)
                self.imageAnnotations.append(p)
            if self.previewCheck.checkState():
                a=self.project.showCell(self.canvas.axes,index)
                self.imageAnnotations.extend(a)
            if self.project.settings[index]["mode"]=="manual":
                try:
                    self.endSelector.disconnect()
                except:
                    pass
                self.endSelector=endSelector(self,index) ## TODO improve: change properties, do not always override
            else:
                try:
                    self.endSelector.disconnect()
                except:
                    pass
                self.endSelector = None
#            else: ## TODO: clean up this mess with disconnect
#                try:
#                    self.endSelector.disconnect()
#                except:
#                    pass
#                self.endSelector = None
        
        else:
            for i in range(len(self.canvas.axes.images)):
                self.canvas.axes.images[i].remove()
            try:
                self.endSelector.disconnect()
            except:
                pass
            self.endSelector = None
            self.lastImage=None
        self.canvas.draw()
    
    def fileSelectionChanged(self):
        self.updateAll()
        a=len(self.getIndices())
        if a:
            self.statusBar().showMessage("Selected %d files" % a)
        else:
            self.statusBar().showMessage("No files selected")
        
        
    def createFileListDock(self):
        dock = QtGui.QDockWidget("Files", self)
        self.fileListWidget=QtGui.QMainWindow()
        self.fileListWidget.setParent(dock)
        dock.setWidget(self.fileListWidget)
        dock.setMaximumWidth(340)
        dock.setMinimumWidth(280)
        self.fileList = myFileList(parent=self.fileListWidget)
#        self.fileList = QtGui.QTreeWidget(parent=self.fileListWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.fileList.setRootIsDecorated(False)
        self.fileList.setAlternatingRowColors(True)
        self.fileList.setHeaderLabels(["File","Cell","Block","Mode","Contact"])
        self.fileListWidget.setCentralWidget(self.fileList)
        self.fileList.setSelectionMode(3)
        self.fileList.setTextElideMode(QtCore.Qt.ElideLeft)
        self.fileList.header().resizeSection(0,80)
        self.fileList.header().resizeSection(1,40)
        self.fileList.header().resizeSection(2,40)
        self.fileList.header().resizeSection(3,40)
        self.fileList.header().resizeSection(4,50)
        self.fileList.itemSelectionChanged.connect(self.fileSelectionChanged)
        self.fileList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.fileList.customContextMenuRequested.connect(self.fileListPopup)
        self.connect(self.fileList, QtCore.SIGNAL("dropped"), self.filesDropped)

        
        
    def createDockWindows(self):
        self.createFileListDock() 
        self.createImageDock()
        self.createWireOptions()  
        self.createContactOptions() 
        self.createExposureOptions()
        dock = QtGui.QDockWidget("Properties", self)
        self.propertiesDisplay=QtGui.QTableWidget()
        dock.setWidget(self.propertiesDisplay)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.propertiesDisplay.setColumnCount(2)
        self.propertiesDisplay.setHorizontalHeaderLabels(["Property","Value"])
        header=self.propertiesDisplay.horizontalHeader()
        header.setStretchLastSection(True)
        dock.setHidden(True)
        
        dock = QtGui.QDockWidget("Log", self)
        self.Log = QtGui.QTextEdit(dock)
        dock.setWidget(self.Log)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.Log.setReadOnly(True)
        
        dock = QtGui.QDockWidget("Fit Log", self)
        self.fitLog = QtGui.QTextEdit(dock)
        dock.setWidget(self.fitLog)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.fitLog.setReadOnly(True)
        
            
        
    def createImageDock(self):   
        dock = QtGui.QDockWidget("Image & Preview", self)
        self.imageWidget=QtGui.QMainWindow()
        self.imageWidget.setParent(dock)
        dock.setWidget(self.imageWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.canvas = MPLCanvas(dock)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.imageWidget,coordinates=False)
        actlist= self.mpl_toolbar.actions()
        names=["Save","Customize","Subplots"]
        for action in actlist:
            if str(action.text()) in names:
                self.mpl_toolbar.removeAction(action)
        self.previewCheck=QtGui.QCheckBox("Preview")
        self.previewCheck.stateChanged.connect(self.previewCheckBoxChanged)
        self.mpl_toolbar.addWidget(self.previewCheck)
        self.mpl_toolbar.setMovable(False)
        self.imageWidget.addToolBar(self.mpl_toolbar)
        self.imageWidget.setCentralWidget(self.canvas)
        self.imageWidget.setMinimumSize(600,450)        
        
    def createWireOptions(self):
        dock = QtGui.QDockWidget("Wire Options", self)
        dock.setMaximumWidth(340)
        dock.setMinimumWidth(280)
        widget=QtGui.QWidget()
        dock.setWidget(widget)
        self.wireOptionsLayout=QtGui.QGridLayout()
        widget.setLayout(self.wireOptionsLayout)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.modeCombo=QtGui.QComboBox()
        self.wireOptionsLayout.addWidget(self.modeCombo,0,0)
        self.modeCombo.insertItem(0,"manual")
        self.modeCombo.insertItem(0,"select")
        self.modeCombo.insertItem(0,"auto")
        self.modeCombo.setEnabled(False)
        self.wireCombo=QtGui.QComboBox()
        self.wireOptionsLayout.addWidget(self.wireCombo,0,1)
        self.wireCombo.setEnabled(False)
        self.wireCombo.activated.connect(self.wireChanged)
        self.modeCombo.activated.connect(self.modeChanged)
        
    def createContactOptions(self):
        dock = QtGui.QDockWidget("Contact Settings", self)
        dock.setMaximumWidth(340)
        dock.setMinimumWidth(280)
        widget=QtGui.QWidget()
        dock.setWidget(widget)
        self.contactOptionsLayout=QtGui.QVBoxLayout()
        widget.setLayout(self.contactOptionsLayout)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.contactsCombo=QtGui.QComboBox()
        self.contactOptionsLayout.addWidget(self.contactsCombo)
        for key in sorted(autoContact.allPatterns.keys()):
            self.contactsCombo.insertItem(0,key)
        self.contactsCombo.setEnabled(False)
        self.contactsCombo.activated.connect(self.contactNameChange)
        self.contactsOptions = QtGui.QTableWidget()
        self.contactOptionsLayout.addWidget(self.contactsOptions)
        self.contactsOptions.setAlternatingRowColors(True)
        self.contactsOptions.setColumnCount(2)
        self.contactsOptions.horizontalHeader().setStretchLastSection(True)
        self.contactsOptions.setHorizontalHeaderLabels(["Option","Value"])
        self.contactsOptions.setEnabled(False)
        self.contactsCombo.setEnabled(False)
        self.contactsOptions.setRowCount(0)
        
        
    def createExposureOptions(self):
        dock = QtGui.QDockWidget("Exposure Settings", self)
        dock.setMaximumWidth(340)
        dock.setMinimumWidth(280)
        widget=QtGui.QWidget()
        dock.setWidget(widget)
        self.exposureOptionsLayout=QtGui.QVBoxLayout()
        widget.setLayout(self.exposureOptionsLayout)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.exposureCombo=QtGui.QComboBox()
        self.exposureOptionsLayout.addWidget(self.exposureCombo)
#        for key in sorted(autoContact.allPatterns.keys()):
#            self.exposureCombo.insertItem(0,key)
        self.exposureCombo.setEnabled(False)
        self.exposureCombo.activated.connect(self.exposureLayerChange)
        self.exposureOptions = QtGui.QTableWidget()
        self.exposureOptionsLayout.addWidget(self.exposureOptions)
        self.exposureOptions.setAlternatingRowColors(True)
        self.exposureOptions.setColumnCount(2)
        self.exposureOptions.horizontalHeader().setStretchLastSection(True)
        self.exposureOptions.setHorizontalHeaderLabels(["Option","Value"])
        self.exposureOptions.setEnabled(False)
        self.exposureCombo.setEnabled(False)
        self.exposureOptions.setRowCount(0)
        

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("Project")
        self.fileToolBar.setMovable(False)
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.addAction(self.saveAsAct)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.exportCATSAct)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.quitAct)

        self.editToolBar = self.fileListWidget.addToolBar("Edit")
        self.editToolBar.setMovable(False)
        self.editToolBar.addAction(self.addFilesAct)
        self.editToolBar.addAction(self.removeFilesAct)
        self.editToolBar.addAction(self.refitImagesAct)
        self.editToolBar.addSeparator()
        self.editToolBar.addAction(self.selectAllAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)
        self.editToolBar.addSeparator()
#        self.editToolBar.addAction(self.fitAct)
        self.editToolBar.addAction(self.exportGDSAct)
        self.editToolBar.addAction(self.exportSettingsAct)
        self.copyAct.setEnabled(False)
        self.pasteAct.setEnabled(False)


    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&Project")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.menuBar().addSeparator()

        self.viewMenu = self.menuBar().addMenu("&View")
        self.menuBar().addSeparator()
        
        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        
    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
        
    def __selectAll__(self):
        self.fileList.selectAll()
        
    def createActions(self):
        self.newAct = QtGui.QAction(QtGui.QIcon('images/new.png'),
                "&New", self, shortcut=QtGui.QKeySequence.New,
                statusTip="Create a new project",
                triggered=self.newProject)
        self.selectAllAct = QtGui.QAction(QtGui.QIcon('images/selectall.png'),
                "&Select All", self, shortcut=QtGui.QKeySequence.SelectAll,
                statusTip="Select all files",
                triggered=self.__selectAll__)
        self.saveAct = QtGui.QAction(QtGui.QIcon('images/save.png'),
                "&Save", self, shortcut=QtGui.QKeySequence.Save,
                statusTip="Save the current project",
                triggered=self.save)
        self.saveAsAct = QtGui.QAction(QtGui.QIcon('images/saveas.png'),
                "&Save As...", self, shortcut=QtGui.QKeySequence.SaveAs,
                statusTip="Save the current project as ...",
                triggered=self.saveAs)
        self.openAct = QtGui.QAction(QtGui.QIcon('images/open.png'),
                "&Open...", self, shortcut=QtGui.QKeySequence.Open,
                statusTip="Open an existing project",
                triggered=self.open)
        self.quitAct = QtGui.QAction(QtGui.QIcon('images/exit.png'),
                "&Exit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)
        self.aboutAct = QtGui.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)
        self.addFilesAct = QtGui.QAction(QtGui.QIcon('images/plus.png'),
                "&Add files...", self,
                statusTip="Add files to current project",
                triggered=self.addFiles)
        self.removeFilesAct = QtGui.QAction(QtGui.QIcon('images/minus.png'),
                "&Remove files", self,shortcut=QtGui.QKeySequence.Delete,
                statusTip="Remove the selected files from project",
                triggered=self.removeFiles)
        self.refitImagesAct = QtGui.QAction(QtGui.QIcon('images/refresh.png'),
                "&Refit Images", self,shortcut=QtGui.QKeySequence.Refresh,
                statusTip="Refit the selected images",
                triggered=self.refitImages)
        self.exportGDSAct = QtGui.QAction(QtGui.QIcon('images/exportgds.png'),
                "&Export GDS", self,
                statusTip="Export selected cells to a GDS file",
                triggered=self.exportGDS)
        self.exportCATSAct = QtGui.QAction(QtGui.QIcon('images/exportcats.png'),
                "&Export CATS", self,
                statusTip="Export the project for CATS conversion",
                triggered=self.exportCATS)
                
        self.exportSettingsAct=QtGui.QAction(QtGui.QIcon('images/exportFile.png'),
                "&Export setttings to file",self,
                statusTip="Export the settings of selected files to a tab-separated file",
                triggered=self.exportSettings)
#        self.fitAct = QtGui.QAction(QtGui.QIcon('images/curve.png'),
#                "&Fit selected", self,
#                statusTip="Perform fit for selected images",
#                triggered=self.fitSelected)
        self.copyAct=QtGui.QAction(QtGui.QIcon('images/copy.png'),
                "&Copy settings",self,shortcut=QtGui.QKeySequence.Copy,
                statusTip="Copy the settings of the selected wire",
                triggered=self.copySettings)

        self.pasteAct=QtGui.QAction(QtGui.QIcon('images/paste.png'),
                "&Paste settings",self,shortcut=QtGui.QKeySequence.Paste,
                statusTip="Paste the settings to all selected wires",
                triggered=self.pasteSettings)
                

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        string=u"""%(prog)s version %(version)s
Copyright \N{COPYRIGHT SIGN} 2012 Daniel Rüffer

This program does automatic contacting of
nanowires dispersed on the FlexiPattern substrates.
Modulversions:
"""% {"prog": progname, "version": progversion}+\
        "autoContact: "+autoContact.version+"\n"+\
        "autoDetect: "+autoContact.autoDetectVersion+"\n"+\
        "createCJOB: "+autoContact.createCJOBVersion+"\n"+\
        "PatternGenerator: "+autoContact.PatternGeneratorVersion+"\n"+\
        "GDSGenerator: "+autoContact.GDSGeneratorVersion

        QtGui.QMessageBox.about(self, "About %s" % progname,string
)

#dynamic loading of Patterns Plugin:
if __name__ == "__main__":
    qApp = QtGui.QApplication(sys.argv)
    
    aw = ApplicationWindow()
    aw.show()
    #aw.__addFiles__([r'D:\Measurements\OriginalData\Optical@Z1CMI\CT30368\0368.JPG'])
    #aw.__addFiles__([r'D:\Measurements\OriginalData\Optical@Z1CMI\CT30368\03680031.JPG'])
    #aw.project.changeContactType([0],"Bent Contact CPW")
    #aw.project.changeContactType([1],"Bent Contact CPW")
    #aw.fileList.setCurrentIndex(aw.fileList.model().index(0,0))
    #aw.autoExport()
    sys.exit(qApp.exec_())
    qApp.exec_()
#
