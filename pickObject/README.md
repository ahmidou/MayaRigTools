# PickObjects
This module was inspired by the Softimage PickObject() command.
calling the function will block the script execution until and exit condition is met.

-Escape or switch tool will exit and return None.

-MMB or Enter will exit and return the picked objects.

usage:
import pickObject
picked = pickObject.pickObject()

TODO:
- I'm currently using `hilite` when picking, but I need to find another way as it could conflict with objects already in subcomponent mode.
- I'm also using `cmds.dagObjectHit` which is a bit dirty as I need to create a dummy popup menu but I'm not sure if there is any alternative. I don't wan't to use `selectFormScreen()` and `cmds.hitTest()` only work with shapes.