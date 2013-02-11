# Fluid Texture Viewer version 1.0

This is a Maya python script that generate a rig to view the texture
of a fluid.
All the Rig will exist under a group named *fluidTextureViewer#* in the world.
So deleting this group will delete the entire rig.

the main controller created is *fluidTextureViewerCtrl#*

with these attributes:

* **translate** the only transformation available, just so you can offset the
position of the viewer in space to put it in a convenient place.

* **display Fluid Viewer** hide/display the viewer (fluid)

* **display Fluid bounding** hide/display the fake bounding box that represent the original fluid size
(cosmetic)

* **view texture rotate**, **view texture scale**, **view texture origin**, **view implode**, 
**view texture time**
for all these parameters, if "on" then the source fluid texture parameter will
be used by the viewer. if "off" then the viewer will display the corresponding
default value.

* **texture gain** the viewer fluid texture gains (opacity)

* **texture opacity preview gain** maya fluid display opacity preview gain of the
viewer fluid.

* **slim axis** the axis along which the fluid viewer size is reduced for viewing
purpose.

* **reso slim** All axis of the viewer fluid have the same resolution as the source
fluid, except the slim Axis which will use this resolution. This parameter will
change the size of the slice.

* **reso mult** the resolution of the viewer fluid will be multiplied by this value

* **apply origin on slim axis** if "off" then the origin texture values displayed
will be limited to the plan of the slice. If "on" then the viewer show the full
space values.

* **apply scale on slim axis** if "off" then the scale texture values displayed
will be limited to the plan of the slice. If "on" then the viewer show the full
space values.

* after that come all the default values used by the viewer when the view of a parameter is
disabled

Also on the fluid object of the viewer *(source fluid name)_textView#*

You can use the translate of the fluid transform of the viewer to translate
the texture slice in texture space. This way you are not stuck with a visualization
of the center of your fluid

## Why?

I found it difficult to visualize the texture of a fluid in Maya and this script
is trying to provide a solution by creating another fluid focused only on the texture.

You can also toggle some parameters if you want to clearly animate some others without changing anything
on the source fluid. For example if you want to see the effect of your translation animation of the texture origin but you have at the same time a strong implode that distort everything : you can just disable
implode in the viewer and you can see clearly your origin animation. (same with texture time etc...)

## Intented way to use it

After you cached the source fluid then you can focus on the fluid texture's parameters animation by playblasting the viewer.

## Usage in Maya

2 ways:
* select a fluid, then copy/paste this into a Maya python script editor and
execute it.
* put the script into a python script folder which path is known by Maya, then use an import
command to use the script and call the main function with appropriate parameters.

This script use Pymel, so if you can't import pymel you are in trouble.

## Main function to call?

FTV_createFluidTextureViewer( fluid )

## Notes
on my laptop, the refresh of the fluid is not triggered by Maya until I display the attribute editor
of the viewer. But once it's done, the viewer refresh correctly when the values of the source fluid change.
I will try to find a way to avoid this later.

Also you will see that the texture rotation of the fluid source make the viewer rotate.
It may seems a bit weird but actually that was the only way I could make all the transformations
works together (having the ability the restrict texture scale, translate to a plan, being able to offset
the slice...). But this way you actually can see the rotation clearly and if you want, you can still disable
the rotation with the viewer parameters.
## Contact
feedback? bugs? request?... feel free to contact me
mathieu@hiddenforest.fr


