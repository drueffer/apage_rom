# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 22:26:27 2012

@author: rueffer
"""

from autoDetect import Descriptor
import re

version="0.981"
latest_changes="""
0.981: introduces MSF for LB, takes it from EbeamSettings.py
"""

defDesc=Descriptor()
class CjobFile(object):
    def __init__(self,descriptor=defDesc,beams=[],negativeMarker=False):
        self.descriptor=descriptor
        self.patternIndex=1
        self.beams=beams
        
#    def getPatternColor(self):
#        i=self.patternIndex
#        self.patternIndex+=1
    def __get_desc__(self):
        return self.__desc__
        
    def __set_desc__(self,descriptor):
        if descriptor == None:
            self.__desc__=Descriptor()
        else:
            self.__desc__=descriptor

    descriptor = property(__get_desc__,__set_desc__)
    
    def getString(self,name,layers,blocks,doses,beams,camps,useCAMP=None,negativeMarker=False):
        string = self.getTemplateString()
        exposures=[]
        for n,m in enumerate(layers):
            plugins=[]
            for block in blocks[n]:
                plugin=self.getPlugin(name,block,layer=m,
                                      dose=doses[m],beam=beams[m],camp=camps[m],
                                      negativeMarker=negativeMarker[m])
                plugins.append(plugin)
            exposure=self.getExposure("L%02d"%m,plugins,camp=camps[m],
                                      useCAMP=useCAMP,negativeMarker=negativeMarker[m])
            exposures.append(exposure)
        for exposure in exposures:
            string=re.sub(r"\$\$EXPOSURES\$\$",exposure+"$$EXPOSURES$$",string)
        string=re.sub(r"\$\$EXPOSURES\$\$\n","",string)
        return string
        
    def getPlugin(self,name,block,layer=0,dose=800,beam="150nA",camp=0,no=2,negativeMarker=False):
        if no != 2:
            raise NotImplementedError("Only 2 markers currently")
        pos="%d,%d"%((block[0],block[1]))
        pattern=name.lower()+"_block%d-%d_%02d.gpf"%((block[0],block[1],layer))
        
        
        dose=str(dose)
        string = self.getPluginString(negativeMarker=negativeMarker)
        string=re.sub(r"\$\$POS\$\$",pos,string)
        string=re.sub(r"\$\$PATTERN\$\$",pattern,string)
        string=re.sub(r"\$\$DOSE\$\$",dose,string)
        string=re.sub(r"\$\$BEAM\$\$",self.beams[beam],string)
        
        cSx=self.descriptor.cellSize[0]
        cSy=self.descriptor.cellSize[1]
        nCx=self.descriptor.cellsPerBlock[0]
        nCy=self.descriptor.cellsPerBlock[1]
        C0=(cSx*nCx/2.,cSy*nCy/2.-cSy-camp*no*cSy)
        C1=(-cSx*nCx/2.+cSx+camp*no*cSx,cSy*nCy/2.)
        C2=(-cSx*nCx/2.,-cSy*nCy/2.+cSy+camp*no*cSy)
        C3=(cSx*nCx/2.-cSx-camp*no*cSx,-cSy*nCy/2.)
        camp0a="\\g<1><POSITION>%.3f,%.3f</POSITION>\\g<1>\\g<2>"%((C0[0],C0[1]))
        camp1a="\\g<1><POSITION>%.3f,%.3f</POSITION>\\g<1>\\g<2>"%((C1[0],C1[1]))
        camp2a="\\g<1><POSITION>%.3f,%.3f</POSITION>\\g<1>\\g<2>"%((C2[0],C2[1]))
        camp3a="\\g<1><POSITION>%.3f,%.3f</POSITION>\\g<1>\\g<2>"%((C3[0],C3[1]))
        camp0b="\\g<1><POSITION>%.3f,%.3f</POSITION>\\g<1>\\g<2>"%((C0[0],C0[1]-cSy))
        camp1b="\\g<1><POSITION>%.3f,%.3f</POSITION>\\g<1>\\g<2>"%((C1[0]+cSx,C1[1]))
        camp2b="\\g<1><POSITION>%.3f,%.3f</POSITION>\\g<1>\\g<2>"%((C2[0],C2[1]+cSy))
        camp3b="\\g<1><POSITION>%.3f,%.3f</POSITION>\\g<1>\\g<2>"%((C3[0]-cSx,C3[1]))
        string=re.sub(r"(\s*)(\$\$CAMP0\$\$)",camp0a,string)
        string=re.sub(r"(\s*)(\$\$CAMP1\$\$)",camp1a,string)
        string=re.sub(r"(\s*)(\$\$CAMP2\$\$)",camp2a,string)
        string=re.sub(r"(\s*)(\$\$CAMP3\$\$)",camp3a,string)
        string=re.sub(r"(\s*)(\$\$CAMP0\$\$)",camp0b,string)
        string=re.sub(r"(\s*)(\$\$CAMP1\$\$)",camp1b,string)
        string=re.sub(r"(\s*)(\$\$CAMP2\$\$)",camp2b,string)
        string=re.sub(r"(\s*)(\$\$CAMP3\$\$)",camp3b,string)
        for i in ["CAMP0","CAMP1","CAMP2","CAMP3"]:
            string=re.sub(r"(\s*)(\$\$%s\$\$)"%i,"",string)
        return string
        
    def getExposure(self,name,plugins,camp=0,useCAMP=None,negativeMarker=False):
        camp=int(camp)
        if useCAMP == None:
            useCAMP=self.descriptor.campSets
        for j in useCAMP:
            for i in j:
                if i[0]>self.descriptor.noBlocks[0] or i[1]>self.descriptor.noBlocks[1]:
                    raise ValueError("CAMP out of range")
        noblockx="%d"%self.descriptor.noBlocks[0]
        noblocky="%d"%self.descriptor.noBlocks[1]
        bx=self.descriptor.cellSize[0]*self.descriptor.cellsPerBlock[0]
        by=self.descriptor.cellSize[1]*self.descriptor.cellsPerBlock[1]
        blockdistx="%.3f"%(bx)
        blockdisty="%.3f"%(by)
        zerox=-self.descriptor.noBlocks[0]*bx/2.
        zeroy=-self.descriptor.noBlocks[1]*by/2.
        
        string = self.getExposureString(negativeMarker=negativeMarker)
        string=re.sub(r"\$\$EXPOSURENAME\$\$",name,string)
        string=re.sub(r"\$\$NOBLOCKX\$\$",noblockx,string)
        string=re.sub(r"\$\$NOBLOCKY\$\$",noblocky,string)
        string=re.sub(r"\$\$BLOCKDISTX\$\$",blockdistx,string)
        string=re.sub(r"\$\$BLOCKDISTY\$\$",blockdisty,string)
        
        pos= self.descriptor.pammPos[camp]
        pamm="\\g<1><POSITION>%.3f,%.3f</POSITION>"%((pos[0],pos[1]))
        string=re.sub(r"(\s*)(\$\$PAMM\$\$)",pamm,string)
        
## TODO: is <PICKUP/> necessary????
        for n,j in enumerate(useCAMP):
            CAMP="\\g<1><POSITION>%.3f,%.3f</POSITION>\\g<1>\\g<2>"%((zerox+j[camp][0]*bx,zeroy+j[camp][1]*by))
            string=re.sub(r"(\s*)(\$\$CAMP%d\$\$)"%n,CAMP,string)
            string=re.sub(r"(\s*)(\$\$CAMP%d\$\$)"%n,"",string)
        for plugin in plugins:
            string=re.sub(r"\$\$PLUGINS\$\$",plugin+"$$PLUGINS$$",string)
        string=re.sub(r"\$\$PLUGINS\$\$\n","",string)
        return string
        
    def getPluginString(self,negativeMarker=False):
        """placeholders:
            POS,PATTERN,DOSE,BEAM,CAMP0-CAMP3
        """
        if negativeMarker:
            m="si_e"
        else:
            m="CAMP"
        return"""      <PLUGIN>
        $$POS$$
        <PATTERN>
          $$PATTERN$$
          <POSITION>0,0</POSITION>
          <DOSE>$$DOSE$$</DOSE>
          <BEAM>$$BEAM$$</BEAM>
          <MARKER>
            %s
            <MARKERLIST>
              $$CAMP0$$
            </MARKERLIST>
            <MARKERLIST>
              $$CAMP1$$
            </MARKERLIST>
            <MARKERLIST>
              $$CAMP2$$
            </MARKERLIST>
            <MARKERLIST>
              $$CAMP3$$
            </MARKERLIST>
            <KEYSTONE>on</KEYSTONE>
          </MARKER>
        </PATTERN>
      </PLUGIN>
"""%m

    def getExposureString(self,negativeMarker=False):
        """Placeholders:
            EXPOSURENAME,
            NOBLOCKX,NOBLOCKY,BLOCKDISTX,BLOCKDISTY,
            PLUGINS, CAMP0-CAMP4,PAMM
        """
        if negativeMarker:
            m="si_e"
            ml="preal"
        else:
            m="CAMP"
            ml="PAMM"
        return    """  <EXPOSURE>
    $$EXPOSURENAME$$
    <POSITION>0,0</POSITION>
    <HIGHTENSION>100kV</HIGHTENSION>
    <CHECKS>
      <MAINDIST>on</MAINDIST>
      <MAINFIELD>on</MAINFIELD>
      <XMBC>on</XMBC>
      <XMBQ>on</XMBQ>
    </CHECKS>
    <LAYOUT>
      $$NOBLOCKX$$x$$NOBLOCKY$$
      <POSITION>0,0</POSITION>
      <REPETITION>$$BLOCKDISTX$$,0 0,0 $$NOBLOCKX$$</REPETITION>
      <REPETITION>0,$$BLOCKDISTY$$ 0,0 $$NOBLOCKY$$</REPETITION>
      <SCANORDER>serpentine</SCANORDER>
      <DROPOUT>1,1-$$NOBLOCKX$$,$$NOBLOCKY$$</DROPOUT>
$$PLUGINS$$
    </LAYOUT>
    <MARKER>
      %s
      <MARKERLIST>
          $$CAMP0$$
      </MARKERLIST>
      <MARKERLIST>
          $$CAMP1$$
      </MARKERLIST>
      <MARKERLIST>
          $$CAMP2$$
      </MARKERLIST>
      <MARKERLIST>
          $$CAMP3$$
      </MARKERLIST>
      <MARKERLIST>
          $$CAMP4$$
      </MARKERLIST>
      <PREMARKER>
        %s
        <MARKERLIST>
          $$PAMM$$
        </MARKERLIST>
        <PAM>29,29</PAM>
      </PREMARKER>
    </MARKER>
    <HEIGHT>check</HEIGHT>
  </EXPOSURE>
"""%((m,ml))
    
    def getTemplateString(self):##TODO is patternlegen really necesary, trying without????
        """Placeholders:
            EXPOSURES
        """
        return"""<!--Version: v02_05-->
<SUBSTRATE>
  Wafer:137 41  160
  <MACHINETYPE>ebpg5000+</MACHINETYPE>
  <NAME>100mm</NAME>
  <MATERIAL>silicon</MATERIAL>
  <ORIENTATION>100</ORIENTATION>
  <TYPE>p</TYPE>
  <DIAMETER>100mm</DIAMETER>
  <ROTATION>270°</ROTATION>
  <FLAT>Length:32.5mm,0°</FLAT>
  <FLAT>Length:18mm,90°</FLAT>
  <POSITION>0,0</POSITION>
$$EXPOSURES$$
</SUBSTRATE>
"""


class CincFile(object):
    def __init__(self,descriptor=defDesc):
        self.descriptor = descriptor
        
    def getCinc(self,name,block,layer,resolution):
        fileName=name+"_Block%d-%d.gds"%((block[0],block[1]))
        symbol="Block%d-%d"%((block[0],block[1]))
        output=name+"_Block%d-%d_%02d"%((block[0],block[1],layer))
        layer=str(int(layer))
        res = "%.3f"%resolution
        return """! CATS Y-2006.09-4 amd64 Linux 2.4.21-32.ELsmp PRODUCTION 2008/01/16 10:54:07 139467 
!Wed Aug  8 07:55:05 2012
Clear
Pregrid No
! ALLOCATE Parameters
Allocate_rects 100000
Allocate_traps 100000
Allocate_space 3000000
Format GPF
GPF MAIN_RANGE       1.25 7.8125
GPF SUB_RANGE        0.078125 0.48828125
GPF HIGH_TENSION     100
GPF SUB_BITS         14
GPF MAX_MSF          512
GPF RESOLUTION       0.05
GPF BSS              0.05
GPF MAIN_RESOLUTION  [7]
GPF SUB_RESOLUTION   [103]
GPF MAX_MAIN_FIELD   512 409.6 250
GPF MAX_SUB_FIELD    8 6.4 4.525
GPF MAIN_HEIGHT      [35000]
GPF MAIN_WIDTH       [35000]
GPF SUB_HEIGHT       [9321]
GPF SUB_WIDTH        [9321]
Compact YES
Height [5000]
Width [5000]
Input $TED/%s
Structure %s
EXTENT ALL
Layers %s
OUTPUT %s
RES %s
DO
EXIT
"""%((fileName,symbol,layer,output,res))

"""
################################################################################
"""
class LBNode(object):
    def __init__(self,label,ftxtfile):
        self.label=label
        self.type=None
        self.name=ftxtfile.name
        self.block=ftxtfile.block
        self.layer=int(ftxtfile.layer)
        self.exposureSettings=ftxtfile.exposureSettings
    
    def getNodeHead(self,ID,nextNode=None,prevNode=None):
        pos=(ID-1)*50
        string= """NODE %s ()
ID       = %d
VERSION    = 2
COMMENT    = Import
LABEL    = %s
POSITION = 50,%d
COLLECTFORLOOP = false
"""%((self.type,ID,self.label,pos))
        if prevNode:
            string+="IN_PORT[0] = %d, %s, 0\n"%((ID-1,prevNode.label))
        if nextNode:
             string+="OUT_PORT[0] = %d, %s, 0\n"%((ID+1,nextNode.label))
        return string


class ImportNode(LBNode):
    def __init__(self,label,ftxtfile):
        super(ImportNode,self).__init__(label,ftxtfile)
        self.type="Import"

    def getNodeBody(self):
        fileName=self.name+"_Block%d-%d.gds"%((self.block[0],self.block[1]))
        return """FILE_NAME = %s
FILE_TYPE = 1
LAYERSET = *
SINGLE_PATH_IMPORT = false
BOXES_IMPORT = true
ZERO_PATH_WIDTH = 0.000000
ENDNODE
"""%((fileName))


class ExtractNode(LBNode):
    def __init__(self,label,ftxtfile,singleLayer=False):
        super(ExtractNode,self).__init__(label,ftxtfile)
        self.type="Extract"
        self.singleLayer=singleLayer

    def getNodeBody(self):
        if self.singleLayer:
            layers="%d"%self.layer
        else:
            layers=""
            for layer in self.exposureSettings["PECLayers"]:
                layers+=("%d%%2C"%layer)
            layers=layers[:-3]
        return """VERSION = 1
LAYERSET = %s
EXTRACT_TYPE = INSTANCES
REGIONBEHAVIOR = Clip
EXTENT_MODE = DEFAULT
ENDNODE
"""%layers


class HealNode(LBNode):
    def __init__(self,label,ftxtfile):
        super(HealNode,self).__init__(label,ftxtfile)
        self.type="Healing"

    def getNodeBody(self):
        return """PROCESSING_MODE = HEALING
SELECTED_LAYER_SET = *
LAYER_ASSIGNMENT = PerLayer

VERSION = 1
TARGET_LAYER = 1(0)
SOFTFRAME = 0.300000
PROCESSHIERARCHIC = True
ENDNODE
"""



class PECNode(LBNode):
    def __init__(self,label,ftxtfile):
        super(PECNode,self).__init__(label,ftxtfile)
        self.type="PEC"

    def getNodeBody(self):
        eS=self.exposureSettings
        return """VERSION = 1
BETA  = %.6f
ETA   = %.6f
BEAM_SIZE = %.6f
PEC_ACCURACY = 1.000000
MAX_NUM_DOSECLASSES = 256
DOSE_CLASS_MODE = ACCURACY
NUMBER_DOSECLASSES = 64
FRACTURE_GRID = %.6f
MINIMUM_FIGURE_SIZE = 0.100000
MINIMUM_DOSE_FACTOR = 0.100000
MAXIMUM_DOSE_FACTOR = 10.000000
AUTOMATIC_MINIMUM_FIGURE_SIZE = true
FIGURE_BASED = true
HIERARCHIC_SHORT_RANGE = true
SHORT_RANGE_USE_GPU = false
RECTANGULAR_FRACTURING = false
PERIODIC_LAYOUT = false
PITCHX = 0.000000
PITCHY = 0.000000
REPX = 1
REPY = 1
USE_NUMERICAL_PSF = false
SINGLE_LINE_BEAM_WIDTH = 0.000000
AUTOMATIC_SR_REGION  = true
SR_LAYER = *
INCLUDE_LONGRANGE = true
FAST_APPROXIMATION = true
PSF_FILENAME = ..%%2F..%%2F..%%2F..
FIT_RESULTS_IN = false
ResistEffects = false
ResistEffectInfluenceRange = 1.000000
Density = 0.000000
DevelopmentRate = 1.000000
Density = 1.000000
DevelopmentRate = 1.000000
ENDNODE
"""%((eS["beta"],eS["eta"],eS["beamsize"],eS["res"]))



class ExportNode(LBNode):
    def __init__(self,label,ftxtfile):
        super(ExportNode,self).__init__(label,ftxtfile)
        self.type="Export"

    def getNodeBody(self):
        res = "%.9f"%self.exposureSettings["res"]
        MSF_main = "%.9f"%self.exposureSettings["MSF"][0]
        MSF_sub = "%.9f"%self.exposureSettings["MSF"][1]
        fileName=self.name.lower()+"_block%d-%d_%02d.gpf"%((self.block[0],self.block[1],self.layer))
        return """FILE_NAME = %s
FILE_TYPE = 7
EXTENT_AUTOMATIC
FORMAT_TYPE = epfl
FORMAT_VERSION = 1.40
TENSION = 100
MAINFIELD_DAC_BITS = 16
MAINFIELD_RESOLUTION_MIN = 1.250000000
MAINFIELD_RESOLUTION_MAX = 7.812500000
MINIMUM_MAINFIELD_SIZE = 10.00000
MAXIMUM_MAINFIELD_SIZE = 250.00000
NUMBER_SUBFIELD_BITS = 14
SUBFIELD_RESOLUTION_MIN = 0.078125000
SUBFIELD_RESOLUTION_MAX = 0.488281250
MAXIMUM_SUBFIELD_MSF = 250
MINIMUM_SUBFIELD_SIZE = 0.00125
MAXIMUM_SUBFIELD_SIZE = 4.52500
SYSTEM_TYPE = HR
RESOLUTION = %s
BEAM_STEP_SIZE = %s
MAIN_FIELD_MSF = %s
SUB_FIELD_MSF = %s
MAIN_FIELD_SIZE_X = 250.000000
MAIN_FIELD_SIZE_Y = 250.000000
MAIN_FIELD_PLACEMENT = Fixed
SUB_FIELD_SIZE_X = 4.525
SUB_FIELD_SIZE_Y = 4.525
COMPACTION = true
BEAM_STEP_SIZE_FRACTURING = false
CURVE_TOLERANCE = 1.000000
Y_TRAPEZIAS = true
DIAGONAL_LINE_COMPACTION = true
TRAPEZOID_DOSE_CORRECTION = false
NORMALIZE_DOSE_RANGE = false
AREA_SELECTION = SelectedThenRemainder
FRACTURE_MODE = LRFT
FIELD_OVERLAP_X = 0.000000
FIELD_OVERLAP_Y = 0.000000
OVERLAP_METHOD = Standard
INTERLEAVING_SIZE = 0.000000
INTERLOCK_LAYER = *
MULTIPASS_MODE = 1
MAINFIELD_OFFSET_X = 0.500000
MAINFIELD_OFFSET_Y = 0.500000
SUBFIELD_OFFSET_X = 0.500000
SUBFIELD_OFFSET_Y = 0.500000
MULTIPASS_LAYER = *
ENDNODE

"""%((fileName,res,res,MSF_main,MSF_sub))




class FtxtFile(object):
    def getFtxt(self,name,block,layer,exposureSettings):
        self.name=name
        self.block=block
        self.layer=layer
        self.exposureSettings=exposureSettings
        flowName=name+"_Block%d-%d"%((block[0],block[1]))
        #Define Nodes
        nodes=[]
        nodes.append(ImportNode("Import",self))
        if self.exposureSettings["doPEC"] and self.exposureSettings["multiPEC"]:
            nodes.append(ExtractNode("Extract_1",self,singleLayer=False))
        else:
            nodes.append(ExtractNode("Extract",self,singleLayer=True))
        nodes.append(HealNode("Heal",self))
        if self.exposureSettings["doPEC"]:
                nodes.append(PECNode("PEC",self))
                if self.exposureSettings["multiPEC"]:
                    nodes.append(ExtractNode("Extract_2",self,singleLayer=True))
        nodes.append(ExportNode("Export",self))
        
        #Create String
        string="FLOW %s\n ()\n"%flowName
        prevNode=None
        for n,node in enumerate(nodes):
            if n<len(nodes)-1:
                nextNode=nodes[n+1]
            else:
                nextNode=None
            string+=node.getNodeHead(n+1,nextNode=nextNode,prevNode=prevNode)
            string+=node.getNodeBody()
            string+="\n\n"
            prevNode=nodes[n]
        return string+"\n"+"ENDFLOW\n"
        

#        flowName=name+"_Block%d-%d"%((block[0],block[1]))
#        resolution=exposureSettings["res"]
#        return "FLOW %s\n ()\n"%flowName+self.getImportNode(name,block,layer,exposureSettings)+"\n\n"\
#                                        +self.getExtractNode(name,block,layer,exposureSettings)+"\n\n"\
#                                        +self.getHealingNode(name,block,layer,exposureSettings)+"\n\n"\
#                                        +self.getPECNode(name,block,layer,exposureSettings)+"\n\n"\
#                                        +self.getExportNode(name,block,layer,exposureSettings)+"\n"+"ENDFLOW\n"
#        
#    



"""
################################################################################
"""




#
#
#
#
#class FtxtFile(object):
#    def __init__(self,descriptor=defDesc):
#        self.descriptor = descriptor
#    
#    def getFtxt(self,name,block,layer,exposureSettings):
#        flowName=name+"_Block%d-%d"%((block[0],block[1]))
#        resolution=exposureSettings["res"]
#        return "FLOW %s\n ()\n"%flowName+self.getImportNode(name,block,layer,exposureSettings)+"\n\n"\
#                                        +self.getExtractNode(name,block,layer,exposureSettings)+"\n\n"\
#                                        +self.getHealingNode(name,block,layer,exposureSettings)+"\n\n"\
#                                        +self.getPECNode(name,block,layer,exposureSettings)+"\n\n"\
#                                        +self.getExportNode(name,block,layer,exposureSettings)+"\n"+"ENDFLOW\n"
#        
#    
#    def getImportNode(self,name,block,layer,exposureSettings):
#        fileName=name+"_Block%d-%d.gds"%((block[0],block[1]))
#        return """NODE Import ()
#ID       = 1
#VERSION    = 2
#COMMENT    = Import
#LABEL    = In%%20GDSII
#POSITION = 500, 50
#COLLECTFORLOOP = false
#OUT_PORT[0] = 2, Heal, 0
#
#FILE_NAME = %s
#FILE_TYPE = 1
#LAYERSET = *
#SINGLE_PATH_IMPORT = false
#BOXES_IMPORT = true
#ZERO_PATH_WIDTH = 0.000000
#ENDNODE
#"""%((fileName))
#
#    def getExtractNode(self,name,block,layer,exposureSettings):
#        layer=str(int(layer))
#        return """NODE Extract ()
#ID       = 2
#VERSION    = 2
#COMMENT    = Extract
#LABEL    = Extract
#POSITION = 500, 80
#COLLECTFORLOOP = false
#IN_PORT[0] = 1, In%%20GDSII, 0
#OUT_PORT[0] = 3, Heal, 0
#
#VERSION = 1
#LAYERSET = %s
#EXTRACT_TYPE = INSTANCES
#REGIONBEHAVIOR = Clip
#EXTENT_MODE = DEFAULT
#ENDNODE
#"""%layer
#
#    def getHealingNode(self,name,block,layer,exposureSettings):
#        layer=str(int(layer))
#        doPEC=exposureSettings["doPEC"]
#        if doPEC:
#            nextNode="PEC"
#        else:
#            nextNode="Export"
#        return """NODE Healing ()
#ID       = 3
#VERSION    = 2
#COMMENT    = Heal
#LABEL    = Heal
#POSITION = 500, 110
#COLLECTFORLOOP = false
#IN_PORT[0] = 2, Extract, 0
#OUT_PORT[0] = 4, %s, 0
#PROCESSING_MODE = HEALING
#
#VERSION = 1
#TARGET_LAYER = 1(%s)
#SOFTFRAME = 0.300000
#PROCESSHIERARCHIC = True
#ENDNODE
#"""%((nextNode,layer))
#
#    def getPECNode(self,name,block,layer,exposureSettings):
#        doPEC=exposureSettings["doPEC"]
#        eS=exposureSettings
#        if not doPEC:
#            return ""
#        else:
#            return """
#NODE PEC ()
#ID       = 4
#VERSION    = 2
#COMMENT    = PEC
#LABEL    = PEC
#POSITION = 500, 140
#COLLECTFORLOOP = false
#IN_PORT[0] = 3, Heal, 0
#OUT_PORT[0] = 5, Out%%20GPF, 0
#
#VERSION = 1
#
#BETA  = %.6f
#ETA   = %.6f
#BEAM_SIZE = %.6f
#PEC_ACCURACY = 1.000000
#MAX_NUM_DOSECLASSES = 256
#DOSE_CLASS_MODE = ACCURACY
#NUMBER_DOSECLASSES = 64
#FRACTURE_GRID = %.6f
#MINIMUM_FIGURE_SIZE = 0.100000
#MINIMUM_DOSE_FACTOR = 0.100000
#MAXIMUM_DOSE_FACTOR = 10.000000
#AUTOMATIC_MINIMUM_FIGURE_SIZE = true
#FIGURE_BASED = true
#HIERARCHIC_SHORT_RANGE = true
#SHORT_RANGE_USE_GPU = false
#RECTANGULAR_FRACTURING = false
#PERIODIC_LAYOUT = false
#PITCHX = 0.000000
#PITCHY = 0.000000
#REPX = 1
#REPY = 1
#USE_NUMERICAL_PSF = false
#SINGLE_LINE_BEAM_WIDTH = 0.000000
#AUTOMATIC_SR_REGION  = true
#SR_LAYER = *
#INCLUDE_LONGRANGE = true
#FAST_APPROXIMATION = true
#PSF_FILENAME = ..%%2F..%%2F..%%2F..
#FIT_RESULTS_IN = false
#ResistEffects = false
#ResistEffectInfluenceRange = 1.000000
#Density = 0.000000
#DevelopmentRate = 1.000000
#Density = 1.000000
#DevelopmentRate = 1.000000
#ENDNODE
#"""%((eS["beta"],eS["eta"],eS["beamsize"],eS["res"]))
#
#    def getExportNode(self,name,block,layer,exposureSettings):
#        doPEC=exposureSettings["doPEC"]
#        res = "%.9f"%exposureSettings["res"]
#        MSF_main = "%.9f"%exposureSettings["MSF"][0]
#        MSF_sub = "%.9f"%exposureSettings["MSF"][1]
#        fileName=name.lower()+"_block%d-%d_%02d.gpf"%((block[0],block[1],layer))
#        if doPEC:
#            nodeNumber=5
#            prevNode="PEC"
#        else:
#            nodeNumber=4
#            prevNode="Heal"
#        return """NODE Export ()
#ID       = %s
#VERSION    = 2
#COMMENT    = Export
#LABEL    = Out%%20GPF
#POSITION = 500, 170
#COLLECTFORLOOP = false
#IN_PORT[0] = %s, %s, 0
#
#FILE_NAME = %s
#FILE_TYPE = 7
#EXTENT_AUTOMATIC
#
#FORMAT_TYPE = epfl
#FORMAT_VERSION = 1.40
#TENSION = 100
#MAINFIELD_DAC_BITS = 16
#MAINFIELD_RESOLUTION_MIN = 1.250000000
#MAINFIELD_RESOLUTION_MAX = 7.812500000
#MINIMUM_MAINFIELD_SIZE = 10.00000
#MAXIMUM_MAINFIELD_SIZE = 250.00000
#NUMBER_SUBFIELD_BITS = 14
#SUBFIELD_RESOLUTION_MIN = 0.078125000
#SUBFIELD_RESOLUTION_MAX = 0.488281250
#MAXIMUM_SUBFIELD_MSF = 250
#MINIMUM_SUBFIELD_SIZE = 0.00125
#MAXIMUM_SUBFIELD_SIZE = 4.52500
#SYSTEM_TYPE = HR
#RESOLUTION = %s
#BEAM_STEP_SIZE = %s
#MAIN_FIELD_MSF = %s
#SUB_FIELD_MSF = %s
#MAIN_FIELD_SIZE_X = 250.000000
#MAIN_FIELD_SIZE_Y = 250.000000
#MAIN_FIELD_PLACEMENT = Fixed
#SUB_FIELD_SIZE_X = 4.525
#SUB_FIELD_SIZE_Y = 4.525
#COMPACTION = true
#BEAM_STEP_SIZE_FRACTURING = false
#CURVE_TOLERANCE = 1.000000
#Y_TRAPEZIAS = true
#DIAGONAL_LINE_COMPACTION = true
#TRAPEZOID_DOSE_CORRECTION = false
#NORMALIZE_DOSE_RANGE = false
#AREA_SELECTION = SelectedThenRemainder
#FRACTURE_MODE = LRFT
#FIELD_OVERLAP_X = 0.000000
#FIELD_OVERLAP_Y = 0.000000
#OVERLAP_METHOD = Standard
#INTERLEAVING_SIZE = 0.000000
#INTERLOCK_LAYER = *
#MULTIPASS_MODE = 1
#MAINFIELD_OFFSET_X = 0.500000
#MAINFIELD_OFFSET_Y = 0.500000
#SUBFIELD_OFFSET_X = 0.500000
#SUBFIELD_OFFSET_Y = 0.500000
#MULTIPASS_LAYER = *
#ENDNODE
#
#"""%((str(nodeNumber),str(nodeNumber-1),prevNode,fileName,res,res,MSF_main,MSF_sub))