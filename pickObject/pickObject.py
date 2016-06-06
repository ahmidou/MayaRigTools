"""
Wrap instance method:
http://nathanhorne.com/?p=485

Event filter installation example:
https://groups.google.com/d/msg/python_inside_maya/LwmKyqp8MW8/pSa0gRKuKHQJ
"""

import maya.api.OpenMaya as om2
import maya.OpenMaya as om
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
    def __init__(self, loopEvent, label=None):
        super(MouseEventFilter, self).__init__()

        self.event = loopEvent
        self.__label = label
        self.pickedObjects = om.MSelectionList()

        if cmds.popupMenu("dummyMenu", exists=True):
            cmds.deleteUI("dummyMenu")
        cmds.popupMenu("dummyMenu", parent='viewPanes', button=1)
        
        
    def eventFilter(self, obj, event):
        print obj
        typ = event.type()
        #print typ
        if event.type() == event.Enter:

        if event.type() == event.leave:

        if event.type() == event.KeyPress:
            ctx = cmds.currentCtx()
            print cmds.contextInfo(ctx, c=True)
            
        if event.type() == event.MouseButtonPress:            
            if event.button() == Qt.MouseButton.MidButton:
                # escape condition
                self.event.quit()      
            else:
                # Select what is under the mouse
                hit = cmds.dagObjectHit(mn="dummyMenu")
                if hit == True:
                    popChild = cmds.popupMenu("dummyMenu", q=True, itemArray=True)
                    mItem = cmds.menuItem(popChild[0], q=True, l=True)
                    pickedName = mItem.replace("...", "")
                    print "HIT: " + pickedName
                    cmds.popupMenu("dummyMenu", edit=True, deleteAllItems=True)
                    picked = om.MSelectionList()
                    picked.add(pickedName)

                    if not picked.isEmpty():
                        self.pickedObjects.merge(picked)
                        om.MGlobal.setHiliteList(self.pickedObjects)
                        views = omui.M3dView
                        for i in range(views.numberOf3dViews()):
                            view = views.get3dView(i) 
                            view.refresh()

        return False
    

def pickObject():
    views = omui.M3dView
    viewCount = views.numberOf3dViews()

    loop = QEventLoop()
    eventFilter = MouseEventFilter(loop)
    
    # add the eventFilter to all the viewports
    widgets = []
    for i in range(viewCount):
        view = views.get3dView(i)   
        widget_ptr = view.widget()
        widget = wrapInstance(long(widget_ptr), QWidget)
        widget.setCursor(QCursor(Qt.PointingHandCursor))
        widget.installEventFilter(eventFilter)
        widgets.append(widget)
    loop.exec_()
    
    # Cleanup
    picked =  eventFilter.pickedObjects 
    om.MGlobal.setHiliteList(om.MSelectionList())
    for widget in widgets:
        widget.unsetCursor()
        widget.removeEventFilter(eventFilter) 
    eventFilter = None
    
    if cmds.popupMenu("dummyMenu", exists=True):
        cmds.deleteUI("dummyMenu")

    return picked
