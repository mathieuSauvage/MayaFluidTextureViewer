'''
================================================================================
* VERSION 1.0
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
This is a Maya python script that generate a rig to view the texture from a
fluid. Please see the full description at the INTERNET SOURCE.
================================================================================
* USAGE:
- select a fluid then copy/paste this into a Maya python script editor and
execute it.
- put the script into a python script folder that Maya know, then use an import
command to use the script and call the main function with appropriate parameters.  
================================================================================
* TODO:
- [MAYBE NOT NEEDED] still need to offset the resolution of a slim Axis by one
  if resoSlim and original resolution of Axis are even/uneven
- check what's up with the cycles (seems more like a Maya issue...)
================================================================================
'''

import pymel.core as pm

class FTV_msCommandException(Exception):
    def __init__(self,message):
        self.message = '[FTV] '+message
    
    def __str__(self):
        return self.message

def FTV_multiConnectAutoKeyableNonLocked(src, dest, attsExcept):
	'''connect every keyable and non locked attribute of src to dest (basically connect parameters from control)'''
	atts = pm.listAttr(src, k=True, u=True)
	for a in atts:
		if a in attsExcept:
			continue
		pm.connectAttr(src+'.'+a, dest+'.'+a)

def FTV_lockAndHide( obj, atts, keyable=False ):
	'''lock and hide (if keyable is set to False) the list of attribute atts on objec obj'''
	for att in atts:
		pm.setAttr(obj+'.'+att, lock=True, k=keyable)

def FTV_getFluidElements( fluid ):
	'''this function consider the type of parameter fluid to not be exactly known but output anyway the fluid Transform and the fluid Shape'''

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

def addMainAttributesToObject( obj, keyable ):
	''' the main attributes are attributes that will be keyable on the controller '''
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
	obj.addAttr('applyOriginOnSlimAxis', k=keyable,at='bool', dv=True)
	obj.addAttr('applyScaleOnSlimAxis', k=keyable, at='bool', dv=True)
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

def FTV_createSystemInputsGrp( sourceFluidShape ):
	''' create the group that gather alls inputs for the rig, inputs from controller, inputs from source fluid etc...'''
	inGp = pm.group(em=True, n='systemInputs#')
	#add the control Inputs
	addMainAttributesToObject(inGp, False)

	# add attributes from source fluids that will be direct inputs
	atts = ['resolutionW','resolutionH','resolutionD','dimensionsW','dimensionsH','dimensionsD', 'textureRotateX','textureRotateY','textureRotateZ', 'textureScaleX', 'textureScaleY','textureScaleZ','textureOriginX','textureOriginY','textureOriginZ','implode','implodeCenterX','implodeCenterY','implodeCenterZ','textureTime','textureType','invertTexture','amplitude','ratio','threshold','depthMax','frequency','frequencyRatio','inflection','billowDensity','spottyness','sizeRand','randomness','falloff','numWaves' ]
	for a in atts :
		inGp.addAttr( a, k=False )
		pm.connectAttr( sourceFluidShape+'.'+a , inGp+'.'+a)

	FTV_lockAndHide( inGp, ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'])

	return inGp

def FTV_createViewerFluid( name, inputsGrp ):
	''' create the fluid that will display the texture, a simple fluid with nothing dynamic '''
	fldShape = pm.createNode('fluidShape')
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

	directAtts = ['textureType','invertTexture','amplitude','ratio','threshold','depthMax','frequency','frequencyRatio','inflection','billowDensity','spottyness','sizeRand','randomness','falloff','numWaves']
	for a in directAtts:
		pm.connectAttr ( inputsGrp+'.'+a, fldShape+'.'+a )

	pm.connectAttr(inputsGrp+'.textureGain',fldShape+'.opacityTexGain')
	pm.connectAttr(inputsGrp+'.textureGain',fldShape+'.colorTexGain')
	pm.connectAttr(inputsGrp+'.textureGain',fldShape+'.incandTexGain')
	pm.connectAttr(inputsGrp+'.textureOpacityPreviewGain',fldShape+'.opacityPreviewGain')
	
# calculations of the sizes and resolutions for the vizualizer depending on slimAxis chosen and resolution multiplier etc...

	# ratios resolution/dimension for every axis of the source fluid
	ratioResoSize = pm.createNode('multiplyDivide',n='ratioResoSize#')
	pm.setAttr( ratioResoSize+'.operation', 2 )
	pm.connectAttr( inputsGrp+'.resolutionW', ratioResoSize+'.input1X' )
	pm.connectAttr( inputsGrp+'.resolutionH', ratioResoSize+'.input1Y' )
	pm.connectAttr( inputsGrp+'.resolutionD', ratioResoSize+'.input1Z' )
	pm.connectAttr( inputsGrp+'.dimensionsW', ratioResoSize+'.input2X' )
	pm.connectAttr( inputsGrp+'.dimensionsH', ratioResoSize+'.input2Y' )
	pm.connectAttr( inputsGrp+'.dimensionsD', ratioResoSize+'.input2Z' )

	# the size of every axis if they where slim axis ( ratio*resoSlim )
	dividSlimResoByRatio = pm.createNode('multiplyDivide',n='slimAxisRatioToWidth#')
	pm.setAttr( dividSlimResoByRatio+'.operation', 2 )
	pm.connectAttr( inputsGrp+'.resoSlim', dividSlimResoByRatio+'.input1X' )
	pm.connectAttr( inputsGrp+'.resoSlim', dividSlimResoByRatio+'.input1Y' )
	pm.connectAttr( inputsGrp+'.resoSlim', dividSlimResoByRatio+'.input1Z' )
	pm.connectAttr( ratioResoSize+'.outputX', dividSlimResoByRatio+'.input2X' )
	pm.connectAttr( ratioResoSize+'.outputY', dividSlimResoByRatio+'.input2Y' )
	pm.connectAttr( ratioResoSize+'.outputZ', dividSlimResoByRatio+'.input2Z' )

	# with the switch depending on the chosen slimAxis we output the correct values to dimensions and resolutions
	outDimX = createSlimAxisTest( 'dimensionX', inputsGrp+'.slimAxis', 0, dividSlimResoByRatio+'.outputX', inputsGrp+'.dimensionsW' )
	outDimY = createSlimAxisTest( 'dimensionY', inputsGrp+'.slimAxis', 1, dividSlimResoByRatio+'.outputY', inputsGrp+'.dimensionsH' )
	outDimZ = createSlimAxisTest( 'dimensionZ', inputsGrp+'.slimAxis', 2, dividSlimResoByRatio+'.outputZ', inputsGrp+'.dimensionsD' )
	pm.connectAttr(outDimX, fldShape+'.dimensionsW')
	pm.connectAttr(outDimY, fldShape+'.dimensionsH')
	pm.connectAttr(outDimZ, fldShape+'.dimensionsD')

	outResX = createSlimAxisTest( 'resolutionX', inputsGrp+'.slimAxis', 0, inputsGrp+'.resoSlim', inputsGrp+'.resolutionW' )
	outResY = createSlimAxisTest( 'resolutionY', inputsGrp+'.slimAxis', 1, inputsGrp+'.resoSlim', inputsGrp+'.resolutionH' )
	outResZ = createSlimAxisTest( 'resolutionZ', inputsGrp+'.slimAxis', 2, inputsGrp+'.resoSlim', inputsGrp+'.resolutionD' )
	
	multResoViewer = pm.createNode('multiplyDivide',n='viewerResolutionMult#')
	pm.connectAttr( inputsGrp+'.resoMult', multResoViewer+'.input1X' )
	pm.connectAttr( inputsGrp+'.resoMult', multResoViewer+'.input1Y' )
	pm.connectAttr( inputsGrp+'.resoMult', multResoViewer+'.input1Z' )
	pm.connectAttr( outResX, multResoViewer+'.input2X' )
	pm.connectAttr( outResY, multResoViewer+'.input2Y' )
	pm.connectAttr( outResZ, multResoViewer+'.input2Z' )

	pm.connectAttr(multResoViewer+'.outputX', fldShape+'.resolutionW')
	pm.connectAttr(multResoViewer+'.outputY', fldShape+'.resolutionH')
	pm.connectAttr(multResoViewer+'.outputZ', fldShape+'.resolutionD')

	#lock of attributes
	FTV_lockAndHide(fldTrans, ['rx','ry','rz','sx','sy','sz'])

	return fldTrans,fldShape

def FTV_generateFluidTransformSpaceGrp( name, fluidSourceData):
	''' return a group that is fully constrained by fluidSourceData'''
	fluidSpaceTransform = pm.group( em=True, n=name )
	pm.parentConstraint(fluidSourceData[0], fluidSpaceTransform)
	pm.scaleConstraint(fluidSourceData[0], fluidSpaceTransform)
	FTV_lockAndHide(fluidSpaceTransform, ['v'])
	return fluidSpaceTransform

def FTV_createTransformedGeometry( objSrc, outShapeAtt, inShapeAtt, sourceTransform ):
	'''given a objSrc, duplicate its shape, then add a node to transform the original shape and output to the duplicated
	one. The shape can be a nurbs or a mesh so we specify the attributes to connect to the transform node with
	outShapeAtt and inShapeAtt and the appplies transformation is going to be the same as the node(group) sourceTransform'''
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

def FTV_createMainFluidTextViewControl( inputsGrp , fluidSpaceTransform):
	''' creation of the main control for the viewer'''
	circle = pm.circle( n='fluidTextureViewerCtrl#', c=(0,0,0), nr=(0,1,0), sw=360, r=1, ut=False,s=8, ch=False )
	pm.parent(circle[0],fluidSpaceTransform,r=True)

	size = 0.5
	ptList = [(-size,-size,-size), (size,-size,-size), (size,-size,size), (-size,-size,size), (-size,-size,-size), (-size,size,-size), (size,size,-size), (size,size,size), (-size,size,size), (-size,size,-size), (size,size,-size),(size,-size,-size),(size,-size,size),(size,size,size),(-size,size,size),(-size,-size,size)]
	cube = pm.curve( p = ptList, d=1, n='tempNameCubeNurbs#')

	grpDummyTransform = pm.group(em=True,n='dummyFluidSizeToMatrix#')

	pm.connectAttr( inputsGrp+'.dimensionsW', grpDummyTransform+'.scaleX')
	pm.connectAttr( inputsGrp+'.dimensionsH', grpDummyTransform+'.scaleY')
	pm.connectAttr( inputsGrp+'.dimensionsD', grpDummyTransform+'.scaleZ')
	FTV_lockAndHide( grpDummyTransform, ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'])

	circleShape = FTV_createTransformedGeometry(circle,'local', 'create',grpDummyTransform)
	cubeShape = FTV_createTransformedGeometry(cube,'local', 'create',grpDummyTransform)
	pm.setAttr(cubeShape+'.template',True)
	allCubeShapes = pm.listRelatives(cube,s=True)
	parentShapeRes = pm.parent(allCubeShapes, circle, add=True, s=True)

	pm.delete(cube)
	pm.rename( parentShapeRes[0],'BBFluidShapeSrc#' )
	retShape = pm.rename( parentShapeRes[1],'BBFluidShape#' )

	FTV_lockAndHide(circle[0], ['rx','ry','rz','sx','sy','sz','v'])

	# attributes connections
	addMainAttributesToObject(circle[0],True)
	FTV_multiConnectAutoKeyableNonLocked( circle[0], inputsGrp, ['translateX','translateY','translateZ'])

	pm.parent(grpDummyTransform,fluidSpaceTransform,r=True)

	return circle[0], retShape

def FTV_createValueToggle( attributeView, offAttributes, onAttributes):
	''' create a condition node if attributeView is True then output onAttributes else output offAttributes''' 
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
	''' create a condition : if choosenAxisAtt == axisNum then attIfAxis else attIfNotAxis  '''
	condSlimAxisIsAxisNum = pm.createNode('condition',n=name+'#') #translateValueIfSlimAxisX
	pm.connectAttr(choosenAxisAtt, condSlimAxisIsAxisNum+'.firstTerm')
	pm.setAttr( condSlimAxisIsAxisNum+'.secondTerm',axisNum)
	pm.connectAttr( attIfAxis, condSlimAxisIsAxisNum+'.colorIfTrueR')
	pm.connectAttr( attIfNotAxis, condSlimAxisIsAxisNum+'.colorIfFalseR')
	return condSlimAxisIsAxisNum+'.outColorR'

def FTV_createValueVectorWithSlimCond( transformationName, slimAxisChooserAtt, attSlimAxisOnOff, sourceValues, defaultValues, doPutDefaultOnAxis  ):
	'''create a vector which should ouput values of sourceValues but if slimAxisChooserAtt is not 4 (No Axis slim)
	and attSlimAxisOnOff is True then the corresponding Axis value will be picked from defaultValues'''
	condIsSlim = pm.createNode('condition',n='ifUseTexture'+transformationName+'OnSlimAxisCond#')
	# if attSlimAxisOnOff is On then it is normal
	# slimAxisOffVectorBuild is a vector, 1 means normal value, 0 means default
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


def FTV_setupTextureSpacesAndAttributes(vizuFluidTrans, vizuFluidShape, inputsGrp):
	'''this will setup the 3D spaces where the textures values are matching 3D space
	the base group, for example, is just the conversion multiplier, 80/freq
	we need this in order to make some space transformations and ouput back to the viewer
	texture parameters'''
	gpTextureSpace = pm.group(em=True, n='textureSpace#')

	multTextSpaceScale = pm.createNode('multiplyDivide',n='textureTo3DSpaceConstantConvert#')
	pm.setAttr(multTextSpaceScale+'.input1X', 80)
	pm.connectAttr(inputsGrp+'.frequency',multTextSpaceScale+'.input2X')
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
	sourceScaleAtts = [inputsGrp+'.textureScaleX',inputsGrp+'.textureScaleY',inputsGrp+'.textureScaleZ']
	defaultScaleAtts = [inputsGrp+'.textureDefaultScaleX',inputsGrp+'.textureDefaultScaleY',inputsGrp+'.textureDefaultScaleZ']

	vectorValueIfScaleOnSlim = FTV_createValueVectorWithSlimCond('scale',inputsGrp+'.slimAxis',inputsGrp+'.applyScaleOnSlimAxis',sourceScaleAtts,defaultScaleAtts,True )
	outTextureScale = FTV_createValueToggle(inputsGrp+'.viewTextureScale',defaultScaleAtts,vectorValueIfScaleOnSlim)

	pm.connectAttr( outTextureScale[0], gpTextureRotateScale+'.scaleX')
	pm.connectAttr( outTextureScale[1], gpTextureRotateScale+'.scaleY')
	pm.connectAttr( outTextureScale[2], gpTextureRotateScale+'.scaleZ')

	# Texture Rotate
	# Texture Rotate, is a bit more simple, we just use viewTextureRotate to toggle between source Fluid Rotate or default Rotate values on Controller
	# Trying to reduce the rotation to view them in a plane doesn't provide a good representative information about the source rotation to make an animation for example

	sourceRotateAtts = [inputsGrp+'.textureRotateX',inputsGrp+'.textureRotateY',inputsGrp+'.textureRotateZ']
	defaultRotateAtts = [inputsGrp+'.textureDefaultRotateX',inputsGrp+'.textureDefaultRotateY',inputsGrp+'.textureDefaultRotateZ']
	outTextureRotate = FTV_createValueToggle(inputsGrp+'.viewTextureRotate',defaultRotateAtts, sourceRotateAtts)
	pm.connectAttr(outTextureRotate[0], gpTextureRotateScale+'.rotateX')
	pm.connectAttr(outTextureRotate[1], gpTextureRotateScale+'.rotateY')
	pm.connectAttr(outTextureRotate[2], gpTextureRotateScale+'.rotateZ')

	FTV_lockAndHide( gpTextureRotateScale, ['tx','ty','tz','v'])
	pm.parent(gpTextureRotateScale,gpTextureSpace,r=True)

# Dealing with Texture Origin

	locOrigin = pm.spaceLocator(n='fluidTextureOrigin#')
	pm.parent( locOrigin , gpTextureRotateScale, r=True)

	sourceTranslateAtts = [inputsGrp+'.textureOriginX',inputsGrp+'.textureOriginY',inputsGrp+'.textureOriginZ']
	defaultTranslateAtts = [inputsGrp+'.textureDefaultOriginX',inputsGrp+'.textureDefaultOriginY',inputsGrp+'.textureDefaultOriginZ']
	
	vectorValueIfTranslateOnSlim = FTV_createValueVectorWithSlimCond('translate',inputsGrp+'.slimAxis',inputsGrp+'.applyOriginOnSlimAxis',sourceTranslateAtts,defaultTranslateAtts,True )
	outSourceTextureOrigin = FTV_createValueToggle(inputsGrp+'.viewTextureOrigin',defaultTranslateAtts,vectorValueIfTranslateOnSlim)
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
	pm.connectAttr(inputsGrp+'.implodeCenterX',minusImpl+'.input3D[0].input3Dx')
	pm.connectAttr(inputsGrp+'.implodeCenterY',minusImpl+'.input3D[0].input3Dy')
	pm.connectAttr(inputsGrp+'.implodeCenterZ',minusImpl+'.input3D[0].input3Dz')

	pm.connectAttr(locImplOffset+'.translate',minusImpl+'.input3D[1]')
	pm.setAttr( minusImpl+'.operation', 2) # SUB
	outFinalImplodeCenter = [ minusImpl+'.output3Dx',minusImpl+'.output3Dy',minusImpl+'.output3Dz' ]

# we also create a toggle for implode
	outImplode = FTV_createValueToggle(inputsGrp+'.viewImplode',[inputsGrp+'.defaultImplode'], [inputsGrp+'.implode'])

# we also create a toggle for texture time
	outTextureTime = FTV_createValueToggle(inputsGrp+'.viewTextureTime',[inputsGrp+'.defaultTextureTime'], [inputsGrp+'.textureTime'])

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

def FTV_setupFluidForceRefresh ( fluidShape,  atts ):
	''' a special expression to force the refresh of the fluid anytime we modify an input'''
	import re
	conns = pm.listConnections( fluidShape+'.voxelQuality', s=True, d=False, p=False  )
	expr = None
	text = None
	attributesTrigger = atts[:] #shallow copy

	if conns is not None and len(conns)>0 and fluidShape.hasAttr('voxelQualityChooser') :
		if pm.objectType( conns[0], isType='expression' ) == False:
			raise FTM_msCommandException('The fluid [ '+fluidShape+' ] has an incoming connection in attribute voxelQuality, unable to setup a refresh expression')
		expr = conns[0]
		text = pm.expression( expr, q=True, s=True)
	else:
		if len(conns)>0:
			raise FTM_msCommandException('The fluid [ '+fluidShape+' ] has an incoming connection in attribute voxelQuality, unable to setup a refresh expression')
		if fluidShape.hasAttr('voxelQualityChooser') == False:
			current = pm.getAttr( fluidShape+'.voxelQuality' )
			fluidShape.addAttr( 'voxelQualityChooser',  k=True, at='enum', en='faster=1:better=2', dv=current)

	if text is not None:
		#let's gather the trigger of refresh inside the expression
		matches = re.findall(r'.*?\$trigs\[size\(\$trigs\)\]=(.*?);', text )  #$triggers[0]=.I[0];
		for m in matches:
			if re.match( r'\.I\[[0-9]+?\]', m) is None:
				attributesTrigger.append(m)
	text  = '// Fluid display Refresh expression\n'
	text += '// you can add triggers here but you have to follow the current syntax\n'
	text += 'float $trigs[];clear $trigs;\n\n'
	for i in range(len(attributesTrigger)):
		text += '$trigs[size($trigs)]='+attributesTrigger[i]+';\n'
	text += '\n//Result\n'
	text += 'voxelQuality = voxelQualityChooser;\n'
	if expr :
		pm.expression( expr, e=True, s=text, o=fluidShape, ae=False)
	else:
		pm.expression( s=text, o=fluidShape, ae=True, n='forceFluidDisplayRefreshExpr#')

def FTV_createFluidTextureViewer( fluid ):
	'''
	create a viewer of fluid texture
	parameter fluid can be a fluid Transform or a fluidShape
	return the main control, the transform of the fluid of the viewer, the parent group of the rig  
	'''
	fluidSourceTrans, fluidSourceShape = FTV_getFluidElements( fluid )
	fluidSpaceTransform = FTV_generateFluidTransformSpaceGrp( 'fldTransformSpace#', (fluidSourceTrans,fluidSourceShape))

	grpSystemIn = FTV_createSystemInputsGrp( fluidSourceShape )
	mainCtrl, bbNurbsCubeShape = FTV_createMainFluidTextViewControl( grpSystemIn, fluidSpaceTransform )
	vizuFluidTrans  , vizuFluidShape   = FTV_createViewerFluid( fluidSourceTrans+'_textView#',grpSystemIn )

	pm.connectAttr( mainCtrl+'.displayFluidBounding',bbNurbsCubeShape+'.visibility' )
	pm.connectAttr( mainCtrl+'.displayFluidViewer',vizuFluidTrans+'.visibility' )

	gpTextureSpace, gpFluidVizuParent, gpImplodeSpace = FTV_setupTextureSpacesAndAttributes( vizuFluidTrans, vizuFluidShape, grpSystemIn )

	pm.parent(gpTextureSpace,mainCtrl,r=True)
	pm.parent(gpImplodeSpace,mainCtrl,r=True)
	pm.parent(gpFluidVizuParent,mainCtrl,r=True)
	pm.parent(vizuFluidTrans,gpFluidVizuParent,r=True)

	rootVizuGroup = pm.group(em=True,n='fluidTextureViewer#')
	FTV_lockAndHide(rootVizuGroup, ['tx','ty','tz','rx','ry','rz','sx','sy','sz'])

	pm.parent(fluidSpaceTransform, rootVizuGroup,r=True)
	pm.parent(grpSystemIn, rootVizuGroup,r=True)

	# for refresh purpose we make a list of attribute that trigger the refresh
	attsTriggers = grpSystemIn.listAttr(ud=True,u=True) # every unlocked dynamic attributes of systemInputs is a trigger (convenient)
	attsTriggers.append( vizuFluidTrans+'.tx')
	attsTriggers.append( vizuFluidTrans+'.ty')
	attsTriggers.append( vizuFluidTrans+'.tz')
	FTV_setupFluidForceRefresh( vizuFluidShape, attsTriggers )

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