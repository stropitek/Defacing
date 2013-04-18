import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import pdb

#
# Defacing
#

class Defacing:
  def __init__(self, parent):
    parent.title = "Defacing"
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Daniel Kostro (bwh)"]
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Daniel Kostro (bwh)
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['Defacing'] = self.runTest

  def runTest(self):
    tester = DefacingTest()
    tester.runTest()

#
# qDefacingWidget
#

class DefacingWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
      # self.parent = slicer.modules.cropvolume.widgetRepresentation()
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
      
      
  def setup(self):
    # Instantiate and connect widgets ...
    
    # Status text
    statusCollapsibleButton = ctk.ctkCollapsibleButton()
    statusCollapsibleButton.text = 'Status'
    self.layout.addWidget(statusCollapsibleButton)
    self.statusFormLayout = qt.QFormLayout(statusCollapsibleButton)

    self.overallStatus = qt.QLabel()
    self.overallStatus.text = 'Idle'
    self.statusFormLayout.addRow('New Process:',self.overallStatus)

    
    self.processes = list()
    #
    # Volumes
    #
    self.inputImagesCollapsibleButton = ctk.ctkCollapsibleButton()
    self.inputImagesCollapsibleButton.text = "Input Images"
    self.layout.addWidget(self.inputImagesCollapsibleButton)

    # Layout within the collapsible button
    inputImagesFormLayout = qt.QFormLayout(self.inputImagesCollapsibleButton)

    # input volume selector
    self.fixedVolumeSelector = slicer.qMRMLNodeComboBox()
    self.fixedVolumeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.fixedVolumeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.fixedVolumeSelector.selectNodeUponCreation = True
    self.fixedVolumeSelector.addEnabled = True
    self.fixedVolumeSelector.removeEnabled = True
    self.fixedVolumeSelector.noneEnabled = False
    self.fixedVolumeSelector.showHidden = False
    self.fixedVolumeSelector.showChildNodeTypes = False
    self.fixedVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.fixedVolumeSelector.setToolTip( "Pick the fixed input to the algorithm." )
    inputImagesFormLayout.addRow("Fixed Image Volume: ", self.fixedVolumeSelector)

    # Moving volume selector
    
    self.movingVolumeSelector = slicer.qMRMLCheckableNodeComboBox()
    
    # self.movingVolumeSelector = slicer.qMRMLNodeComboBox()
    self.movingVolumeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.movingVolumeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.movingVolumeSelector.selectNodeUponCreation = True
    self.movingVolumeSelector.addEnabled = True
    self.movingVolumeSelector.removeEnabled = True
    self.movingVolumeSelector.noneEnabled = False
    self.movingVolumeSelector.showHidden = False
    self.movingVolumeSelector.showChildNodeTypes = False
    self.movingVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.movingVolumeSelector.setToolTip( "Pick the moving volume to the algorithm." )
    inputImagesFormLayout.addRow("Moving Volume: ", self.movingVolumeSelector)
    
    
    #
    # Crop parameters
    #
    self.cropParametersCollapsibleButton = ctk.ctkCollapsibleButton()
    self.cropParametersCollapsibleButton.text = "Crop Parameters"
    self.layout.addWidget(self.cropParametersCollapsibleButton)
    cropParametersFormLayout = qt.QFormLayout(self.cropParametersCollapsibleButton)
    cropParametersFormLayout
    
    # Input ROI
    self.annotationROISelector = slicer.qMRMLNodeComboBox()
    self.annotationROISelector.nodeTypes = ( ("vtkMRMLAnnotationROINode"), "" )
    self.annotationROISelector.editEnabled = True;
    self.annotationROISelector.renameEnabled = True;
    self.annotationROISelector.setMRMLScene( slicer.mrmlScene )
    self.annotationROISelector.setToolTip( "Pick the fixed input to the algorithm." )
    cropParametersFormLayout.addRow("Input ROI: ", self.annotationROISelector)
    
    # ROI Visibility
    self.ROIVisibilityButton = qt.QToolButton();
    visibilityIcon = qt.QIcon();
    visibilityIcon.addPixmap(qt.QPixmap(':/Icons/VisibleOff.png'),qt.QIcon().Normal,qt.QIcon().Off)
    visibilityIcon.addPixmap(qt.QPixmap(':/Icons/VisibleOn.png'),qt.QIcon().Normal,qt.QIcon().On)
    self.ROIVisibilityButton.setIcon(visibilityIcon);
    self.ROIVisibilityButton.setCheckable(True)
    cropParametersFormLayout.addRow("Visibility ROI:", self.ROIVisibilityButton)
    
    # Cropping technique
    croppingTechniqueLayout = qt.QHBoxLayout();
    self.interpolationButton = qt.QRadioButton('Interpolated cropping')
    self.interpolationButton.setChecked(True)
    self.voxelBasedButton = qt.QRadioButton('Voxel based cropping')
    croppingTechniqueLayout.addWidget(self.interpolationButton)
    croppingTechniqueLayout.addWidget(self.voxelBasedButton)
    cropParametersFormLayout.addRow("Technique: ", croppingTechniqueLayout)
    
    # Interpolation options
    self.interpolationOptionsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
    self.interpolationOptionsCollapsibleGroupBox.title = "Interpolation options"
    cropParametersFormLayout.addRow('',self.interpolationOptionsCollapsibleGroupBox)
    interpolationOptionsLayout = qt.QFormLayout(self.interpolationOptionsCollapsibleGroupBox)
    interpolationOptionsLayout.setFieldGrowthPolicy(qt.QFormLayout().ExpandingFieldsGrow)
    interpolationOptionsLayout.setRowWrapPolicy(qt.QFormLayout().WrapLongRows)
    
    # Isotropic
    self.isotropicCheckBox = qt.QCheckBox();
    self.isotropicCheckBox.checked = True;
    interpolationOptionsLayout.addRow('Isotropic output voxel', self.isotropicCheckBox)
    
    # Input spacing scaling constant
    self.inputSpacingScaling = qt.QDoubleSpinBox()
    self.inputSpacingScaling.setToolTip('In not equal to 1, this will result in upsampling (&lt;1) or downlsampling (&gt;1) relative to the voxel spacing of the input volume.')
    self.inputSpacingScaling.value = 1.000000
    interpolationOptionsLayout.addRow('Input spacing scaling constant: ', self.inputSpacingScaling)
    
    # Interpolator technique
    interpolatorWidget = qt.QWidget()
    sizep = qt.QSizePolicy()
    sizep.setHorizontalPolicy(qt.QSizePolicy().Expanding)
    sizep.setVerticalPolicy(qt.QSizePolicy().Preferred)
    sizep.setHorizontalStretch(0)
    sizep.setVerticalStretch(0)
    interpolatorWidget.setSizePolicy(sizep)
    interpolatorLayout = qt.QGridLayout(interpolatorWidget);
    interpolationOptionsLayout.addRow("Technique: ", interpolatorWidget)
    self.iNNButton = qt.QRadioButton('Nearest Neighbor')
    self.iLinearButton = qt.QRadioButton('Linear')
    self.iWindowedSincButton = qt.QRadioButton('WindowedSinc')
    self.iBSplineButton = qt.QRadioButton('B-spline')
    self.iNNButton.setSizePolicy(qt.QSizePolicy().Minimum, qt.QSizePolicy().Preferred)
    self.iLinearButton.setSizePolicy(qt.QSizePolicy().MinimumExpanding, qt.QSizePolicy().Preferred)
    self.iWindowedSincButton.setSizePolicy(qt.QSizePolicy().Minimum, qt.QSizePolicy().Preferred)
    self.iBSplineButton.setSizePolicy(qt.QSizePolicy().MinimumExpanding, qt.QSizePolicy().Preferred)
    self.iLinearButton.setChecked(True)
    interpolatorLayout.addWidget(self.iNNButton,0,0)
    interpolatorLayout.addWidget(self.iLinearButton,0,1)
    interpolatorLayout.addWidget(self.iWindowedSincButton,1,0)
    interpolatorLayout.addWidget(self.iBSplineButton,1,1)
    
    #
    # Crop Button
    #
    self.cropButton = qt.QPushButton("Crop")
    self.cropButton.toolTip = "Crop the fixed volume."
    self.cropButton.enabled = False
    self.layout.addWidget(self.cropButton)
    
    # Align and crop
    self.alignAndCropButton = qt.QPushButton("Align and Crop")
    self.alignAndCropButton.toolTip = "Align moving volumes with fixed volume and crop all the images"
    self.alignAndCropButton.enabled = False
    self.layout.addWidget(self.alignAndCropButton)

    self.layout.addStretch(1)
    
    self.cropParametersNode = slicer.modulemrml.vtkMRMLCropVolumeParametersNode()
    
    self.onFixedVolumeSelect()
    self.onMovingVolumeSelect()
    self.onAnnotationROIChanged()
    self.onROIVisibilityChanged()

    # connections
    self.cropButton.connect('clicked(bool)', self.onCrop)
    self.alignAndCropButton.connect('clicked(bool)', self.onAlignAndCrop)
    self.fixedVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onFixedVolumeSelect)
    self.movingVolumeSelector.connect("checkedNodesChanged(void)", self.onMovingVolumeSelect)
    self.annotationROISelector.connect("currentNodeChanged(vtkMRMLNode*)",self.onAnnotationROIChanged)
    self.ROIVisibilityButton.connect("toggled(bool)", self.onROIVisibilityChanged)
    self.voxelBasedButton.connect('clicked(bool)', self.onVoxelBasedButtonClicked)
    self.interpolationButton.connect('clicked(bool)', self.onInterpolationButtonClicked)
    
    # Display current fixed node
    self.displayFixedVolume()
    
    self.updateCropParameters()
    
    self.outputNodes = dict()
    self.nreg_completed = 0
        
  def onFixedVolumeSelect(self):
    self.refreshActionButtons()
    self.displayFixedVolume()
    
  def onMovingVolumeSelect(self):
    self.refreshActionButtons()
    
  def refreshActionButtons(self):
    bval = self.cropParamValidity()
    self.cropButton.enabled = bval and self.fixedVolumeSelector.currentNode()
    self.alignAndCropButton.enabled = bval and self.fixedVolumeSelector.currentNode() and len(self.movingVolumeSelector.checkedNodes()) != 0
    
  def onAnnotationROIChanged(self):
    if self.annotationROISelector.currentNode():
      self.annotationROISelector.currentNode().SetDisplayVisibility(True)
      self.ROIVisibilityButton.setChecked(True)
    self.refreshActionButtons()

    
  def onROIVisibilityChanged(self):
    checked = self.ROIVisibilityButton.isChecked()
    if self.annotationROISelector.currentNode():
      self.annotationROISelector.currentNode().SetDisplayVisibility(checked)
      
  def onInterpolationButtonClicked(self, clicked):
    if clicked:
      self.interpolationOptionsCollapsibleGroupBox.setEnabled(True)
      self.interpolationOptionsCollapsibleGroupBox.collapsed = False
    self.refreshActionButtons()
      
  def onVoxelBasedButtonClicked(self, clicked):
    if clicked:
      self.interpolationOptionsCollapsibleGroupBox.setEnabled(False)
      self.interpolationOptionsCollapsibleGroupBox.collapsed = True
    self.refreshActionButtons()

  def updateCropParameters(self):
    if self.fixedVolumeSelector.currentNode():
      self.cropParametersNode.SetInputVolumeNodeID(self.fixedVolumeSelector.currentNode().GetID())
    else:
      self.cropParametersNode.SetInputVolumeNodeID(None)
      
    if self.annotationROISelector.currentNode():
      self.cropParametersNode.SetROINodeID(self.annotationROISelector.currentNode().GetID())
    else:
      self.cropParametersNode.SetROINodeID(None)
    
    if self.iNNButton.isChecked():
      self.cropParametersNode.SetInterpolationMode(1)
    elif self.iLinearButton.isChecked():
      self.cropParametersNode.SetInterpolationMode(2)
    elif self.iWindowedSincButton.isChecked():
      self.cropParametersNode.SetInterpolationMode(3)
    elif self.iBSplineButton.isChecked():
      self.cropParametersNode.SetInterpolationMode(4)
    
    if self.isotropicCheckBox.isChecked():
      self.cropParametersNode.SetIsotropicResampling(1)
    else:
      self.cropParametersNode.SetIsotropicResampling(0)
    
    self.cropParametersNode.SetSpacingScalingConst(self.inputSpacingScaling.value)
    self.cropParametersNode.SetROIVisibility(self.ROIVisibilityButton.isChecked())
    
    
  def cropParamValidity(self):
    if not self.annotationROISelector.currentNode():
      return False
    if not self.voxelBasedButton.isChecked() and not self.interpolationButton.isChecked():
      return False
    if self.interpolationButton.isChecked() and not self.iBSplineButton.isChecked() and not self.iNNButton.isChecked() and not self.iWindowedSincButton.isChecked() and not self.iLinearButton.isChecked():
      return False
    return True
    
  def runRegistration(self, movingVolumeNode):
    parameters = {}
    
    fixedVolumeNode = self.fixedVolumeSelector.currentNode()
    
    parameters['movingVolume'] = movingVolumeNode.GetID()
    parameters["fixedVolume"] = fixedVolumeNode.GetID()
    
    self.outputNodes[parameters['movingVolume']] = slicer.vtkMRMLScalarVolumeNode()
    self.outputNodes[parameters['movingVolume']].SetName(movingVolumeNode.GetName()+'_reg')
    slicer.mrmlScene.AddNode(self.outputNodes[parameters['movingVolume']])
    
    parameters["outputVolume"] = self.outputNodes[parameters['movingVolume']].GetID()
    # parameters["outputTransform"] = 
    # parameters["transformType"] = "Rigid"
    parameters["histogramMatch"] = True
    parameters["initializeTransformMode"] = "useMomentsAlign"
    parameters["interpolationMode"] = "Linear"
    parameters["maskProcessingMode"] = "ROIAUTO"
    reg = slicer.modules.brainsfit
    return (slicer.cli.run(reg,None,parameters,False))
    
  
  def onCrop(self):
    self.updateCropParameters()
    cropLogic = slicer.modules.cropvolume.logic()
    print("Run Crop")
    cropLogic.Apply(self.cropParametersNode)
    
  def onAlignAndCrop(self):
    self.toggleUiVisibility()
    cropLogic = slicer.modules.cropvolume.logic()
    self.updateCropParameters()
    print("Run Align and Crop")
    self.cropParametersNode.SetInputVolumeNodeID(self.fixedVolumeSelector.currentNode().GetID())
    cropLogic.Apply(self.cropParametersNode)
    
    for movingNode in self.movingVolumeSelector.checkedNodes():
      self.regCli = self.runRegistration(movingNode)
      self.regCli.AddObserver('ModifiedEvent', self.printStatus)
    
    
  def printStatus(self,caller, event):
    print("Got a %s from a %s. Status is: %s" % (event, caller.GetClassName(), caller.GetStatusString()))
    if caller.IsA('vtkMRMLCommandLineModuleNode'):
      if caller.GetParameterAsString('movingVolume'):
        if caller.GetStatusString() == 'Running':
          self.overallStatus.text = '1 Registration Running, '+ str(self.nreg_completed) + ' completed and ' + str(len(self.outputNodes)-self.nreg_completed-1) + ' remaining'
        if caller.GetStatusString() == 'Completed':
          self.nreg_completed += 1
          cropLogic = slicer.modules.cropvolume.logic()
          self.cropParametersNode.SetInputVolumeNodeID(self.outputNodes[caller.GetParameterAsString('movingVolume')].GetID())
          cropLogic.Apply(self.cropParametersNode)
          print('Cropped '+caller.GetParameterAsString('movingVolume'))
          perc = round(100*self.nreg_completed/len(self.outputNodes))
          if perc == 100:
            self.overallStatus.text = 'All ' + str(self.nreg_completed) + ' registrations completed'
            self.toggleUiVisibility()()
          else:
            self.overallStatus.text = str(self.nreg_completed) + ' registrations completed and ' + str(len(self.outputNodes)-self.nreg_completed-1) + ' remaining'
            
            
  def toggleUiVisibility(self):
    uiVisibility = not self.inputImagesCollapsibleButton.enabled
    self.inputImagesCollapsibleButton.enabled = uiVisibility
    self.cropParametersCollapsibleButton.enabled = uiVisibility
    self.cropButton.enabled = uiVisibility
    self.alignAndCropButton.enabled = uiVisibility
    if(uiVisibility):
      self.refreshActionButtons()
  
  def displayFixedVolume(self):
    if self.fixedVolumeSelector.currentNode():
      slicer.app.applicationLogic().GetSelectionNode().SetActiveVolumeID(self.fixedVolumeSelector.currentNode().GetID())
      slicer.app.applicationLogic().PropagateVolumeSelection(0)


#
# DefacingLogic
#

class DefacingLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that 
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def run(self,inputVolume,outputVolume):
    """
    Run the actual algorithm
    """
    return True


class DefacingTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_Defacing1()

  def test_Defacing1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """
    self.delayDisplay("Starting the test")
    self.delayDisplay("Hello World")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = DefacingLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
