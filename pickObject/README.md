# PickObjects
This module was inspired by the Softimage PickObject() command.
calling the function will block the script execution until and exit condition is met.

escape or changing tool will exit and return None.

MMB or enter will exit and return the picked objects.

usage:
import pickObject
picked = pickObject.pickObject()

TODO:
I'm currently using hilite when picking, but I need to find another way as it could conflict with objects already in subcomponent mode.
I'm also using "cmds.dagObjectHit" which is a bit dirty as I need to create a dummy popup menu