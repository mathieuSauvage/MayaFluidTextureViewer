# Fluid Texture Viewer version 1.0

This is a Maya python script that generate a rig to view the texture parameters
from a fluid.
All the Rig will exist under a group named "fluidTextureVizualiser#" in the world.
So deleting this group will delete the entire rig.

the main controller created is fluidTextureViewerCtrl#

with the attributes:

* *translate* the only transformation available, just so you can offset the
position of the viewer in space to put it where it's more convenient for you.

* [display Fluid Viewer] hide/display the viewer (fluid)

* [display Fluid bounding] hide/display the bounding box of the original fluid 
(cosmetic)

* [view texture rotate],[view texture scale],[view texture origin],[view implode], 
[view texture time]
for all these parameters, if "on" then the source fluid texture parameter will
be used by the viewer. if "off" then the viewer will use the corresponding
default value.

* [texture gain] the viewer fluid texture gains (opacity)

* [texture opacity preview gain] maya fluid display opacity preview gain of the
viewer fluid.

* [slim Axis] the axis along which the fluid viewer size is reduced for viewing
purpose.

* [reso Slim] All axis of the viewer fluid have the same resolution as the source
fluid, except the slim Axis which will use this resolution. This parameter will
change the size of the slice.

* [reso mult] the resolution of the viewer fluid will be multiplied by this value

* [apply origin on slim Axis] if "off" then the origin texture values displayed
will be limited to the plan of the slice. If "on" then the viewer show the full
space values.

* [apply scale on slim Axis] if "off" then the scale texture values displayed
will be limited to the plan of the slice. If "on" then the viewer show the full
space values.

then all the default values used by the viewer when the view of a parameter is
disabled

## Usage in Maya

* select a fluid then copy/paste this into a Maya python script editor and
execute it.

* put the script into a python script folder that Maya know, then use an import
command to use the script and call the main function with appropriate parameters.

## Main Function to call?

FTV_createFluidTextureViewer( fluid )

## Contact
If you find bugs, or want something added to this script feel free to contact me
mathieu@hiddenforest.fr


