"""
Wrap instance method:
http://nathanhorne.com/?p=485

Event filter installation example:
https://groups.google.com/d/msg/python_inside_maya/LwmKyqp8MW8/pSa0gRKuKHQJ
"""
from maya import cmds
import maya.api.OpenMaya as om2
import maya.OpenMaya as om
import maya.OpenMayaUI as mui
import maya.api.OpenMayaUI as omui
from PySide import QtGui, QtCore
from PySide.QtCore import * 
from PySide.QtGui import * 
from shiboken import wrapInstance
import shiboken


# Lifted from older Maya Python post:
# https://groups.google.com/d/msg/python_inside_maya/LwmKyqp8MW8/pSa0gRKuKHQJ
#
class MouseEventFilter(QtCore.QObject):
    def __init__(self, loopEvent, currentTool, label=None):
        super(MouseEventFilter, self).__init__()
        self.currentTool = currentTool
        self.event = loopEvent
        self.typeFilter = None
        self.pickedObjects = om.MSelectionList()
        self.colorData = {}

        if cmds.popupMenu("dummyMenu", exists=True):
            cmds.deleteUI("dummyMenu")
        cmds.popupMenu("dummyMenu", parent='viewPanes', button=1)
        

    def hilite(self, picked):
        #list = []
        #self.pickedObjects.getSelectionStrings(list)
        #cmds.hilite( list, toggle=True )
        #
        om.MGlobal.setHiliteList(self.pickedObjects)
        """if not picked.isEmpty():
            node = om2.MFnDependencyNode(picked.getDependNode(0))
            oe =  node.findPlug("overrideEnabled", False)
            os =  node.findPlug("overrideShading",False)
            c = node.findPlug("overrideColor",False)
            oc = node.findPlug("overrideRGBColors",False)
            oe.setBool(True)
            os.setBool(False)
            oc.setBool(0)
            c.setInt(21)"""


    def unHilite(self):
        pass
        #list = []
        #om.MSelectionList().getSelectionStrings(list)
        #cmds.hilite( list, toggle=True )
        #
        om.MGlobal.setHiliteList(om.MSelectionList())
        
    def eventFilter(self, obj, event):
        if event.type() == event.Enter:
            obj.grabKeyboard()

        if event.type() == event.Leave:
            obj.releaseKeyboard()

        if event.type() == event.KeyRelease:
            ctx = cmds.currentCtx()
            currentTool = cmds.contextInfo(ctx, c=True)
            if currentTool != self.currentTool or event.key() == QtCore.Qt.Key_Escape:
                self.pickedObjects = None
                obj.releaseKeyboard()
                self.unHilite()
                self.event.quit()
            if event.key() == QtCore.Qt.Key_Enter:
                obj.releaseKeyboard()
                self.unHilite()
                self.event.quit()
            
        if event.type() == event.MouseButtonPress:            
            if event.button() == Qt.MouseButton.RightButton:
                # escape condition
                if self.pickedObjects.isEmpty():
                    self.pickedObjects = None
                obj.releaseKeyboard()
                self.unHilite()
                self.event.quit()
                return True 

            else:
                pickedName = None
                if obj.metaObject().className() == "TpanelDagOutliner":
                    pickedName = cmds.hitTest( obj.objectName(), event.x(), event.y() )[0]
                    print "HIT: " + pickedName
                # Select what is under the mouse
                hit = cmds.dagObjectHit(mn="dummyMenu")
                if hit == True:
                    popChild = cmds.popupMenu("dummyMenu", q=True, itemArray=True)
                    mItem = cmds.menuItem(popChild[0], q=True, l=True)
                    pickedName = mItem.replace("...", "")
                    print "HIT: " + pickedName
                    cmds.popupMenu("dummyMenu", edit=True, deleteAllItems=True)

                if pickedName != None:
                    picked = om.MSelectionList()
                    picked.add(pickedName)

                    if not picked.isEmpty():
                        self.pickedObjects.merge(picked)
                        self.hilite(picked)
                        views = omui.M3dView
                        for i in range(views.numberOf3dViews()):
                            view = views.get3dView(i) 
                            view.refresh()
                    return True
                return False
        else:
            return False
        return False
    

def pickObject():
    views = omui.M3dView
    viewCount = views.numberOf3dViews()
    outlinerPanels =cmds.getPanel(typ='outlinerPanel')
    ctx = cmds.currentCtx()
    currentTool =  cmds.contextInfo(ctx, c=True)

    loop = QEventLoop()
    eventFilter = MouseEventFilter(loop, currentTool)
    
    # add the eventFilter to all the viewports
    widgets = []
    for i in range(viewCount):
        view = views.get3dView(i)
        widget_ptr = view.widget()
        widget = wrapInstance(long(widget_ptr), QWidget)
        widget.setCursor(QCursor(Qt.PointingHandCursor))
        widget.installEventFilter(eventFilter)
        widgets.append(widget)

    # add the eventFilter to all the outliners
    for panel in outlinerPanels:
        ptr = mui.MQtUtil.findControl(panel)
        outPanel = wrapInstance(long(ptr), QObject)
        regex = QRegExp("outlinerPanel.*")
        outliners =  outPanel.findChildren(QtGui.QWidget, regex)
        for outliner in outliners:
            if outliner.metaObject().className() == "TpanelDagOutliner":
                #print outliner.objectName() +" "+ outliner.metaObject().className()
                outliner.installEventFilter(eventFilter)
                widgets.append(outliner)

    loop.exec_()
    
    # Cleanup
    picked =  eventFilter.pickedObjects 
    
    for widget in widgets:
        widget.unsetCursor()
        widget.removeEventFilter(eventFilter)
        #widget.releaseKeyboard()
    eventFilter = None
    
    if cmds.popupMenu("dummyMenu", exists=True):
        cmds.deleteUI("dummyMenu")

    return picked

"""import sys
sys.path.append(r"D:\dev\AL_Maya\MayaRigTools\pickObject")

import pickObject
reload(pickObject)
pickObject.pickObject()"""
