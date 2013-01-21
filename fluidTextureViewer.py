import pymel.core as pm

#TODO
'''
Placer le fluid sous le control 
Creer une vizualisation de la taille du fluid original
checker why Reso Mult change la size....
Creer un sous Grp avec les coordonnees de Texture rotation et scale
Creer un sous Grp translate qui est contraont au fluid translate
additioner ces valeurs de translate aux valeur du pos origin

'''
class FTV_msCommandException(Exception):
    def __init__(self,message):
        self.message = '[FTV] '+message
    
    def __str__(self):
        return self.message

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

def FTV_createFluidDummy( name ):
	fldShape = pm.createNode('fluidShape')
	par = pm.listRelatives(fldShape, p=True)
	fldTrans = par[0]

	pm.setAttr(fldShape+'.velocityMethod', 0)
	pm.setAttr(fldShape+'.densityMethod', 3)
	pm.setAttr(fldShape+'.opacityTexture', 1)
	pm.setAttr(fldShape+'.selfShadowing', 1)
	pm.setAttr(fldShape+'.boundaryDraw', 4)

	pm.setAttr(fldShape+'.primaryVisibility', 0)
	pm.setAttr(fldShape+'.receiveShadows', 0)
	pm.setAttr(fldShape+'.castsShadows', 0)

	fldShape.addAttr('sizeXOrig', dv=10)
	fldShape.addAttr('sizeYOrig', dv=10)
	fldShape.addAttr('sizeZOrig', dv=10)
	fldShape.addAttr('resoSlim', dv=3)
	fldShape.addAttr('resoXOrig', dv=10)
	fldShape.addAttr('resoYOrig', dv=10)
	fldShape.addAttr('resoZOrig', dv=10)
	fldShape.addAttr('slimAxis',at='enum',en='XAxis:YAxis:ZAxis:None:')
	fldShape.addAttr('resoMult', dv=1,min=.001)

	fldShape.addAttr('viewImplode', at='bool', dv=1)
	fldShape.addAttr('viewTextureTime', at='bool', dv=1)
	fldShape.addAttr('textureTranslateOnSlimAxis', at='bool', dv=0)
	fldShape.addAttr('textureScaleOnSlimAxis', at='bool', dv=0)
	fldShape.addAttr('viewTextureScale', at='bool', dv=1)
	fldShape.addAttr('viewTextureOrigin', at='bool', dv=1)
	fldShape.addAttr('viewTextureRotate', at='bool', dv=1)

	fldShape.addAttr('textureDefaultScaleX', dv=1.0)
	fldShape.addAttr('textureDefaultScaleY', dv=1.0)
	fldShape.addAttr('textureDefaultScaleZ', dv=1.0)
	fldShape.addAttr('textureDefaultOriginX', dv=0.0)
	fldShape.addAttr('textureDefaultOriginY', dv=0.0)
	fldShape.addAttr('textureDefaultOriginZ', dv=0.0)
	fldShape.addAttr('textureDefaultRotateX', dv=0.0)
	fldShape.addAttr('textureDefaultRotateY', dv=0.0)
	fldShape.addAttr('textureDefaultRotateZ', dv=0.0)
	

	pm.expression( s='float $res[];\n\nfloat $size[];\n\n\n\n$res[0] = resoXOrig * resoMult;\n\n$res[1] = resoYOrig * resoMult;\n\n$res[2] = resoZOrig * resoMult;\n\n\n\n$size[0] = sizeXOrig;\n\n$size[1] = sizeYOrig;\n\n$size[2] = sizeZOrig;\n\n\n\nfloat $ratio = $res[0] / $size[0];\nfloat $rezoSlim = resoSlim;\n\n\nif ( slimAxis != 3 )\n{\n\tif (($rezoSlim%2) != ( $res[int(slimAxis)] % 2 ))\n\t\t$rezoSlim += 1;\n\n\t$size[int(slimAxis)] = $rezoSlim/$ratio;\n\n\t$res[int(slimAxis)] = $rezoSlim;\n}\n\n\n\nresolutionW = $res[0];\n\nresolutionH = $res[1];\n\nresolutionD = $res[2];\n\n\ndimensionsW = $size[0];\ndimensionsH = $size[1];\ndimensionsD = $size[2];', o=fldShape, ae=True, uc=all)
	fldTrans = pm.rename( fldTrans, name )
	shps = pm.listRelatives(fldTrans, s=True)
	fldShape = shps[0]
	return (fldTrans,fldShape)

def FTV_connectFluidToTexture( fluidSource, vizuFluid ):
	pm.connectAttr ( fluidSource+'.resolutionW', vizuFluid+'.resoXOrig' )
	pm.connectAttr ( fluidSource+'.resolutionH', vizuFluid+'.resoYOrig' )
	pm.connectAttr ( fluidSource+'.resolutionD', vizuFluid+'.resoZOrig' )
	pm.connectAttr ( fluidSource+'.dimensionsW', vizuFluid+'.sizeXOrig' )
	pm.connectAttr ( fluidSource+'.dimensionsH', vizuFluid+'.sizeYOrig' )
	pm.connectAttr ( fluidSource+'.dimensionsD', vizuFluid+'.sizeZOrig' )

	# texture direct connections
	directAtts = ['invertTexture','amplitude','ratio','threshold','depthMax','frequency','frequencyRatio','inflection','billowDensity','spottyness','sizeRand','randomness','falloff','numWaves']
	for a in directAtts:
		pm.connectAttr ( fluidSource+'.'+a, vizuFluid+'.'+a )

	#pm.expression( s='textureType  = '+fluidSource+'.textureType ;\ninvertTexture = '+fluidSource+'.invertTexture;\namplitude = '+fluidSource+'.amplitude;\nratio = '+fluidSource+'.ratio;\nthreshold = '+fluidSource+'.threshold;\n\nfloat $scaleDefault[3] = {1.0,1.0,1.0};\nfloat $scale[3] = { $scaleDefault[0],$scaleDefault[1],$scaleDefault[2] };\n\nfloat $originDefault[3] = {0.0,0.0,0.0};\nfloat $origin[3] = { $originDefault[0],$originDefault[1],$originDefault[2] };\n\nfloat $rotateDefault[3] = {0.0,0.0,0.0};\nfloat $rotate[3] = { $rotateDefault[0],$rotateDefault[1],$rotateDefault[2] };\n\nfloat $defaultTextureTime = 0.0;\nfloat $defaultImplodeValue = 0.0;\n\nint $slimAxis = slimAxis;\n\n//------------------------ Texture Scale --------------------------\nif (viewTextureScale == 1)\n{\n\t$scale[0] = '+fluidSource+'.textureScaleX;\n\t$scale[1] = '+fluidSource+'.textureScaleY;\n\t$scale[2] = '+fluidSource+'.textureScaleZ;\n\tif (!textureTranslateOnSlimAxis)\n\t\t$scale[$slimAxis] = $scaleDefault[$slimAxis];\n}\ntextureScaleX = $scale[0];\ntextureScaleY = $scale[1];\ntextureScaleZ = $scale[2];\n\n//------------------------ Texture Origin --------------------------\nif (viewTextureOrigin == 1)\n{\n\t$origin[0] = '+fluidSource+'.textureOriginX;\n\t$origin[1] = '+fluidSource+'.textureOriginY;\n\t$origin[2] = '+fluidSource+'.textureOriginZ;\n\tif (!textureTranslateOnSlimAxis)\n\t\t$origin[$slimAxis] = $originDefault[$slimAxis];\n}\ntextureOriginX = $origin[0];\ntextureOriginY = $origin[1];\ntextureOriginZ = $origin[2];\n\n//------------------------ Texture Scale --------------------------\nif (viewTextureRotate == 1)\n{\n\t$rotate[0] = '+fluidSource+'.textureRotateX;\n\t$rotate[1] = '+fluidSource+'.textureRotateY;\n\t$rotate[2] = '+fluidSource+'.textureRotateZ;\n\tif (!textureTranslateOnSlimAxis)\n\t\t$rotate[$slimAxis] = $rotateDefault[$slimAxis];\n}\ntextureRotateX = $rotate[0];\ntextureRotateY = $rotate[1];\ntextureRotateZ = $rotate[2];\n\ndepthMax = '+fluidSource+'.depthMax;\nfrequency = '+fluidSource+'.frequency;\nfrequencyRatio = '+fluidSource+'.frequencyRatio;\ninflection = '+fluidSource+'.inflection;\n\nif (viewTextureTime == 1)\n\ttextureTime = '+fluidSource+'.textureTime;\nelse\n\ttextureTime = $defaultTextureTime;\n\nbillowDensity = '+fluidSource+'.billowDensity;\nspottyness = '+fluidSource+'.spottyness;\nsizeRand = '+fluidSource+'.sizeRand;\nrandomness = '+fluidSource+'.randomness;\nfalloff = '+fluidSource+'.falloff;\nnumWaves = '+fluidSource+'.numWaves;\n\nif (viewImplode == 1)\n\timplode = '+fluidSource+'.implode;\nelse\n\timplode = $defaultImplodeValue;', o=vizuFluid, ae=True, uc=all)

def FTV_generateFluidSpaceGrp( name, fluidSourceData):
	fluidSpaceTransform = pm.group( em=True, n=name )
	pm.parentConstraint(fluidSourceData[0], fluidSpaceTransform)
	pm.scaleConstraint(fluidSourceData[0], fluidSpaceTransform)
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
	circle = pm.circle( n='fluidTextureVizuCtrl#', c=(0,0,0), nr=(0,1,0), sw=360, r=1, ut=False,s=8, ch=False )
	pm.parent(circle[0],fluidSpaceTransform,r=True)

	size = 0.5
	ptList = [(-size,-size,-size), (size,-size,-size), (size,-size,size), (-size,-size,size), (-size,-size,-size), (-size,size,-size), (size,size,-size), (size,size,size), (-size,size,size), (-size,size,-size), (size,size,-size),(size,-size,-size),(size,-size,size),(size,size,size),(-size,size,size),(-size,-size,size)]
	cube = pm.curve( p = ptList, d=1, n='tempNameCubeNurbs#')

	grpDummyTransform = pm.group(em=True,n='dummyFluidSize#')
	pm.connectAttr( vizuFluidTrans+'.sizeXOrig', grpDummyTransform+'.scaleX')
	pm.connectAttr( vizuFluidTrans+'.sizeYOrig', grpDummyTransform+'.scaleY')
	pm.connectAttr( vizuFluidTrans+'.sizeZOrig', grpDummyTransform+'.scaleZ')

	circleShape = FTV_createTransformedGeometry(circle,'local', 'create',grpDummyTransform)
	cubeShape = FTV_createTransformedGeometry(cube,'local', 'create',grpDummyTransform)
	pm.setAttr(cubeShape+'.template',True)
	allCubeShapes = pm.listRelatives(cube,s=True)
	pm.parent(allCubeShapes, circle, add=True, s=True)
	pm.delete(cube)

	pm.parent(grpDummyTransform,fluidSpaceTransform,r=True)
	return circle[0]

def FTV_createValueToggle( attributeView, offAttributes, onAttributes):
	parts = attributeView.split('.')
	print parts
	condOnOff = pm.createNode('condition',n=parts[1]+'ValuesOnOff#')
	pm.connectAttr(attributeView, condOnOff+'.firstTerm')
	pm.setAttr( condOnOff+'.secondTerm',1)
	pm.connectAttr(offAttributes[0],condOnOff+'.colorIfFalseR')
	pm.connectAttr(offAttributes[1],condOnOff+'.colorIfFalseG')
	pm.connectAttr(offAttributes[2],condOnOff+'.colorIfFalseB')

	pm.connectAttr(onAttributes[0],condOnOff+'.colorIfTrueR')
	pm.connectAttr(onAttributes[1],condOnOff+'.colorIfTrueG')
	pm.connectAttr(onAttributes[2],condOnOff+'.colorIfTrueB')

	return [condOnOff+'.outColorR', condOnOff+'.outColorG', condOnOff+'.outColorB']

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


def FTV_createSourceTextureSpace(vizuFluidTrans, vizuFluidShape, fluidSourceShape):
	gpTextureSpace = pm.group(em=True, n='textureSpace#')

# Dealing with Texture Scale
	# Texture Scale, first we may want to view the texture Scale except on the slim Axis for clearer viewing purpose (this is toggle by 'textureScaleOnSlimAxis'),
	# so we have to deal with all axis combinaisons, then we deal with a global toggle viewTextureScale between previous calculated values and the default values
	sourceScaleAtts = [fluidSourceShape+'.textureScaleX',fluidSourceShape+'.textureScaleY',fluidSourceShape+'.textureScaleZ']
	defaultScaleAtts = [vizuFluidShape+'.textureDefaultScaleX',vizuFluidShape+'.textureDefaultScaleY',vizuFluidShape+'.textureDefaultScaleZ']

	vectorValueIfScaleOnSlim = FTV_createValueVectorWithSlimCond('scale',vizuFluidShape+'.slimAxis',vizuFluidShape+'.textureScaleOnSlimAxis',sourceScaleAtts,defaultScaleAtts,True )
	outTextureScale = FTV_createValueToggle(vizuFluidShape+'.viewTextureScale',defaultScaleAtts,vectorValueIfScaleOnSlim)

	#to convert fluid texture scale value to 3D space, we need to multiply them by 80/freq
	multTextSpaceScale = pm.createNode('multiplyDivide',n='textureTo3DSpaceConstantConvert#')
	pm.setAttr(multTextSpaceScale+'.input1X', 80)
	pm.connectAttr(fluidSourceShape+'.frequency',multTextSpaceScale+'.input2X')
	pm.setAttr(multTextSpaceScale+'.operation',2)
	textureSpaceTo3DMultiplicator = multTextSpaceScale+'.outputX'

	multDiv = pm.createNode('multiplyDivide',n='wantedTextureScaleTo3DSpace#')
	pm.setAttr( multDiv+'.operation', 1 )
	pm.connectAttr( textureSpaceTo3DMultiplicator, multDiv+'.input1X')
	pm.connectAttr( textureSpaceTo3DMultiplicator, multDiv+'.input1Y')
	pm.connectAttr( textureSpaceTo3DMultiplicator, multDiv+'.input1Z')
	pm.connectAttr( outTextureScale[0], multDiv+'.input2X')
	pm.connectAttr( outTextureScale[1], multDiv+'.input2Y')
	pm.connectAttr( outTextureScale[2], multDiv+'.input2Z')
	pm.connectAttr( multDiv+'.outputX', gpTextureSpace+'.sx')
	pm.connectAttr( multDiv+'.outputY', gpTextureSpace+'.sy')
	pm.connectAttr( multDiv+'.outputZ', gpTextureSpace+'.sz')

# Dealing with Texture Rotate

	# Texture Rotate, is a bit more simple, we just use viewTextureRotate to toggle between source Fluid Rotate or default Rotate values on Controller
	# Trying to reduce the rotation to view them in a plane doesn't provide a good representative information about the source rotation to make an animation for example
	gpRotTextureSpace = pm.group(em=True,n='textureSpaceRotate#')
	pm.parent(gpRotTextureSpace,gpTextureSpace,r=True)
	sourceRotateAtts = [fluidSourceShape+'.textureRotateX',fluidSourceShape+'.textureRotateY',fluidSourceShape+'.textureRotateZ']
	defaultRotateAtts = [vizuFluidShape+'.textureDefaultRotateX',vizuFluidShape+'.textureDefaultRotateY',vizuFluidShape+'.textureDefaultRotateZ']
	outTextureRotate = FTV_createValueToggle(vizuFluidShape+'.viewTextureRotate',defaultRotateAtts, sourceRotateAtts)
	pm.connectAttr(outTextureRotate[0], gpRotTextureSpace+'.rotateX')
	pm.connectAttr(outTextureRotate[1], gpRotTextureSpace+'.rotateY')
	pm.connectAttr(outTextureRotate[2], gpRotTextureSpace+'.rotateZ')

# Dealing with Texture Origin

	# this locator position will be the offset in texture origin due to the vizualiser position, so it will be added anyway to the final result
	loc = pm.spaceLocator(n='offsetOriginTexture#')
	pm.pointConstraint(vizuFluidTrans, loc)
	pm.parent( loc , gpRotTextureSpace, r=True)

	# locSource is the actual origin of the source fluid texture, and locDefault will represent the default origin values choosen for vizu
	locSource = pm.spaceLocator(n='sourceFluidOrigin#')
	pm.connectAttr(fluidSourceShape+'.textureOriginX', locSource+'.tx')
	pm.connectAttr(fluidSourceShape+'.textureOriginY', locSource+'.ty')
	pm.connectAttr(fluidSourceShape+'.textureOriginZ', locSource+'.tz')
	pm.parent( locSource , gpRotTextureSpace, r=True)

	locDefault = pm.spaceLocator(n='defaultOrigin#')
	pm.connectAttr(vizuFluidShape+'.textureDefaultOriginX', locDefault+'.tx')
	pm.connectAttr(vizuFluidShape+'.textureDefaultOriginY', locDefault+'.ty')
	pm.connectAttr(vizuFluidShape+'.textureDefaultOriginZ', locDefault+'.tz')
	pm.parent( locDefault , gpRotTextureSpace, r=True)

	# then because we are dealing with the vizualizer and the slim Axis is choosen before rotate we need to convert this in non-rotated texture space (we need also to convert the default chosen for textureOrigin)
	locSourceNonRotated = pm.spaceLocator(n='sourceFluidOriginNonRotated#')
	pm.parent( locSourceNonRotated , gpTextureSpace, r=True)
	pm.pointConstraint(locSource,locSourceNonRotated)
	locDefaultNonRotated = pm.spaceLocator(n='defaultOriginNonRotated#')
	pm.parent( locDefaultNonRotated , gpTextureSpace, r=True)
	pm.pointConstraint(locDefault,locDefaultNonRotated)

	# and remove the coordinate according to slimAxis choice
	locInVizuPlan = pm.spaceLocator(n='sourceFluidNonRotatedOriginInVizuPlan#')
	pm.parent( locInVizuPlan , gpTextureSpace, r=True)

	sourceTranslateAtts = [locSourceNonRotated+'.tx',locSourceNonRotated+'.ty',locSourceNonRotated+'.tz']
	defaultTranslateAtts = [locDefaultNonRotated+'.tx',locDefaultNonRotated+'.ty',locDefaultNonRotated+'.tz']
	
	vectorValueIfTranslateOnSlim = FTV_createValueVectorWithSlimCond('translate',vizuFluidShape+'.slimAxis',vizuFluidShape+'.textureTranslateOnSlimAxis',sourceTranslateAtts,defaultTranslateAtts,True )
	outTextureOriginNonRotated = FTV_createValueToggle(vizuFluidShape+'.viewTextureOrigin',defaultTranslateAtts,vectorValueIfTranslateOnSlim)
	pm.connectAttr(outTextureOriginNonRotated[0], locInVizuPlan+'.tx')
	pm.connectAttr(outTextureOriginNonRotated[1], locInVizuPlan+'.ty')
	pm.connectAttr(outTextureOriginNonRotated[2], locInVizuPlan+'.tz')

	# and we translate this back to the rotated space of the texture
	locFinalVizuOrigin = pm.spaceLocator(n='finalVizuOriginTexture#')
	pm.parent( locFinalVizuOrigin , gpRotTextureSpace, r=True)
	pm.pointConstraint(locInVizuPlan,locFinalVizuOrigin)

	#then add this to the Vizualizer offset
	minus = pm.createNode('plusMinusAverage',n='VizuPosOffsetMinusFinalTextureOrigin#')
	pm.connectAttr(loc+'.translate',minus+'.input3D[0]')
	pm.connectAttr(locFinalVizuOrigin+'.translate',minus+'.input3D[1]')
	pm.setAttr( minus+'.operation', 1)

# Here we reconnect all the values to VizuFluid
	pm.connectAttr( outTextureScale[0], vizuFluidShape+'.textureScaleX')
	pm.connectAttr( outTextureScale[1], vizuFluidShape+'.textureScaleY')
	pm.connectAttr( outTextureScale[2], vizuFluidShape+'.textureScaleZ')
	pm.connectAttr( outTextureRotate[0], vizuFluidShape+'.textureRotateX')
	pm.connectAttr( outTextureRotate[1], vizuFluidShape+'.textureRotateY')
	pm.connectAttr( outTextureRotate[2], vizuFluidShape+'.textureRotateZ')
	pm.connectAttr( minus+'.output3Dx', vizuFluidShape+'.textureOriginX')
	pm.connectAttr( minus+'.output3Dy', vizuFluidShape+'.textureOriginY')
	pm.connectAttr( minus+'.output3Dz', vizuFluidShape+'.textureOriginZ')

	return gpTextureSpace


def FTV_multiConnect(src, dest, atts):
	for a in atts:
		pm.connectAttr( src+'.'+a, dest+'.'+a)

def FTV_setupMainControlAttributes( control, vizuFluidShape ):
	control.addAttr('resoMult', k=True,dv=1.0,min=.001)
	control.addAttr('slimAxis', k=True, at='enum', en='XAxis:YAxis:ZAxis:None:')
	control.addAttr('resoSlim', k=True,dv=3.0)
	control.addAttr('textureTranslateOnSlimAxis', k=True,at='bool', dv=False)
	control.addAttr('textureScaleOnSlimAxis', k=True, at='bool', dv=False)
	control.addAttr('viewImplode', k=True,at='bool', dv=True)
	control.addAttr('viewTextureTime', k=True,at='bool', dv=True)
	control.addAttr('viewTextureScale', k=True,at='bool', dv=True)
	control.addAttr('viewTextureOrigin', k=True,at='bool', dv=True)
	control.addAttr('viewTextureRotate', k=True,at='bool', dv=True)
	FTV_multiConnect( control, vizuFluidShape, ['resoMult','slimAxis','resoSlim','viewImplode','viewTextureTime','textureTranslateOnSlimAxis','textureScaleOnSlimAxis','viewTextureScale','viewTextureRotate','viewTextureOrigin'])

def FTV_createFluidTextureVizualizer( fluid ):
	fluidSourceTrans,fluidSourceShape = FTV_getFluidElements( fluid )
	vizuFluidTrans, vizuFluidShape  = FTV_createFluidDummy( fluidSourceTrans+'_textVizu#' )

	FTV_connectFluidToTexture( fluidSourceShape, vizuFluidShape)
	fluidSpaceTransform = FTV_generateFluidSpaceGrp( 'fldTextSpace#', (fluidSourceTrans,fluidSourceShape))

	mainCtrl = FTV_createMainFluidTextViewControl( vizuFluidTrans,vizuFluidShape, fluidSpaceTransform )
	pm.parent(vizuFluidTrans,mainCtrl,r=True)
	FTV_setupMainControlAttributes( mainCtrl, vizuFluidShape )

	gpTextureSpace = FTV_createSourceTextureSpace( vizuFluidTrans, vizuFluidShape, fluidSourceShape )
	pm.parent(gpTextureSpace,mainCtrl,r=True)

if __name__ == "__main__":
	try:
		sel = pm.ls(sl=True)
		if not len(sel):
			raise FTV_msCommandException('Please select a fluid')
		FTV_createFluidTextureVizualizer( sel[0])
	except FTV_msCommandException, e:
		pm.mel.error( e.message)