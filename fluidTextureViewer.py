'''
================================================================================
* VERSION : 1.0
================================================================================
* AUTHOR:
Mathieu Sauvage mathieu@hiddenforest.fr
================================================================================
* INTERNET SOURCE:
https://github.com/mathieuSauvage/MayaFluidTextureViewer.git
================================================================================
* MAIN FUNCTION:
FTV_createFluidTextureViewer( fluid )
================================================================================
* DESCRIPTION:
This is a Maya python script that generate a rig to view the texture parameters
from a fluid. Please see the full description at the INTERNET SOURCE.
================================================================================
* USAGE:

- select a fluid then copy/paste this into a Maya python script editor and
execute it.

- put the script into a python script folder that Maya know, then use an import
command to use the script and call the main function with appropriate parameters.  
================================================================================
* TODO:
maybe add something to force the refresh of the Viewer fluid
================================================================================
'''

import pymel.core as pm

class FTV_msCommandException(Exception):
    def __init__(self,message):
        self.message = '[FTV] '+message
    
    def __str__(self):
        return self.message

# connect every keyable and non locked attribute of src to dest (basically connect parameters from control)
def FTV_multiConnectAutoKeyableNonLocked(src, dest, attsExcept):
	atts = pm.listAttr(src, k=True, u=True)
	for a in atts:
		if a in attsExcept:
			continue
		pm.connectAttr(src+'.'+a, dest+'.'+a)

def FTV_lockAndHide( obj, atts, keyable=False ):
	for att in atts:
		pm.setAttr(obj+'.'+att, lock=True, k=keyable)

def FTV_getFluidElements( fluid ):
	if fluid is None:
		raise FTV_msCommandException('Please select a Fluid')

	fldTrs = None
	fldShp = None
	if pm.nodeType(fluid)== 'transform':
		childs = pm.listRelatives(s=True)
		if len(childs)>0 and pm.nodeType(childs[0]) == 'fluidShape' :
			fldTrs = fluid
			fldShp = childs[0]
		else :
			raise FTV_msCommandException('selection is invalid, you must select a fluid')
	elif pm.nodeType(fluid)== 'fluidShape':
		par = pm.listRelatives(p=True)
		if len(par)>0 and pm.nodeType(par[0]) == 'transform' :
			fldTrs = par[0]
			fldShp = fluid
		else :
			raise FTV_msCommandException('selection is invalid, you must select a fluid')
	else :
		raise FTV_msCommandException('selection is invalid, you must select a fluid')
	return (fldTrs,fldShp)

# the main attributes are attributes that will be keyable on the controller
def addMainAttributesToObject( obj, keyable ):
	line = '-------------'
	obj.addAttr('display',nn=line+' [display] ', k=keyable, at='enum', en=line+':')
	pm.setAttr(obj+'.display',l=True)
	obj.addAttr('displayFluidViewer', k=keyable,at='bool', dv=True)
	obj.addAttr('displayFluidBounding', k=keyable,at='bool', dv=True)
	obj.addAttr('viewTextureRotate', k=keyable,at='bool', dv=True)
	obj.addAttr('viewTextureScale', k=keyable,at='bool', dv=True)
	obj.addAttr('viewTextureOrigin', k=keyable,at='bool', dv=True)
	obj.addAttr('viewImplode', k=keyable,at='bool', dv=True)
	obj.addAttr('viewTextureTime', k=keyable,at='bool', dv=True)
	obj.addAttr('viewerParameters',nn=line+' [viewer Parameters] ', k=keyable, at='enum', en=line+':')
	pm.setAttr(obj+'.viewerParameters',l=True)
	obj.addAttr('textureGain',k=keyable,dv=1.0)
	obj.addAttr('textureOpacityPreviewGain',k=keyable,dv=.8)
	obj.addAttr('slimAxis', k=keyable, at='enum', en='XAxis:YAxis:ZAxis:None:')
	obj.addAttr('resoSlim', k=keyable,dv=3.0)
	obj.addAttr('resoMult', k=keyable,dv=1.0,min=.001)
	obj.addAttr('applyOriginOnSlimAxis', k=keyable,at='bool', dv=False)
	obj.addAttr('applyScaleOnSlimAxis', k=keyable, at='bool', dv=False)
	obj.addAttr('defautValues', nn=line+' [default Values if disable] ', k=keyable, at='enum', en=line+':')
	pm.setAttr(obj+'.defautValues',l=True)
	obj.addAttr('textureDefaultScaleX', k=keyable, dv=1.0)
	obj.addAttr('textureDefaultScaleY', k=keyable, dv=1.0)
	obj.addAttr('textureDefaultScaleZ', k=keyable, dv=1.0)
	obj.addAttr('textureDefaultOriginX',k=keyable, dv=0.0)
	obj.addAttr('textureDefaultOriginY',k=keyable, dv=0.0)
	obj.addAttr('textureDefaultOriginZ',k=keyable, dv=0.0)
	obj.addAttr('textureDefaultRotateX',k=keyable, dv=0.0)
	obj.addAttr('textureDefaultRotateY',k=keyable, dv=0.0)
	obj.addAttr('textureDefaultRotateZ',k=keyable, dv=0.0)
	obj.addAttr('defaultImplode',k=keyable, dv=0.0)
	obj.addAttr('defaultTextureTime',k=keyable, dv=0.0)

def FTV_createFluidDummy( name ):
	fldShape = pm.createNode('fluidShape', n=name)
	par = pm.listRelatives(fldShape, p=True)
	fldTrans = pm.rename( par[0], name) # we rename after because we can't do a proper naming in the createNode of a fluidshape
	shps = pm.listRelatives(fldTrans, s=True)
	fldShape = shps[0]

	pm.setAttr(fldShape+'.velocityMethod', 0)
	pm.setAttr(fldShape+'.velocityMethod', l=True)
	pm.setAttr(fldShape+'.densityMethod', 3)
	pm.setAttr(fldShape+'.densityMethod', l=True)
	pm.setAttr(fldShape+'.temperatureMethod', l=True)
	pm.setAttr(fldShape+'.fuelMethod', l=True)
	
	pm.setAttr(fldShape+'.opacityTexture', 1)
	pm.setAttr(fldShape+'.selfShadowing', 1)
	pm.setAttr(fldShape+'.boundaryDraw', 4)
	pm.setAttr(fldShape+'.coordinateMethod', l=True)

	pm.setAttr(fldShape+'.primaryVisibility', 0)
	pm.setAttr(fldShape+'.receiveShadows', 0)
	pm.setAttr(fldShape+'.castsShadows', 0)

	fldShape.addAttr('sizeXOrig', dv=10)
	fldShape.addAttr('sizeYOrig', dv=10)
	fldShape.addAttr('sizeZOrig', dv=10)
	fldShape.addAttr('resoXOrig', dv=10)
	fldShape.addAttr('resoYOrig', dv=10)
	fldShape.addAttr('resoZOrig', dv=10)
	addMainAttributesToObject(fldShape,False)

	pm.connectAttr(fldShape+'.textureGain',fldShape+'.opacityTexGain')
	pm.connectAttr(fldShape+'.textureGain',fldShape+'.colorTexGain')
	pm.connectAttr(fldShape+'.textureGain',fldShape+'.incandTexGain')

	pm.connectAttr(fldShape+'.textureOpacityPreviewGain',fldShape+'.opacityPreviewGain')
	# expression that calculate the size and resolution for the vizualizer depending on slimAxis chosen and resolution multiplier etc...
	pm.expression( s='float $res[];\n\nfloat $size[];\n\n\n\n$res[0] = resoXOrig * resoMult;\n\n$res[1] = resoYOrig * resoMult;\n\n$res[2] = resoZOrig * resoMult;\n\n\n\n$size[0] = sizeXOrig;\n\n$size[1] = sizeYOrig;\n\n$size[2] = sizeZOrig;\n\n\n\n\nfloat $rezoSlim = resoSlim;\nint $slimAxis = slimAxis;\n\nif ( $slimAxis != 3 )\n{\n\tfloat $ratio = $res[$slimAxis] / $size[$slimAxis];\n\tif (($rezoSlim%2) != ( $res[$slimAxis] % 2 ))\n\t\t$rezoSlim += 1;\n\n\t$size[$slimAxis] = $rezoSlim/$ratio;\n\n\t$res[$slimAxis] = $rezoSlim;\n}\n\n\n\nresolutionW = $res[0];\n\nresolutionH = $res[1];\n\nresolutionD = $res[2];\n\n\ndimensionsW = $size[0];\ndimensionsH = $size[1];\ndimensionsD = $size[2];', o=fldShape, ae=True, uc=all)
	#lock of attributes
	FTV_lockAndHide(fldTrans, ['rx','ry','rz','sx','sy','sz'])

	return fldTrans,fldShape

def FTV_setDirectConnectionsFluidToTexture( fluidSource, vizuFluid ):
	pm.connectAttr ( fluidSource+'.resolutionW', vizuFluid+'.resoXOrig' )
	pm.connectAttr ( fluidSource+'.resolutionH', vizuFluid+'.resoYOrig' )
	pm.connectAttr ( fluidSource+'.resolutionD', vizuFluid+'.resoZOrig' )
	pm.connectAttr ( fluidSource+'.dimensionsW', vizuFluid+'.sizeXOrig' )
	pm.connectAttr ( fluidSource+'.dimensionsH', vizuFluid+'.sizeYOrig' )
	pm.connectAttr ( fluidSource+'.dimensionsD', vizuFluid+'.sizeZOrig' )

	# texture direct connections
	directAtts = ['textureType','invertTexture','amplitude','ratio','threshold','depthMax','frequency','frequencyRatio','inflection','billowDensity','spottyness','sizeRand','randomness','falloff','numWaves']
	for a in directAtts:
		pm.connectAttr ( fluidSource+'.'+a, vizuFluid+'.'+a )

def FTV_generateFluidTransformSpaceGrp( name, fluidSourceData):
	fluidSpaceTransform = pm.group( em=True, n=name )
	pm.parentConstraint(fluidSourceData[0], fluidSpaceTransform)
	pm.scaleConstraint(fluidSourceData[0], fluidSpaceTransform)
	FTV_lockAndHide(fluidSpaceTransform, ['v'])

	return fluidSpaceTransform

def FTV_createTransformedGeometry( objSrc, outShapeAtt, inShapeAtt, sourceTransform ):
	shps = pm.listRelatives(objSrc, s=True)
	srcShape = shps[0]

	dup = pm.duplicate(objSrc)
	shps = pm.listRelatives(dup[0], s=True)
	destShape = shps[0]
	dupShape = pm.parent(destShape, objSrc, add=True, s=True)
	pm.delete(dup[0])	
	destShape = dupShape[0] 

	trGeo = pm.createNode('transformGeometry')
	pm.connectAttr( sourceTransform+'.matrix', trGeo+'.transform')
	pm.connectAttr( srcShape+'.'+outShapeAtt,  trGeo+'.inputGeometry' )
	pm.connectAttr( trGeo+'.outputGeometry', destShape+'.'+inShapeAtt )
	pm.setAttr(srcShape+'.intermediateObject',True)
	return destShape

def FTV_createMainFluidTextViewControl( vizuFluidTrans, vizuFluidShape, fluidSpaceTransform):
	circle = pm.circle( n='fluidTextureViewerCtrl#', c=(0,0,0), nr=(0,1,0), sw=360, r=1, ut=False,s=8, ch=False )
	pm.parent(circle[0],fluidSpaceTransform,r=True)

	size = 0.5
	ptList = [(-size,-size,-size), (size,-size,-size), (size,-size,size), (-size,-size,size), (-size,-size,-size), (-size,size,-size), (size,size,-size), (size,size,size), (-size,size,size), (-size,size,-size), (size,size,-size),(size,-size,-size),(size,-size,size),(size,size,size),(-size,size,size),(-size,-size,size)]
	cube = pm.curve( p = ptList, d=1, n='tempNameCubeNurbs#')

	grpDummyTransform = pm.group(em=True,n='dummyFluidSizeToMatrix#')

	pm.connectAttr( vizuFluidTrans+'.sizeXOrig', grpDummyTransform+'.scaleX')
	pm.connectAttr( vizuFluidTrans+'.sizeYOrig', grpDummyTransform+'.scaleY')
	pm.connectAttr( vizuFluidTrans+'.sizeZOrig', grpDummyTransform+'.scaleZ')
	FTV_lockAndHide( grpDummyTransform, ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'])

	circleShape = FTV_createTransformedGeometry(circle,'local', 'create',grpDummyTransform)
	cubeShape = FTV_createTransformedGeometry(cube,'local', 'create',grpDummyTransform)
	pm.setAttr(cubeShape+'.template',True)
	allCubeShapes = pm.listRelatives(cube,s=True)
	pm.parent(allCubeShapes, circle, add=True, s=True)
	pm.delete(cube)
	pm.rename( allCubeShapes[0],'BBFluidShapeSrc#' )
	retShape = pm.rename( allCubeShapes[1],'BBFluidShape#' )

	FTV_lockAndHide(circle[0], ['rx','ry','rz','sx','sy','sz','v'])
	pm.parent(grpDummyTransform,fluidSpaceTransform,r=True)

	return circle[0], retShape

def FTV_createValueToggle( attributeView, offAttributes, onAttributes):
	parts = attributeView.split('.')
	condOnOff = pm.createNode('condition',n=parts[1]+'ValuesOnOff#')
	pm.connectAttr(attributeView, condOnOff+'.firstTerm')
	pm.setAttr( condOnOff+'.secondTerm',1)
	pm.connectAttr(offAttributes[0],condOnOff+'.colorIfFalseR')
	pm.connectAttr(onAttributes[0],condOnOff+'.colorIfTrueR')

	if len(offAttributes)>1:
		pm.connectAttr(offAttributes[1],condOnOff+'.colorIfFalseG')
		pm.connectAttr(offAttributes[2],condOnOff+'.colorIfFalseB')
		pm.connectAttr(onAttributes[1],condOnOff+'.colorIfTrueG')
		pm.connectAttr(onAttributes[2],condOnOff+'.colorIfTrueB')
		return [condOnOff+'.outColorR', condOnOff+'.outColorG', condOnOff+'.outColorB']

	return condOnOff+'.outColorR'

def createSlimAxisTest( name, choosenAxisAtt, axisNum, attIfAxis, attIfNotAxis ):
	condSlimAxisIsAxisNum = pm.createNode('condition',n=name+'#') #translateValueIfSlimAxisX
	pm.connectAttr(choosenAxisAtt, condSlimAxisIsAxisNum+'.firstTerm')
	pm.setAttr( condSlimAxisIsAxisNum+'.secondTerm',axisNum)
	pm.connectAttr( attIfAxis, condSlimAxisIsAxisNum+'.colorIfTrueR')
	pm.connectAttr( attIfNotAxis, condSlimAxisIsAxisNum+'.colorIfFalseR')
	return condSlimAxisIsAxisNum+'.outColorR'

def FTV_createValueVectorWithSlimCond( transformationName, slimAxisChooserAtt, attSlimAxisOnOff, sourceValues, defaultValues, doPutDefaultOnAxis  ):
	condIsSlim = pm.createNode('condition',n='ifUseTexture'+transformationName+'OnSlimAxisCond#')
	# if attSlimAxisOnOff is On then it is normal
	# slimAxisOffVectorBuild is a vector, 1 means normal value, 0 meansdefault
	pm.connectAttr(attSlimAxisOnOff, condIsSlim+'.firstTerm')
	pm.setAttr(condIsSlim+'.secondTerm',1)
	colorIfTrueNames = ['colorIfTrueR','colorIfTrueG','colorIfTrueB']
	colorIfFalseNames = ['colorIfFalseR','colorIfFalseG','colorIfFalseB']
	axisName = ['X','Y','Z']
	for i in range(3):
		slimAxisCoordinateOut = None
		if doPutDefaultOnAxis:
			slimAxisCoordinateOut = createSlimAxisTest(transformationName+'ValueChooserIfSlimAxisIs'+axisName[i], slimAxisChooserAtt, i, defaultValues[i], sourceValues[i])
		else :
			slimAxisCoordinateOut = createSlimAxisTest(transformationName+'ValueChooserIfSlimAxisIs'+axisName[i], slimAxisChooserAtt, i, sourceValues[i], defaultValues[i])
		pm.connectAttr(sourceValues[i],condIsSlim+'.'+colorIfTrueNames[i])
		pm.connectAttr(slimAxisCoordinateOut,condIsSlim+'.'+colorIfFalseNames[i])

	return [condIsSlim+'.outColorR', condIsSlim+'.outColorG', condIsSlim+'.outColorB']


def FTV_setupTextureSpacesAndAttributes(vizuFluidTrans, vizuFluidShape, fluidSourceShape):
#to convert fluid texture values to 3D space, we need to multiply them by 80/freq
	gpTextureSpace = pm.group(em=True, n='textureSpace#')

	multTextSpaceScale = pm.createNode('multiplyDivide',n='textureTo3DSpaceConstantConvert#')
	pm.setAttr(multTextSpaceScale+'.input1X', 80)
	pm.connectAttr(fluidSourceShape+'.frequency',multTextSpaceScale+'.input2X')
	pm.setAttr(multTextSpaceScale+'.operation',2)
	textureSpaceTo3DMultiplicator = multTextSpaceScale+'.outputX'
	pm.connectAttr( textureSpaceTo3DMultiplicator, gpTextureSpace+'.scaleX')
	pm.connectAttr( textureSpaceTo3DMultiplicator, gpTextureSpace+'.scaleY')
	pm.connectAttr( textureSpaceTo3DMultiplicator, gpTextureSpace+'.scaleZ')
	pm.setAttr(gpTextureSpace+'.v', False)
	FTV_lockAndHide( gpTextureSpace, ['tx','ty','tz','rx','ry','rz','v'])

# Dealing with texture Scale And Rotate
	gpTextureRotateScale = pm.group(em=True, n='textureRotateAndScale#')

	# Texture Scale, first we may want to view the texture Scale except on the slim Axis for clearer viewing purpose (this is toggle by 'applyScaleOnSlimAxis'),
	# so we have to deal with all axis combinaisons, then we deal with a global toggle viewTextureScale between previous calculated values and the default values
	sourceScaleAtts = [fluidSourceShape+'.textureScaleX',fluidSourceShape+'.textureScaleY',fluidSourceShape+'.textureScaleZ']
	defaultScaleAtts = [vizuFluidShape+'.textureDefaultScaleX',vizuFluidShape+'.textureDefaultScaleY',vizuFluidShape+'.textureDefaultScaleZ']

	vectorValueIfScaleOnSlim = FTV_createValueVectorWithSlimCond('scale',vizuFluidShape+'.slimAxis',vizuFluidShape+'.applyScaleOnSlimAxis',sourceScaleAtts,defaultScaleAtts,True )
	outTextureScale = FTV_createValueToggle(vizuFluidShape+'.viewTextureScale',defaultScaleAtts,vectorValueIfScaleOnSlim)

	pm.connectAttr( outTextureScale[0], gpTextureRotateScale+'.scaleX')
	pm.connectAttr( outTextureScale[1], gpTextureRotateScale+'.scaleY')
	pm.connectAttr( outTextureScale[2], gpTextureRotateScale+'.scaleZ')

	# Texture Rotate
	# Texture Rotate, is a bit more simple, we just use viewTextureRotate to toggle between source Fluid Rotate or default Rotate values on Controller
	# Trying to reduce the rotation to view them in a plane doesn't provide a good representative information about the source rotation to make an animation for example

	sourceRotateAtts = [fluidSourceShape+'.textureRotateX',fluidSourceShape+'.textureRotateY',fluidSourceShape+'.textureRotateZ']
	defaultRotateAtts = [vizuFluidShape+'.textureDefaultRotateX',vizuFluidShape+'.textureDefaultRotateY',vizuFluidShape+'.textureDefaultRotateZ']
	outTextureRotate = FTV_createValueToggle(vizuFluidShape+'.viewTextureRotate',defaultRotateAtts, sourceRotateAtts)
	pm.connectAttr(outTextureRotate[0], gpTextureRotateScale+'.rotateX')
	pm.connectAttr(outTextureRotate[1], gpTextureRotateScale+'.rotateY')
	pm.connectAttr(outTextureRotate[2], gpTextureRotateScale+'.rotateZ')

	FTV_lockAndHide( gpTextureRotateScale, ['tx','ty','tz','v'])
	pm.parent(gpTextureRotateScale,gpTextureSpace,r=True)

# Dealing with Texture Origin

	locOrigin = pm.spaceLocator(n='fluidTextureOrigin#')
	pm.parent( locOrigin , gpTextureRotateScale, r=True)

	sourceTranslateAtts = [fluidSourceShape+'.textureOriginX',fluidSourceShape+'.textureOriginY',fluidSourceShape+'.textureOriginZ']
	defaultTranslateAtts = [vizuFluidShape+'.textureDefaultOriginX',vizuFluidShape+'.textureDefaultOriginY',vizuFluidShape+'.textureDefaultOriginZ']
	
	vectorValueIfTranslateOnSlim = FTV_createValueVectorWithSlimCond('translate',vizuFluidShape+'.slimAxis',vizuFluidShape+'.applyOriginOnSlimAxis',sourceTranslateAtts,defaultTranslateAtts,True )
	outSourceTextureOrigin = FTV_createValueToggle(vizuFluidShape+'.viewTextureOrigin',defaultTranslateAtts,vectorValueIfTranslateOnSlim)
	pm.connectAttr(outSourceTextureOrigin[0], locOrigin+'.tx')
	pm.connectAttr(outSourceTextureOrigin[1], locOrigin+'.ty')
	pm.connectAttr(outSourceTextureOrigin[2], locOrigin+'.tz')


	# potential texture offset due to a translate of the texture Viewer
	# this locator position will be the offset in texture origin due to the vizualiser position, so it will be added anyway to the final result
	loc = pm.spaceLocator(n='offsetOriginTexture#')
	pm.pointConstraint(vizuFluidTrans, loc)
	pm.parent( loc , gpTextureRotateScale, r=True)

	#then add this to the texture Origin
	minus = pm.createNode('plusMinusAverage',n='VizuPosOffsetMinusTextureOrigin#')
	pm.connectAttr(loc+'.translate',minus+'.input3D[0]')
	pm.connectAttr(locOrigin+'.translate',minus+'.input3D[1]')
	pm.setAttr( minus+'.operation', 1)
	outFinalTextureOrigin = [ minus+'.output3Dx',minus+'.output3Dy',minus+'.output3Dz' ]

# And we are going to create a group controlled by the texture rotation to be the parent of the vizualizer
	gpRotateTextureVizualizer = pm.group(em=True, n='textureVizualizerRotate#')
	FTV_lockAndHide( gpRotateTextureVizualizer, ['tx','ty','tz','sx','sy','sz','v'])

# Then we need also to recreate the implode space
# Implode space take the texture Rotate and also a special scale of 5
# We are going to translate the visualizer Pos into his space to offset correctly the value of the Implode Position
	gpImplodeSpace = pm.group(em=True, n='textureImplodeSpace#')
	pm.setAttr(gpImplodeSpace+'.sx',5)
	pm.setAttr(gpImplodeSpace+'.sy',5)
	pm.setAttr(gpImplodeSpace+'.sz',5)
	locImplOffset = pm.spaceLocator(n='offsetImplode#')
	pm.pointConstraint(vizuFluidTrans, locImplOffset)
	pm.parent( locImplOffset , gpImplodeSpace, r=True)
	pm.setAttr( gpImplodeSpace+'.v', False)
	FTV_lockAndHide( gpImplodeSpace, ['tx','ty','tz','v'])
	FTV_lockAndHide( gpImplodeSpace, ['sx','sy','sz'], True)

	minusImpl = pm.createNode('plusMinusAverage',n='VizuImplOffsetMinusSourceImplode#')
	pm.connectAttr(fluidSourceShape+'.implodeCenter',minusImpl+'.input3D[0]')
	pm.connectAttr(locImplOffset+'.translate',minusImpl+'.input3D[1]')
	pm.setAttr( minusImpl+'.operation', 2) # SUB
	outFinalImplodeCenter = [ minusImpl+'.output3Dx',minusImpl+'.output3Dy',minusImpl+'.output3Dz' ]

	#we also create the on/off for implode
	outImplode = FTV_createValueToggle(vizuFluidShape+'.viewImplode',[vizuFluidShape+'.defaultImplode'], [fluidSourceShape+'.implode'])

# we also create a toggle for texture time
	outTextureTime = FTV_createValueToggle(vizuFluidShape+'.viewTextureTime',[vizuFluidShape+'.defaultTextureTime'], [fluidSourceShape+'.textureTime'])


# Finally, here, we reconnect all the values to VizuFluid, or the parent of vizufluid
	pm.connectAttr( outTextureScale[0], vizuFluidShape+'.textureScaleX')
	pm.connectAttr( outTextureScale[1], vizuFluidShape+'.textureScaleY')
	pm.connectAttr( outTextureScale[2], vizuFluidShape+'.textureScaleZ')

	pm.connectAttr( outTextureRotate[0], gpRotateTextureVizualizer+'.rotateX')
	pm.connectAttr( outTextureRotate[1], gpRotateTextureVizualizer+'.rotateY')
	pm.connectAttr( outTextureRotate[2], gpRotateTextureVizualizer+'.rotateZ')

	pm.connectAttr( outTextureRotate[0], gpImplodeSpace+'.rotateX')
	pm.connectAttr( outTextureRotate[1], gpImplodeSpace+'.rotateY')
	pm.connectAttr( outTextureRotate[2], gpImplodeSpace+'.rotateZ')

	pm.connectAttr( outFinalTextureOrigin[0], vizuFluidShape+'.textureOriginX')
	pm.connectAttr( outFinalTextureOrigin[1], vizuFluidShape+'.textureOriginY')
	pm.connectAttr( outFinalTextureOrigin[2], vizuFluidShape+'.textureOriginZ')

	pm.connectAttr( outFinalImplodeCenter[0], vizuFluidShape+'.implodeCenterX')
	pm.connectAttr( outFinalImplodeCenter[1], vizuFluidShape+'.implodeCenterY')
	pm.connectAttr( outFinalImplodeCenter[2], vizuFluidShape+'.implodeCenterZ')

	# connect the implode
	pm.connectAttr(outImplode, vizuFluidShape+'.implode')

	#connect the textureTime
	pm.connectAttr(outTextureTime, vizuFluidShape+'.textureTime')

	return gpTextureSpace, gpRotateTextureVizualizer, gpImplodeSpace


def FTV_setupMainControlAttributes( control, vizuFluidShape ):
	addMainAttributesToObject(control,True)
	FTV_multiConnectAutoKeyableNonLocked( control, vizuFluidShape, ['translateX','translateY','translateZ'])

def FTV_createFluidTextureViewer( fluid ):

	fluidSourceTrans, fluidSourceShape = FTV_getFluidElements( fluid )
	vizuFluidTrans  , vizuFluidShape   = FTV_createFluidDummy( fluidSourceTrans+'_textVizu#' )

	FTV_setDirectConnectionsFluidToTexture( fluidSourceShape, vizuFluidShape)

	fluidSpaceTransform = FTV_generateFluidTransformSpaceGrp( 'fldTransformSpace#', (fluidSourceTrans,fluidSourceShape))

	mainCtrl, bbNurbsCubeShape = FTV_createMainFluidTextViewControl( vizuFluidTrans,vizuFluidShape, fluidSpaceTransform )
	FTV_setupMainControlAttributes( mainCtrl, vizuFluidShape )
	pm.connectAttr( mainCtrl+'.displayFluidBounding',bbNurbsCubeShape+'.visibility' )
	pm.connectAttr( mainCtrl+'.displayFluidViewer',vizuFluidTrans+'.visibility' )

	gpTextureSpace, gpFluidVizuParent, gpImplodeSpace = FTV_setupTextureSpacesAndAttributes( vizuFluidTrans, vizuFluidShape, fluidSourceShape )
	pm.parent(gpTextureSpace,mainCtrl,r=True)
	pm.parent(gpImplodeSpace,mainCtrl,r=True)
	pm.parent(gpFluidVizuParent,mainCtrl,r=True)
	pm.parent(vizuFluidTrans,gpFluidVizuParent,r=True)

	rootVizuGroup = pm.group(em=True,n='fluidTextureViewer#')
	FTV_lockAndHide(rootVizuGroup, ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'])

	pm.parent(fluidSpaceTransform, rootVizuGroup,r=True)

	return mainCtrl, vizuFluidTrans, fluidSpaceTransform

if __name__ == "__main__":
	try:
		sel = pm.ls(sl=True)
		if not len(sel):
			raise FTV_msCommandException('Please select a fluid')
		cmdResult = FTV_createFluidTextureViewer( sel[0])
		pm.select(cmdResult[0], r=True)
	except FTV_msCommandException, e:
		pm.mel.error( e.message)