# -*- coding: utf-8 -*-
"""
Created on Sun Aug 19 14:06:31 2012

@author: rueffer
"""

from GDSGenerator import *
from GDSGenerator import Structure as Struct
from Settings import Descriptor as descSet
from numpy import mod,array
import numpy as np
from copy import copy as allcopy

from GDSGenerator import version as GDSGeneratorVersion
version="0.980"
#===============================================================================
#  Descriptor
#===============================================================================

def myRotate(ar,angle):
    if not isinstance(ar,np.ndarray):
        raise TypeError("no numyp array")
    rot = np.array([[np.cos(angle/180.*np.pi),-np.sin(angle/180.*np.pi)],
                     [np.sin(angle/180.*np.pi),np.cos(angle/180.*np.pi)]])
    if ar.shape==(2,):
        return np.dot(rot,ar)
    elif len(ar.shape)==2 and ar.shape[1]==2:
        return np.dot(rot,ar.T).T
    else:
        raise TypeError("only array of shape (2,) or (x,2) allowed")
        
#def myMirror(ar):
#    if not isinstance(ar,np.ndarray):
#        raise TypeError("no numyp array")
#    if ar.shape==(2,):
#        return np.dot(ar,np.array([1.,-1.]))
#    elif len(ar.shape)==2 and ar.shape[1]==2:
#        return np.dot(np.array([1.,-1.]),ar.T).T
#    else:
#        raise TypeError("only array of shape (2,) or (x,2) allowed")
#        
        
class EmptyDesc(object):
    def __init__(self,markerSize=4,markerArea=(200,150),cellSize=(500,500),cellsPerBlock=(16,16),centerMarkSize=100,
                 bitDistance=8,centerMark=True, noBlocks=(8,8),noBitsX=4,noBitsY=4,text="MASK",ebeamMarkerSize=20.,
                 patternLayer=100,commentLayer=101,campSets=None,maxMarker=3,
                 pammPos=[(-34000,-22000),(-34000,22000),(34000,-22000),(34000,22000)],**kwargs):
        """Helper class for default behavior
        """
        self.markerSize=markerSize/2.
        self.markerArea=markerArea
        self.cellSize=cellSize
        self.cellsPerBlock=cellsPerBlock
        self.centerMarkSize=centerMarkSize
        self.bitDistance=bitDistance
        self.centerMark=centerMark
        self.noBlocks=noBlocks
        self.noBitsX=noBitsX
        self.noBitsY=noBitsY
        self.text=text
        self.defExposureLayer=0
        self.patternLayer=patternLayer
        self.commentLayer=commentLayer
        self.ebeamMarkerSize=ebeamMarkerSize
        self.pammPos=pammPos
        #        self.defBeam=defBeam
#        self.defDose=defDose
#        self.defRes=defRes
#        self.defAlpha=defAlpha
#        self.defBeta=defBeta
#        self.defEta=defEta
        self.maxMarker=maxMarker
        if campSets == None:
            self.campSets=[[(0,0),(1,0),(0,1),(1,1)],
                      [(2,0),(3,0),(2,1),(3,1)],
                      [(0,2),(1,2),(0,3),(1,3)],
                      [(7,1),(6,1),(7,0),(7,1)],
                      [(1,7),(1,6),(0,7),(1,7)],
                     ]
        
        for i in descSet:
            if not self.__dict__.has_key(i[0]):
                raise KeyError(i+" - wrong key in descriptor default setting")
            self.__setattr__(i[0],i[1])
        for i in [0,1]: 
            if np.mod(self.cellsPerBlock[i],2): 
                raise ValueError("Please enter even value for cellsPerBlock")

class Descriptor(EmptyDesc):
    def __init__(self,**kwargs):
        """DEfaults to settings
        """
        super(Descriptor,self).__init__(**kwargs)
                
    def changeKwargs(self,**kwargs):
        for keys in self.__dict__:
            if kwargs.has_key(key):
                self.__setattr__(key,kwargs.pop(key))
        return kwargs
        
    def getBits(self,cell):
            zero=[-self.markerArea[i]/2. for i in [0,1]]
            bitx=[int(i) for i in bin(int(cell[0]))[::-1][:-2]]
            bity=[int(i) for i in bin(int(cell[1]))[::-1][:-2]]
            s0=int(np.log2(self.cellsPerBlock[0]*self.noBlocks[0]))
            s1=int(np.log2(self.cellsPerBlock[1]*self.noBlocks[1]))
            for i in range(s0-len(bitx)):
                bitx.append(0)
            for i in range(s1-len(bity)):
                bity.append(0)
            tx=np.zeros(s0,dtype=np.bool)
            ty=np.zeros(s1,dtype=np.bool)
            px=np.empty((s0,2))
            py=np.empty((s1,2))
            for i,b in enumerate(bitx):
                x=zero[0]+mod(i+1,self.noBitsX)*self.bitDistance
                y=zero[1]+((i+1)/self.noBitsY)*self.bitDistance
                px[i]=(x,y)
                tx[i]=b
            for i,b in enumerate(bity):
                x=zero[0]+(self.noBitsX-mod(i+1,self.noBitsX)-1)*self.bitDistance
                y=zero[1]+(self.noBitsY-(i+1)/self.noBitsY-1)*self.bitDistance
                py[i]=(x,y)
                ty[i]=b
            return px,py,tx,ty
                        
    def getCellPosition(self,cell):
        cellSize=[self.cellSize[i] for i in [0,1]]
        zero=[(self.cellSize[i]-self.cellSize[i]*self.cellsPerBlock[i]*self.noBlocks[i])/2. for i in [0,1]]
        pos=array([zero[0]+cell[0]*cellSize[0],zero[1]+cell[1]*cellSize[1]])
        return np.array(pos,dtype=np.int)
    
    def getBlockPosition(self,block):
        pos=array([(block[i]-0.5)*self.cellSize[i]*self.cellsPerBlock[i]-0.5*self.cellSize[i]*self.cellsPerBlock[i] *self.noBlocks[i] for i in [0,1]])
        return np.array(pos,dtype=np.int)
        
    def getBlockNo(self,cell):
        return np.array([int(cell[i])/int(self.cellsPerBlock[i])+1 for i in [0,1]],dtype=np.int)
        
    def getCellPosInBlock(self,cell):
        block=self.getBlockNo(cell)
        pos=self.getCellPosition(cell)-self.getBlockPosition(block)
        return pos
        
    def createInverseTransformFunc(self,center,angle,scale):   
        sub=center*np.array([1,-1])*scale
        def f(xy):
            if not isinstance(xy,np.ndarray):
                xy=np.array(xy,dtype=np.float)
            xy =  myRotate(xy,angle)
            return np.divide(np.add(xy,sub),np.array([scale,-scale]))
        return f
           
    def createTransformFunc(self,center,angle,scale):   
        sub=center*np.array([1,-1])*scale
        def f(xy):
            xy= np.subtract(np.multiply(xy,np.array([scale,-scale])),sub)
            if not isinstance(xy,np.ndarray):
                xy=np.array(xy,dtype=np.float)
            return myRotate(xy,-angle)
        return f
        
        
class Structure(Struct):
        
    def __init__(self,name,layer=None,descriptor=None,**kwargs):
        self.descriptor=descriptor
        super(Structure,self).__init__(name,layer=layer,**kwargs)
    
    def __get_desc__(self):
        return self.__desc__
        
    def __set_desc__(self,descriptor):
        if descriptor == None:
            self.__desc__=Descriptor()
        else:
            self.__desc__=descriptor

    descriptor = property(__get_desc__,__set_desc__)
    
            
        
         
class Template(Structure):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor  
        for key in self.__dict__.keys():
            if kwargs.has_key(key):
                attr=kwargs.pop(key)
                self.__setattr__(key,attr)
        for key in self.kwargs:
            if key not in self.__dict__.keys():
                if kwargs.has_key(key):
                    attr=kwargs.pop(key)
                elif key not in self.__dict__.keys():
                    attr=self.kwargs[key]
                self.__setattr__(key,attr)
        del self.kwargs
        super(Template,self).__init__(name,layer=None,**kwargs)
        
    def updateDefaultValue(self,key,value):
        if key not in self.__dict__.keys():
            self.__setattr__(key,value)
             
    def getCurvePoints(self,P0,P1,P2,R,n=20):
        """Generates a curve. P0,P1 and P2 define a corner and R defines the radius of the
        tangential circle element. n gives the number of point to approximate the curve.
        P1 is the corner itself and P0 and P2 give the tangents.
        """
        P0=np.array(P0)
        P1=np.array(P1)
        P2=np.array(P2)
        o1=(P0-P1)/np.sqrt(np.dot(P0-P1,P0-P1))
        o2=(P2-P1)/np.sqrt(np.dot(P2-P1,P2-P1))
        if np.arcsin(np.cross(o1,o2)) > 0:
            a=1.
            b=-1.
        else:
            a=-1.
            b=1.
        
        v1=R*np.dot(np.array([[0.,b],[a,0.]]),o1)
        v2=R*np.dot(np.array([[0.,a],[b,0.]]),o2)
        dv=v2-v1
        a=np.array([[o1[0],-o2[0]],[o1[1],-o2[1]]])
        b=dv
        x=np.linalg.solve(a,b)
        circleCenter= P1+x[0]*o1+v1
        angle = np.arcsin(np.cross(v2/R,v1/R))
        points=[]
        for i in range(n+1):
            x=-i*angle/n
            rot = np.array([[np.cos(x),-np.sin(x)],
                             [np.sin(x),np.cos(x)]])
            points.append(circleCenter+np.dot(rot,-v1))
        return points
        

class NanoWireTemplate(Template):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "end1":(10,10),
        "end2":(-10,-10),
        "layer":0
        })
        super(NanoWireTemplate,self).__init__(name,descriptor=descriptor,**kwargs)
        #self.make()
        
#    def getLayers(self):
#        return [self.layer]
    
    def make(self):
        self.insertElement(Rectangle(self.width,self.length),layer=self.layer)
        
    def getDefLayers(self):
        return set([self.layer])

    def getCoords(self):
        """Returns top,bot,center,lengthvector,length,angle
        with:
        top: coordinate of the upper end of the wire
        bot: coordinate of the lower end of the wire
        center: coordinate of the center of the wire
        lengthvector: is the vector top-bot
        length: is the absolute value of the length
        anggle: is the rotational angle of the wire 
        """
        if self.end1[1]>self.end2[1]:
            top=np.array(self.end1)
            bot=np.array(self.end2)
        else:
            top=np.array(self.end2)
            bot=np.array(self.end1)
        center=(top+bot)/2.
        lengthvector=(top-bot)
        length=np.sqrt(np.dot(lengthvector,lengthvector))   
        angle=np.mod((-np.arcsin(np.cross(lengthvector/length,[0.,1.]))*180./np.pi),180)
        return top,bot,center,lengthvector,length,angle
    
    def getOptions(self):
        options=deepcopy(self.__dict__)
        options.pop("end1")
        options.pop("end2")
        for key in options.keys():
            if key[0:2] =="__":
                options.pop(key)
        return options
        
        


class Cell(Structure):
    def __init__(self,cell,**kwargs):
        super(Cell,self).__init__("",**kwargs)
        self.name = "Cell"+str(cell[0])+"-"+str(cell[1])+""
        self.coords=cell
        self.EXTENTS=None
#        self.createCellFrame()        
        
    def __get_coords__(self):
        return self.__coords__
        
    def __set_coords__(self,coords):
        self.__coords__=coords

    coords = property(__get_coords__,__set_coords__)
    
    def insertElement(self,element,layer=None,**kwargs):
        if kwargs.has_key("xy"):
            xy=np.array(kwargs.pop("xy"))
        else:
            xy=np.zeros(2)
        if isinstance(element,type(self)):
            raise TypeError("Can't insert a "+str(element)+" into "+str(self))
#        elif isinstance(element,Structure):
#            for struct in [element]+element.getAllStructures():
#                if struct.name[0:4] != "Cell":
#                   struct.name = self.name+"_"+struct.name
                   
        pos=xy
        super(Cell,self).insertElement(element,layer=layer,xy=pos,**kwargs)  
        
    
    def getPos(self):
        return self.descriptor.getCellPosition(self.coords)
        
    def getBlockNo(self):
        return self.descriptor.getBlockNo(self.coords)
        
    def getPosInParent(self):
        return self.descriptor.getCellPosInBlock(self.coords)
        
    def createCircleMarker(self):
        CIRCLEMARKER=Structure("CircleMarker")
        elem=Circle(self.descriptor.markerSize)
        CIRCLEMARKER.insertElement(elem,layer=self.descriptor.patternLayer)
        return CIRCLEMARKER
        
    def __getFramePoints__(self):
        wo=self.descriptor.cellSize[0]
        Ho=self.descriptor.cellSize[1]
        return [[wo/2.,Ho/2],[-wo/2.,Ho/2],[-wo/2.,-Ho/2],[wo/2.,-Ho/2],[wo/2.,Ho/2]]
        
                
    def createFrame(self,details=2):
        if details == 0:
            return None
        if details == 1:
            wi=self.descriptor.markerArea[0]
            Hi=self.descriptor.markerArea[1]
            wo=self.descriptor.cellSize[0]
            Ho=self.descriptor.cellSize[1]
            CELLFRAME=Structure("CellFrame")
            CELLFRAME.insertElement(Path([[wo/2.,Ho/2],[-wo/2.,Ho/2],[-wo/2.,-Ho/2],[wo/2.,-Ho/2],[wo/2.,Ho/2]],1),
                                         layer=self.descriptor.commentLayer)
            CELLFRAME.insertElement(Path([[wi/2.,Hi/2],[-wi/2.,Hi/2],[-wi/2.,-Hi/2],[wi/2.,-Hi/2],[wi/2.,Hi/2]],1),
                                         layer=self.descriptor.commentLayer)
        elif details == 2:
            CIRCLEMARKER=self.createCircleMarker()
            c=[self.descriptor.markerArea[i] for i in [0,1]]
            CELLFRAME=Structure("CellFrame")
            CELLFRAME.insertElement(Array(CIRCLEMARKER,c[0],c[1],2,2,centered=True))
            CELLFRAME.insertElement(CIRCLEMARKER,xy=(-self.descriptor.markerArea[0]/2.+3*self.descriptor.bitDistance,
                                      -self.descriptor.markerArea[1]/2.+3*self.descriptor.bitDistance))
        else:
            raise ValueError("details can be 0,1,2")
        return CELLFRAME
        
    def createPattern(self,details=2):
        if details in [0,1]:
            return None
        elif details == 2:
            cell=self.coords
            name=str(cell[0])+"-"+str(cell[1])
            bitDist=self.descriptor.bitDistance
            zero=[-self.descriptor.markerArea[i]/2. for i in [0,1]]
            BITS=Structure("CellBits_"+name)
            CIRCLEMARKER=self.createCircleMarker()
            bit=[int(i) for i in bin(int(cell[0]))[::-1][:-2]]
            ##TODO use descriptor.getBits(cell)
            for i,b in enumerate(bit):
                if b:
                    x=zero[0]+mod(i+1,self.descriptor.noBitsX)*bitDist
                    y=zero[1]+((i+1)/self.descriptor.noBitsY)*bitDist
                    BITS.insertElement(CIRCLEMARKER,xy=(x,y))
            bit=[int(i) for i in bin(int(cell[1]))[::-1][:-2]]
            for i,b in enumerate(bit):
                if b:
                    x=zero[0]+(self.descriptor.noBitsX-mod(i+1,self.descriptor.noBitsX)-1)*bitDist
                    y=zero[1]+(self.descriptor.noBitsY-(i+1)/self.descriptor.noBitsY-1)*bitDist
                    BITS.insertElement(CIRCLEMARKER,xy=(x,y))
            return BITS
        else:
            raise ValueError("details can be 0,1,2")
        
    def insertPatterns(self,details=2,copy=True):
        PATTERN=Structure(self.name+"_etc")
        if copy:
            out=self.copy()
            out.insertElement(PATTERN)
        else:
            self.insertElement(PATTERN)
        PATTERN.insertElement(self.createFrame(details=details))
        PATTERN.insertElement(self.createPattern(details=details))
        PATTERN.insertElement(self.createExtents())
        if copy:
            return out
#        self.insertElement(PATTERN)
    
    def createExtents(self):
        ext=self.calcExtents()
        frame=self.__getFramePoints__()
        #TODO: this is an ugly hack to have bigger extents... solve the bug with the text etc..
        mx=max(abs(ext[0]).max(),frame[0][1])*1.3
        my=max(abs(ext[1]).max(),frame[1][1])*1.3
        points=[[mx,my],[-mx,my],[-mx,-my],[mx,-my],[mx,my]]
        if self.EXTENTS==None:
            self.EXTENTS=Structure(self.name+"_ext")
            self.EXTENTS.insertElement(Polygon(points),layer=self.descriptor.commentLayer)
        else:
            self.EXTENTS.getAllPatterns(typ=Polygon)[0].points=points
        return self.EXTENTS
            
        ##TODO
        
    
class Block(Cell):
    def __init__(self,block,**kwargs):
        super(Block,self).__init__(block,**kwargs)
        self.name = "Block"+str(block[0])+"-"+str(block[1])+""
                
    def getPos(self):
        return self.descriptor.getBlockPosition(self.coords)

    def getBlockNo(self):
        return np.array(self.coords)
        
    def getPosInParent(self):
        return self.getPos()
        
    def insertElement(self,element,layer=None,**kwargs):
        if kwargs.has_key("xy"):
            xy=np.array(kwargs.pop("xy"))
        else:
            xy=np.zeros(2)
        if isinstance(element,type(self)):
            raise TypeError("Cent't insert a "+str(element)+" into "+str(self))
        elif isinstance(element,Cell):
            pos=xy+element.getPosInParent()
        else:
            pos=xy
        super(Block,self).insertElement(element,layer=layer,xy=pos,**kwargs)  
        
    def __getFramePoints__(self):
        wi=self.descriptor.cellSize[0]*self.descriptor.cellsPerBlock[0]
        Hi=self.descriptor.cellSize[1]*self.descriptor.cellsPerBlock[1]
        return [[wi/2.,Hi/2],[-wi/2.,Hi/2],[-wi/2.,-Hi/2],[wi/2.,-Hi/2],[wi/2.,Hi/2]]
                

    def createFrame(self,details=2):
        if details == 0:
            return None
        CELLFRAME=super(Block,self).createFrame(details=details)
        BLOCKFRAME=Structure("BlockFrame")
        if details == 1:
            wi=self.descriptor.cellSize[0]*self.descriptor.cellsPerBlock[0]
            Hi=self.descriptor.cellSize[1]*self.descriptor.cellsPerBlock[1]
            BLOCKFRAME.insertElement(Path([[wi/2.,Hi/2],[-wi/2.,Hi/2],[-wi/2.,-Hi/2],[wi/2.,-Hi/2],[wi/2.,Hi/2]]),layer=self.descriptor.commentLayer)
        elif details == 2:
            d=[float(self.descriptor.cellSize[i]) for i in [0,1]]
            n=[int(self.descriptor.cellsPerBlock[i]) for i in [0,1]]
            CELLFRAMES=Array(CELLFRAME,d[0],d[1],n[0],n[1],centered=True)
            EBEAMFRAME=self.createEbeamFrame(sub=False)
            BLOCKFRAME.insertElement(CELLFRAMES)
            BLOCKFRAME.insertElement(EBEAMFRAME)
        else:
            raise ValueError("details can be 0,1,2")
        return BLOCKFRAME
        
    def createEBeamMarker(self):
        EBEAMMARKER=Structure("EBeamMarker")
        elem=Square(self.descriptor.ebeamMarkerSize)
        EBEAMMARKER.insertElement(elem,layer=self.descriptor.patternLayer)
        return EBEAMMARKER
        
    def createEbeamFrame(self,sub=False):
        d=[float(self.descriptor.cellSize[i]) for i in [0,1]]
        n=[int(self.descriptor.cellsPerBlock[i]) for i in [0,1]]
        EBEAMMARKER=self.createEBeamMarker()
        EBEAMFRAME=Structure("EBeamFrame")
        EBEAMFRAMEELEMENT_X=Array(EBEAMMARKER,d[0],0,n[0]/2-1,1,centered=True)
        EBEAMFRAMEELEMENT_Y=Array(EBEAMMARKER,0,d[1],1,n[1]/2-1,centered=True)
        EBEAMFRAME.insertElement(EBEAMFRAMEELEMENT_X,xy=(-d[0]*n[0]/4.,d[1]*n[1]/2.))
        EBEAMFRAME.insertElement(EBEAMFRAMEELEMENT_X,xy=(d[0]*n[0]/4.,-d[1]*n[1]/2.))
        EBEAMFRAME.insertElement(EBEAMFRAMEELEMENT_Y,xy=(-d[0]*n[0]/2.,-d[1]*n[1]/4.))
        EBEAMFRAME.insertElement(EBEAMFRAMEELEMENT_Y,xy=(d[0]*n[0]/2.,d[1]*n[1]/4.))
        if sub:
            return EBEAMFRAME,EBEAMFRAMEELEMENT_X,EBEAMFRAMEELEMENT_Y
        else:
            return EBEAMFRAME 
            
    def createPattern(self,details=2):
        if details in [0,1]:
            return None
        elif details==2:
            block=self.coords
            cellSize=[self.__desc__.cellSize[i] for i in [0,1]]
            bitDist=self.__desc__.bitDistance
            cellsBlock=[self.__desc__.cellsPerBlock[i] for i in [0,1]]
            zero=[-0.5*cellSize[i]*cellsBlock[i]+(cellSize[i]-self.__desc__.markerArea[i])/2. for i in [0,1]]
            startCell=[self.__desc__.cellsPerBlock[i]*(block[i]-1) for i in [0,1]]
            CIRCLEMARKER=self.createCircleMarker()
            BITCOLSX=[]
            BITX=[]
            BITCOLSY=[]
            BITY=[]
            maxBits=len(bin(block[0]*cellsBlock[0]))-2
            bit=[0 for i in range(maxBits)]
            for n,i in enumerate(bin(startCell[0])[::-1][:-2]): 
                bit[n]=int(i)
            for i in range(maxBits):
                dx1=cellSize[0]
                dy1=cellSize[1]
                if i <  len(bin(cellsBlock[0]-1))-2:
                    nx1=2**i
                    ny1=cellsBlock[1]
                    x2=zero[0]+cellSize[0]*2**i+mod(i+1,self.__desc__.noBitsX)*bitDist
                    y2=zero[1]+((i+1)/self.__desc__.noBitsY)*bitDist
                    dx2=cellSize[0]*2**(i+1)
                    dy2=0
                    nx2=cellsBlock[0]/2**(i+1)
                    ny2=1
                    do = True
                    ar=True
                else:
                    nx1=cellsBlock[0]
                    ny1=cellsBlock[1]
                    x2=zero[0]+mod(i+1,self.__desc__.noBitsX)*bitDist
                    y2=zero[1]+((i+1)/self.__desc__.noBitsY)*bitDist
                    dx2=cellSize[0]
                    dy2=0
                    nx2=1
                    ny2=1
                    do = bit[i]
                    ar=False
                if do:
                    elem=Structure("B"+str(block[0])+","+str(block[1])+"_"+"BitX"+str(i)+"_Column")
                    BITCOLSX.append(elem)
                    elem.insertElement(Array(CIRCLEMARKER,dx1,dy1,nx1,ny1,centered=False))
                    elem2=Structure("B"+str(block[0])+","+str(block[1])+"_"+"BitX"+str(i))
                    BITX.append(elem2)
                    if ar:
                        elem2.insertElement(Array(elem,dx2,dy2,nx2,ny2,centered=False),xy=(x2,y2))
                    else:
                        elem2.insertElement(elem,xy=(x2,y2))
    
            BITSX=Structure("B"+str(block[0])+"-"+str(block[1])+"_"+"BitsX")
            for i in BITX:
                BITSX.insertElement(i)
                
            maxBits=len(bin(block[1]*cellsBlock[1]))-2
            bit=[0 for i in range(maxBits)]
            for n,i in enumerate(bin(startCell[1])[::-1][:-2]): 
                bit[n]=int(i)
            for i in range(maxBits):
                dx1=cellSize[0]
                dy1=cellSize[1]
                if i <  len(bin(cellsBlock[0]-1))-2:
                    nx1=cellsBlock[1]
                    ny1=2**i
                    x2=zero[0]+(self.__desc__.noBitsX-mod(i+1,self.__desc__.noBitsX)-1)*bitDist
                    y2=zero[1]+cellSize[1]*2**i+(self.__desc__.noBitsY-(i+1)/self.__desc__.noBitsY-1)*bitDist
                    dx2=0
                    dy2=cellSize[1]*2**(i+1)
                    nx2=1
                    ny2=cellsBlock[1]/2**(i+1)
                    do=True
                    ar=True
                else:
                    nx1=cellsBlock[0]
                    ny1=cellsBlock[1]
                    x2=zero[0]+(self.__desc__.noBitsX-mod(i+1,self.__desc__.noBitsX)-1)*bitDist
                    y2=zero[1]+(self.__desc__.noBitsY-(i+1)/self.__desc__.noBitsY-1)*bitDist
                    dx2=0
                    dy2=cellSize[1]
                    nx2=1
                    ny2=1
                    do = bit[i]
                    ar=False
                if do:
                    elem=Structure("B"+str(block[0])+","+str(block[1])+"_"+"BitY"+str(i)+"_Column")
                    BITCOLSY.append(elem)
                    elem.insertElement(Array(CIRCLEMARKER,dx1,dy1,nx1,ny1,centered=False))
                    elem2=Structure("B"+str(block[0])+","+str(block[1])+"_"+"BitY"+str(i))
                    BITY.append(elem2)
                    if ar:
                        elem2.insertElement(Array(elem,dx2,dy2,nx2,ny2,centered=False),xy=(x2,y2))
                    else:
                        elem2.insertElement(elem,xy=(x2,y2))
                    
            BITSY=Structure("B"+str(block[0])+"-"+str(block[1])+"_"+"BitsY")
            for i in BITY:
                BITSY.insertElement(i)
    #        
            BLOCKBITS=Structure("B"+str(block[0])+","+str(block[1])+"_"+"Bits")
            BLOCKBITS.insertElement(BITSX)
            BLOCKBITS.insertElement(BITSY)
            return BLOCKBITS
        else:
            raise ValueError("details can be 0,1,2")
    
class FlexiPattern(Block):
    
    def __init__(self,name,**kwargs):
        super(Block,self).__init__((0,0),**kwargs)
        self.name = name
         
    def __getFramePath__(self):
        wi=self.descriptor.cellSize[0]*self.descriptor.cellsPerBlock[0]*self.descriptor.noBlocks[0]
        Hi=self.descriptor.cellSize[1]*self.descriptor.cellsPerBlock[1]*self.descriptor.noBlocks[1]
        return [[wi/2.,Hi/2],[-wi/2.,Hi/2],[-wi/2.,-Hi/2],[wi/2.,-Hi/2],[wi/2.,Hi/2]]

    def insertElement(self,element,layer=None,**kwargs):
        if kwargs.has_key("xy"):
            xy=np.array(kwargs.pop("xy"))
        else:
            xy=np.zeros(2)
        if isinstance(element,type(self)):
            raise TypeError("Cent't insert a "+str(element)+" into "+str(self))
        if isinstance(element,Cell) or isinstance(element,Block):
            pos=xy+element.getPos()
        else:
            pos=xy
        super(Block,self).insertElement(element,layer=layer,xy=pos,**kwargs)  
                    
    def createFillMarkers(self,details=2):
        FILLMARKERS=Structure("FillMarkers")
        EBEAMFRAME,EBEAMFRAMEELEMENT_X,EBEAMFRAMEELEMENT_Y=self.createEbeamFrame(sub=True)
        b=[self.__desc__.noBlocks[i] for i in [0,1]]
        d=[self.__desc__.cellsPerBlock[i]*self.__desc__.cellSize[i] for i in [0,1]]
        p=[self.__desc__.cellsPerBlock[i]*self.__desc__.cellSize[i]*self.__desc__.noBlocks[i] for i in [0,1]]
        FILLMARKERS.insertArray(EBEAMFRAMEELEMENT_X,-p[0]/2.+d[0]/4.,-p[1]/2.,
                                        d[0],p[1],b[0],1)
        FILLMARKERS.insertArray(EBEAMFRAMEELEMENT_X,-p[0]/2.+d[0]*3./4.,+p[1]/2.,
                                        d[0],0,b[0],1)
        FILLMARKERS.insertArray(EBEAMFRAMEELEMENT_Y,-p[0]/2.,-p[1]/2.+d[1]*3./4.,
                                        p[0],d[1],1,b[1])
        FILLMARKERS.insertArray(EBEAMFRAMEELEMENT_Y,+p[0]/2.,-p[1]/2.+d[1]/4.,
                                        0,d[1],1,b[1])
        FILLMARKERS.insertArray(EBEAMMARKER,-p[0]/2.,-p[1]/2,
                                        d[0]/2.,d[1],b[0]*2+1,b[1]+1)
        FILLMARKERS.insertArray(EBEAMMARKER,-p[0]/2.,-p[1]/2+d[1]/2.,
                                        d[0],d[1],b[0]+1,b[1])
          
    def insertPatterns(self,details=2,copy=False):
        if copy:
            out=self.copy()
        else:
            out = self
        out.insertElement(Path(self.__getFramePath__()),layer=self.descriptor.commentLayer)
        for block in out.getAllStructures(typ=Block):
            block.insertPatterns(details=details,copy=False)
        for cell in out.getAllStructures(typ=Cell):
            cell.insertPatterns(details=details,copy=False)
        return out
              
  
#    
#a=FlexiPattern("a")
##cf=a.createCellFrame()
##a.insertElement(cf)
##cf2=a.createCellPattern((16,16))
##a.insertElement(cf2)
#CELL=Cell((1,1))
#CELL.insertExtents()
#CELL.insertElement(Text("test"),layer=0)
#CELL.insertExtents()
##cf=CELL.createFrame()
##CELL.insertElement(cf)
#BLOCK=Block((1,1))
#BLOCK.insertElement(CELL)
##bf=BLOCK.createFrame()
##BLOCK.insertElement(bf)
##BLOCK.insertPatterns(details=1)
##ef=a.createBlockFrame()
##a.insertElement(ef)
##bf=a.createEbeamFrame()
##a.insertElement(bf)
##bp=a.createBlockPattern((8,8))
##a.insertElement(bp)
#a.insertElement(BLOCK)
#ac=a.copy()
#ac.insertPatterns()
#a.insertPatterns(details=1)
#gca().clear()
#gca().set_xlim((-500,500))
#gca().set_ylim((-500,500))
#CELL.show(gca())
#a.save("test.gds")
#ac.save("test2.gds")
#
##print CELL.insertExtents()
