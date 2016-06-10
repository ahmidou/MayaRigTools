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
    def __init__(self, loopEvent, currentTool, filters, label=None):
        super(MouseEventFilter, self).__init__()
        self.currentTool = currentTool
        self.event = loopEvent
        self.typeFilter = filters
        self.hit = False
        self.pickedObjects = om.MSelectionList()
        self.buttonPressed = []
        self.modifierPressed = []
        self.colorData = {}

        if cmds.popupMenu("dummyMenu", exists=True):
            cmds.deleteUI("dummyMenu")
        cmds.popupMenu("dummyMenu", parent='viewPanes', button=1)

    def hilite(self, picked):
        # list = []
        # self.pickedObjects.getSelectionStrings(list)
        # cmds.hilite( list, toggle=True )
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
        # list = []
        # om.MSelectionList().getSelectionStrings(list)
        # cmds.hilite( list, toggle=True )
        #
        om.MGlobal.setHiliteList(om.MSelectionList())

    def _getLastDagNode(self, sel_list):
        d = om.MDagPath()
        sel_list.getDagPath(0,d)

        obj = om.MObject(d.node())  
        if obj.apiTypeStr() == "kTransform":
            try:
                d.extendToShape()
            except:
                obj = om.MObject(d.node())
            finally:
                obj = om.MObject(d.node())
        return obj

    def _quit(self, obj):
        obj.releaseKeyboard()
        self.unHilite()
        self.event.quit()

    def eventFilter(self, obj, event):
        #try:
            if event.type() == event.Enter:
                obj.grabKeyboard()

            if event.type() == event.Leave:
                obj.releaseKeyboard()
    
            if event.type() == event.KeyRelease:
                ctx = cmds.currentCtx()
                currentTool = cmds.contextInfo(ctx, c=True)
                if currentTool != self.currentTool or event.key() == QtCore.Qt.Key_Escape:
                    self.pickedObjects = None
                    self._quit(obj)
                if event.key() == QtCore.Qt.Key_Enter:
                    self._quit(obj)

            if event.type() == event.MouseButtonPress:
                modifier = 0
                qMod = event.modifiers()
                if qMod == QtCore.Qt.ShiftModifier:
                    modifier = 1
                elif qMod == QtCore.Qt.ControlModifier:
                    modifier = 2
                elif qMod == QtCore.Qt.AltModifier:
                    modifier = 3

                if event.button() == Qt.MouseButton.RightButton:
                    # Escape condition
                    if self.pickedObjects.isEmpty():
                        self.pickedObjects = None
                    self._quit(obj)
                    return True

                else:
                    pickedName = None

                    # Outliner picking
                    if obj.metaObject().className() == "TpanelDagOutliner":
                        pickedName = cmds.hitTest(
                            obj.objectName(), event.x(), event.y())[0]

                    # Viewport picking
                    self.hit = cmds.dagObjectHit(mn="dummyMenu")
                    if self.hit is True:
                        popChild = cmds.popupMenu(
                            "dummyMenu", q=True, itemArray=True)
                        mItem = cmds.menuItem(popChild[0], q=True, l=True)
                        pickedName = mItem.replace("...", "")
                        cmds.popupMenu("dummyMenu", edit=True,
                                       deleteAllItems=True)

                    if pickedName is not None:
                        picked = om.MSelectionList()
                        picked.add(pickedName)
                        node = self._getLastDagNode(picked)
                        if not picked.isEmpty() and (len(self.typeFilter) == 0 or node.apiTypeStr() in self.typeFilter):
                            self.pickedObjects.merge(picked)
                            self.hilite(picked)
                            views = omui.M3dView
                            for i in range(views.numberOf3dViews()):
                                view = views.get3dView(i)
                                view.refresh()
                            if event.button() == Qt.MouseButton.LeftButton:
                                self.buttonPressed.append(1)
                            elif event.button() == Qt.MouseButton.MidButton:
                                self.buttonPressed.append(2)
                            self.modifierPressed.append(modifier)

                        return True
                    if obj.metaObject().className() == "TpanelDagOutliner":
                        return False
                    return True
                #return False
            #if event.type() == event.MouseButtonRelease:
                #if self.hit == False:
                #return False

            """except:
            self.pickedObjects = None
            obj.releaseKeyboard()
            self.unHilite()
            self.event.quit()
            return False"""

            return False


def pickObject(leftMessage=None, middleMessage=None, buttonPressed=[], modifierPressed=[], filters=[]):
    """
    Form a complex number.

    Keyword arguments:
    leftMessage     --  Status bar message for the left mouse button
    middleMessage   --  Status bar message for the middle mouse button
    buttonPressed   --  Returns the mouse button clicked by the user.
                        Possible Values:
                            - 0: Right mouse button (or the Esc key), which means the user aborted the picking session
                            - 1: Left mouse button
                            - 2: Middle mouse button
    modifierPressed --  Returns the modifier key pressed by the user.
                        Possible Values:
                            - 0: None
                            - 1: Shift modifier key
                            - 2: Ctrl modifier key
                            - 3: Shift-Ctrl modifier key
    filter          --  a list of MFn.Type as strings. 
                        ie: ["kMesh", "kNurbsCurve", "kNurbsSurface", "kLocator", "kJoint"]

    return a MSelectionList, or None if nothing picked or escaped
    """

    # Init
    views = omui.M3dView
    viewCount = views.numberOf3dViews()
    outlinerPanels = cmds.getPanel(typ='outlinerPanel')
    ctx = cmds.currentCtx()
    currentTool = cmds.contextInfo(ctx, c=True)
    loop = QEventLoop()
    eventFilter = MouseEventFilter(loop, currentTool, filters)

    # Add the eventFilter to all the viewports
    widgets = []
    for i in range(viewCount):
        view = views.get3dView(i)
        widget_ptr = view.widget()
        widget = wrapInstance(long(widget_ptr), QWidget)
        widget.setCursor(QCursor(Qt.PointingHandCursor))
        widget.installEventFilter(eventFilter)
        widgets.append(widget)

    # Add the eventFilter to all the outliners
    for panel in outlinerPanels:
        ptr = mui.MQtUtil.findControl(panel)
        if ptr is not None:
            outPanel = wrapInstance(long(ptr), QObject)
            regex = QRegExp("outlinerPanel.*")
            outliners = outPanel.findChildren(QtGui.QWidget, regex)
            for outliner in outliners:
                if outliner.metaObject().className() == "TpanelDagOutliner":
                    outliner.installEventFilter(eventFilter)
                    widgets.append(outliner)

    # Add the help messages
    ptr = mui.MQtUtil.findControl("helpLine1")
    helpLine = wrapInstance(long(ptr), QStatusBar)
    lMessage = QLabel("L: " + leftMessage)
    lMessage.setMargin(helpLine.width() / 10)
    helpLine.addPermanentWidget(lMessage)
    mMessage = QLabel("M: " + middleMessage)
    mMessage.setMargin(helpLine.width() / 10)
    helpLine.addPermanentWidget(mMessage)
    rMessage = QLabel(" R: Exit")
    rMessage.setMargin(helpLine.width() / 10)
    helpLine.addPermanentWidget(rMessage)

    loop.exec_()

    # Get Outputs
    picked = eventFilter.pickedObjects
    buttonPressed.extend(eventFilter.buttonPressed)
    modifierPressed.extend(eventFilter.modifierPressed)

    # Cleanup
    for widget in widgets:
        widget.unsetCursor()
        widget.removeEventFilter(eventFilter)
        # widget.releaseKeyboard()
    eventFilter = None
    if cmds.popupMenu("dummyMenu", exists=True):
        cmds.deleteUI("dummyMenu")
    helpLine.removeWidget(lMessage)
    helpLine.removeWidget(mMessage)
    helpLine.removeWidget(rMessage)

    return picked

"""import sys
sys.path.append(r"D:\dev\AL_Maya\MayaRigTools\pickObject")

import pickObject
reload(pickObject)
buttonPressed = []
modPressed = []
print pickObject.pickObject("pick mesh","pick curve", buttonPressed, modPressed, ["kMesh", "kNurbsCurve", "kNurbsSurface", "kLocator", "kJoint"])"""
