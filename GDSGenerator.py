# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 14:45:30 2012

@author: rueffer
"""
import re
import numpy as np
from numpy import sin,cos,pi
from os.path import abspath,dirname
import gdsii.elements as Elements
from gdsii.structure import Structure as gdsiiStruct
from gdsii.library import Library
from matplotlib import patches
from copy import deepcopy
from Settings import colorMap as cmSet

version="0.970"
pat1=re.compile(".+\.([a-zA-Z0-9_]+)'>.*")



def f(xy):
    return xy
    
def rotMatrix(angle):
    return np.array([[cos(angle/180.*np.pi),-sin(angle/180.*np.pi)],[sin(angle/180.*np.pi),cos(angle/180.*np.pi)]])
        ##TODO use this more

class colorMap(dict):       
    def __init__(self):
        super(colorMap,self).__init__(self)
#        self.defineColor(0,[0,128,128],0.3)
#        self.defineColor(1,[128,128,224],0.3)
#        self.defineColor(2,[96,224,96],0.3)
#        self.defineColor(100,[0,38,255],0.2)
#        self.defineColor(101,[255,0,0],0.3)
        for i in cmSet:
            self.defineColor(i[0],i[1],i[2])
            
    def getMPLColor(self,layer):
        return [c/255. for c in self[layer]["color"]]
        
    def getAlpha(self,layer):
        return self[layer]["alpha"]
    
    def defineColor(self,layer,color,alpha=1.0):
        """Layer 0...
        Color=[255,255,555]
        """
        color={"color":color,"alpha":alpha}
        self.update({layer:color})



class Element(object):        
    def __init__(self,**kwargs):
        if len(kwargs) != 0:
            l=kwargs.keys()
            raise KeyError("<"+re.sub(pat1,r"\1",str(type(self)))+"> got unexpected keyword(s): "+str(l))
        pass
        
    def show(self,ax,maxRegion=2.,cmap=colorMap(),pltTransform=f):
        raise NotImplemented
             
    def __getGDS__(self,xy=(0,0),angle=0,mag=1,layer=None,datatype=None,unitsfact=1E3):
        raise NotImplemented
        
    def calcExtents(self):
        raise NotImplemented

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return np.all(self.points == other.points) 
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def copy(self):
        return deepcopy(self)
        
    def __repr__(self):
        return "<"+re.sub(pat1,r"\1",str(type(self)))+">"


class Pattern(Element):
    def __init__(self,**kwargs):
        super(Pattern,self).__init__(**kwargs)
    
        
class Structure(Element):
    def __init__(self,name,layer=None,**kwargs):
        super(Structure,self).__init__(**kwargs)
        self.__childs__=[]
        self.__layer__=layer
        self.name=name
#        self.__struct__=gdsiiStruct(name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if len(self.__childs__)!=len(other.__childs__):
                return False
            out=True
            out = out and self.__layer__ == other.layer
            out = out and self.name == other.name
            for n,child in enumerate(self.__childs__):
                out = out and child["angle"]==other.__childs__[n]["angle"]
                out = out and child["element"]==other.__childs__[n]["element"]
                out = out and child["layer"]==other.__childs__[n]["layer"]
                out = out and child["mag"]==other.__childs__[n]["mag"]
                out = out and np.all(child["xy"]==other.__childs__[n]["xy"])
            return out
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
                
    def __getAllNames__(self):
        ##TODO: improve speed??
        names=[self.name]
        for child in self.__childs__:
            elem=child["element"]
            if isinstance(elem,Structure) or isinstance(elem,Array):
                names.extend(elem.__getAllNames__())
        return names
        
    def getAllPatterns(self,typ=Pattern):
        pat=[]
        for child in self.__childs__:
            elem=child["element"]
            if isinstance(elem,typ):
                pat.append(elem)
        return pat
        
    def __getAllStruct__(self):
        ##TODO: improve speed??
        struct=[self]
        for child in self.__childs__:
            elem=child["element"]
            if isinstance(elem,Structure) or isinstance(elem,Array):
                struct.extend(elem.__getAllStruct__())
        return struct
    
    def getAllStructures(self,typ=None):
        if typ == None:
            return self.__getAllStruct__()[1:]
        elif isinstance(typ,type):
            l=[]
            for s in self.__getAllStruct__()[1:]:
                if isinstance(s,typ):
                    l.append(s)
            return l
        else:
            raise TypeError("typ must be None or of type type")
            
        
    def __structureExists__(self,element):
        if isinstance(element,Array):
            return False
        l=self.__getAllNames__()
        if element.name in l:
            l2=self.__getAllStruct__()
            if l2[l.index(element.name)] != element:
                return element
        return False
        
    def getStructure(self,name):
        l=self.__getAllNames__()
        if name in l:
            l2=self.__getAllStruct__()
            return l2[l.index(name)] 
        raise ValueError("Can't find structure")
        
    def structureNameExists(self,name):
        return name in self.__getAllNames__()
        
    def duplicateStructure(self,element):
        for struct in self.__getAllStruct__():
            res = element.__structureExists__(struct)
            if res:
                if res == element:
                    return True
            return False
     ### DOES NOT CORREcT DUPLICATE NAMES CORRECTLY!!!!!!!!!!!!!!!!!!!   
    def insertElement(self,element,layer=None,xy=(0,0),angle=0,mag=1):
        """Layer must be given for Pattern objects. 
        For Stuctures, layer=None uses the individual layer for each child
                       layer={value} overrides the layer value for all childs
        """
        if isinstance(element,Structure) or isinstance(element,Array):
            if self.duplicateStructure(element):
                raise RuntimeError("Duplicate Structurename")
        elif isinstance(element,Pattern):
            if layer == None and self.__layer__ == None:
                raise ValueError("You must specify a layer for pattern objects if none is given for the structure")
        elif isinstance(element,type(None)):
            return
        else:
            raise TypeError(str(type(element))+"not supported by insertElement")
        self.__childs__.append({"element":element,"layer":layer,
                                "xy":np.array(xy),"angle":angle,"mag":mag})
                                
                                
    def calcExtents(self,xy=(0,0),angle=0,mag=1,**kwargs):
        """returns np.array([[min_x,max_x],[min_y,max_y]])
        """
        rot=np.array([[cos(angle/180.*np.pi),-sin(angle/180.*np.pi)],[sin(angle/180.*np.pi),cos(angle/180.*np.pi)]])
        if len(self.__childs__) == 0:
            return np.array([[0,0],[0,0]])
        ext=np.empty((len(self.__childs__),2,2))
        for n,child in enumerate(self.__childs__):
            pos=child["xy"]
            pos=np.dot(rot,pos)*mag
            pos=pos+np.array(xy)
            ext[n]=child["element"].calcExtents(xy=pos,angle=child["angle"]+angle,mag=child["mag"]*mag)
        ext=np.array([[ext[:,0,0].min(),ext[:,0,1].max()],[ext[:,1,0].min(),ext[:,1,1].max()]])
        return ext
        
    def getLayers(self,layer=None):
        if layer == None and self.__layer__ != None:
            layer = self.__layer__
        layers=set()
        for child in self.__childs__:
            if layer == None:
                l = child["layer"]
            else:
                l = layer
            layers=layers.union(child["element"].getLayers(l))
        return layers
        
    def __getGDS__(self,lib,xy=(0,0),angle=0,mag=1,layer=None,unitsfact=1E3,**kwargs):
#        lib.append(self.__struct__)
##TODO: mirror
        struct=gdsiiStruct(self.name)
        if not self.name in [i.name for i in lib]:
            lib.append(struct)
        if layer == None and self.__layer__ != None:
            layer = self.__layer__
        for child in self.__childs__:
            if layer == None:
                l = child["layer"]
            else:
                l = layer
            liste=child["element"].__getGDS__(lib,xy=child["xy"],angle=child["angle"],mag=child["mag"],
                                              layer=l,unitsfact=unitsfact,**kwargs)
            for l in liste:
#                self.__struct__.append(l)
                struct.append(l)
        pos=np.array(xy)*unitsfact
        elem = Elements.SRef(self.name,[(pos[0],pos[1])])
        elem.angle = angle
        elem.mag = mag
        elem.strans = 0
        return [elem]
        
    def save(self,filename,units=1E-6,physical_unit=1E-9,logical_unit=1E-3):
        lib=Library(5,filename,physical_unit=1E-9,logical_unit=1E-3)
#        lib.append(self.__struct__)            
        self.__getGDS__(lib,units=1E-6,physical_unit=1E-9)[0]
        f=open(filename,"wb")
        lib.save(f)
        f.close()        
    
    def show(self,ax,xy=(0,0),angle=0,mag=1,layer=None,pltTransform=f,maxRegion=2.,cmap=colorMap(),**kwargs):
        if layer == None and self.__layer__ != None:
            layer = self.__layer__
        rot=rotMatrix(angle)
        annotations=[]
        for child in self.__childs__:
            if layer == None:
                l = child["layer"]
            else:
                l = layer
            pos=child["xy"]
            pos=np.dot(rot,pos)
            pos=pos+np.array(xy)
            ##TODO PROBLEM OF POSITIONING!!!!!!!!!!!
            a=child["element"].show(ax,xy=pos,angle=child["angle"]+angle,mag=child["mag"]*mag,layer=l,
                       pltTransform=pltTransform,maxRegion=maxRegion,cmap=cmap)
            if a != None:
				annotations.extend(a)
        return annotations
        
    def __get_name__(self):
        return self.__name__
        
    def __set_name__(self,name):
        if not isinstance(name,str):
            raise TypeError("only strings")
        self.__name__=name
        
#    def __get_layer__(self):
#        return self.__layer__
#        
#    def __set_layer__(self,layer):
#        self.__layer__=layer
        
    name = property(__get_name__,__set_name__)
#    layer = property(__get_layer__,__set_layer__)

    def __repr__(self):
        return super(Structure,self).__repr__()+ ": "+ self.name
        
        
class Array(Element):
    def __init__(self,element,dx,dy,cols,rows,layer=None,globRot=True,centered=False,**kwargs):
        self.__structure__=element
        self.dx=dx
        self.dy=dy
        self.cols=cols
        self.rows=rows
        self.globRot=globRot
        self.centered=centered
        super(Array,self).__init__(**kwargs)
                        
    def __getAllNames__(self):
        return self.__structure__.__getAllNames__()
        
    def __getAllStruct__(self):
        return self.__structure__.__getAllStruct__()
        
    def __structureExists__(self,element):
        return self.__structure__.__structureExists__(element)
        
    def getStructure(self,name):
        return self.__structure__.getStructure(name)
        
    def structureNameExists(self,name):
        return self.__structure__.structureNameExists(name)
        
    def duplicateStructure(self,element):
        return self.__structure__.duplicateStructure(element)
        
    def insertElement(self,element,layer=None,xy=(0,0),angle=0,mag=1):
        raise NotImplementedError
        
    def __getGDS__(self,lib,xy=(0,0),layer=None,angle=0,mag=1,unitsfact=1E3,**kwargs):
        self.__structure__.__getGDS__(lib)
        p1,p2,p3,dx,dy=self.__calcXYs__(xy,angle,unitsfact)
        elem = Elements.ARef(self.__structure__.name,self.rows,self.cols,[(p1[0],p1[1]),(p2[0],p2[1]),(p3[0],p3[1])])
        elem.angle = angle
        elem.mag = mag
        elem.strans = 0
        return [elem]
        
    def getLayers(self,layer=None):
        return self.__struture__.getLayers()
        
    def calcExtents(self,xy=(0,0),angle=0,mag=1,**kwargs):
        """returns np.array([[min_x,max_x],[min_y,max_y]])
        """
        points=np.empty((4,2))
        points[0],points[1],points[2],dx,dy=self.__calcXYs__(xy,angle,1)
        points[1]-=dy
        points[2]-=dx
        points[3]=points[1]+points[2]-points[0]
        ext= np.empty((2,2))
        ext[0][0]=points[:,0].min()
        ext[0][1]=points[:,0].max()
        ext[1][0]=points[:,1].min()
        ext[1][1]=points[:,1].max()
        childext=self.__structure__.calcExtents(xy=(0,0),angle=angle,mag=mag,**kwargs)
        return ext+childext
        
    def show(self,ax,xy=(0,0),angle=0,mag=1,layer=None,pltTransform=f,maxRegion=2.,cmap=colorMap(),**kwargs):
        p1,p2,p3,dx,dy=self.__calcXYs__(xy,angle,1)
        annotations=[]
        for i in range(self.cols):
            for j in range(self.rows):
               a= self.__structure__.show(ax,xy=p1+i*dx+j*dy,angle=angle,mag=mag,
                           pltTransform=pltTransform,maxRegion=maxRegion,cmap=cmap)
               a.extend(annotations)
        return annotations
        
    def __calcXYs__(self,xy,angle,unitsfact):
        dx=np.array([self.dx,0])*unitsfact
        dy=np.array([0,self.dy])*unitsfact
        tab=np.array([self.cols,self.rows])
        rot=np.array([[cos(angle/180.*np.pi),-sin(angle/180.*np.pi)],[sin(angle/180.*np.pi),cos(angle/180.*np.pi)]])
        p3=dx*tab
        p2=dy*tab
        p0=(dx+dy)/2.*(tab-1)
        
        if self.globRot:
            p3=np.dot(rot,p3)
            p2=np.dot(rot,p2)
            p0=np.dot(rot,p0)
        px=np.array(xy)*unitsfact 
        if self.centered:
            p1=px-p0
            p2=p2+px-p0
            p3=p3+px-p0
        else:
            p1=px
            p2=p2+px
            p3=p3+px
                
        dx=(p3-p1)/(tab)
        dy=(p2-p1)/(tab)
            
        return p1,p2,p3,dx,dy
        
        
        
    def __get_dx__(self):
        return self.__dx__
        
    def __set_dx__(self,dx):
        self.__dx__=dx

    def __get_dy__(self):
        return self.__dy__
        
    def __set_dy__(self,dy):
        self.__dy__=dy
        
    def __get_cols__(self):
        return self.__cols__
        
    def __set_cols__(self,cols):
        self.__cols__=cols
        
    def __get_rows__(self):
        return self.__rows__
        
    def __set_rows__(self,rows):
        self.__rows__=rows
        
    def __get_globRot__(self):
        return self.__globRot__
        
    def __set_globRot__(self,globRot):
        self.__globRot__=globRot
        
    def __get_centered__(self):
        return self.__centered__
        
    def __set_centered__(self,centered):
        self.__centered__=centered
        
    dx = property(__get_dx__,__set_dx__)
    dy = property(__get_dy__,__set_dy__)
    cols = property(__get_cols__,__set_cols__)
    rows = property(__get_rows__,__set_rows__)
    globRot = property(__get_globRot__,__set_globRot__)
    centered = property(__get_centered__,__set_centered__)

class Polygon(Pattern):
    def __init__(self,points,**kwargs):
        if isinstance(points,list):
            if points[0]!=points[-1]:
                points=points+[points[0]]
        elif isinstance(points,np.ndarray):
            if np.any(points[0]!=points[-1]):
                points=np.vstack((points,points[0]))
                points=points.tolist()+[points[0].tolist()]
#        print "points:",points[0],points[-1]
        self.__set_points__(points)
                
    def __inMaxRegion__(self,ax,maxRegion=2.):
        points=self.points
        xlim=ax.get_xlim()
        ylim=ax.get_ylim()
        dx=(xlim[1]-xlim[0])*maxRegion
        dy=(ylim[1]-ylim[0])*maxRegion
        maxR= [[xlim[0]-dx,xlim[1]+dx],[ylim[0]-dy,ylim[1]+dy]]
        a = any(abs(points[:,0])>abs(maxR[0][0])) and any(abs(points[:,0])>abs(maxR[0][1]))
        b = any(abs(points[:,1])>abs(maxR[1][0])) and any(abs(points[:,1])>abs(maxR[1][1]))
        answer = not(a or b)
        return answer
        
        
    def __calcPoints__(self,xy=(0,0),angle=0,mag=1,unitsfact=1E3):
        points=self.points.copy()*mag*unitsfact
        rot=np.array([[cos(angle/180.*np.pi),-sin(angle/180.*np.pi)],[sin(angle/180.*np.pi),cos(angle/180.*np.pi)]])
        points=np.dot(points,rot.T)
        temp=np.empty(points.shape)
        temp[:,0]=xy[0]*unitsfact
        temp[:,1]=xy[1]*unitsfact
        points=points+temp
        return points
    
    def calcExtents(self,xy=(0,0),angle=0,mag=1,**kwargs):
        """returns np.array([[min_x,max_x],[min_y,max_y]])
        """
        points=self.__calcPoints__(xy=xy,angle=angle,mag=mag,unitsfact=1)
        max_x=points[:,0].max()
        max_y=points[:,1].max()
        min_x=points[:,0].min()
        min_y=points[:,1].min()
        ##TODO
#        print np.array([[min_x,max_x],[min_y,max_y]])
        return np.array([[min_x,max_x],[min_y,max_y]])
        
    def __getGDS__(self,lib,xy=(0,0),angle=0,mag=1,layer=None,datatype=None,unitsfact=1E3,**kwargs):
        if layer == None:
            raise ValueError("Layer can not be None")
        points=self.__calcPoints__(xy=xy,angle=angle,mag=mag,unitsfact=unitsfact)
        if datatype == None:
            datatype=layer
#        points_ar=np.array(points)
#        points=np.where(abs(points_ar)>1E-10,points_ar,np.zeros(points_ar.shape))
#        print "gds:",points
        elem = Elements.Boundary(layer,datatype,points)
        return [elem]
    
    def getLayers(self,layer=None):
        if layer == None:
            raise ValueError("Layer can not be None")
        return set([layer])
        
        
    def show(self,ax,xy=(0,0),angle=0,mag=1,layer=None,pltTransform=f,maxRegion=2.,cmap=colorMap(),**kwargs):
        points=self.__calcPoints__(xy=xy,angle=angle,mag=mag,unitsfact=1.)
#        if isinstance(self,Rectangle):
#            print points
#            print points
        points=pltTransform(points)
        #TODO: Reimplement
        #if not self.__inMaxRegion__(ax,maxRegion=maxRegion):
            #return
        alpha=cmap.getAlpha(layer)
        color=cmap.getMPLColor(layer)
        annotations=[]
        if alpha != 1.0:
            a1=patches.Polygon(points,ec="none",fc=color,alpha=alpha,**kwargs)
            a2=patches.Polygon(points,ec=color,fc="none",**kwargs)
            ax.add_artist(a1)
            ax.add_artist(a2)
            annotations.append(a1)
            annotations.append(a2)
        else:
            a=patches.Polygon(points,ec=color,fc=color,**kwargs)
            ax.add_artist(a)
            annotations.append(a)
        return annotations
        
    def __get_points__(self):
        return self.__points__
        
    def __set_points__(self,points):
        points=np.array(points)
        if points.shape[1] == 2 and points.shape[0] > 2:
            self.__points__=points
        else:
            raise ValueError("invalid format for points")
        
    points = property(__get_points__,__set_points__)
    
class Square(Polygon):
    def __init__(self,width,**kwargs):
        self.__width__=width
        points=self.__toPolygon__()
        super(Square,self).__init__(points,**kwargs)
        
    def __toPolygon__(self):
        w=self.width
        return  np.array([[w/2.,w/2.],[-w/2.,w/2.],[-w/2.,-w/2.],[w/2.,-w/2.]])
        

    def __get_width__(self):
        return self.__width__
        
    def __set_width__(self,width):
        self.__width__=width
        self.points=self.__toPolygon__()
        
    width = property(__get_width__,__set_width__)
    
    

class Rectangle(Square):
    def __init__(self,width,height,**kwargs):
        self.__height__=height
        super(Rectangle,self).__init__(width,**kwargs)
                       
    def __toPolygon__(self):
        w=self.width
        h=self.height
        return  np.array([[w/2.,h/2.],[-w/2.,h/2.],[-w/2.,-h/2.],[w/2.,-h/2.]])
        
    def __get_height__(self):
        return self.__height__
        
    def __set_height__(self,height):
        self.__height__=height
        self.points=self.__toPolygon__()
        
    height = property(__get_height__,__set_height__)
    
    
class Circle(Polygon):
    def __init__(self,radius,res=100,**kwargs):
        self.__r__=radius
        self.__res__=res
        points=self.__toPolygon__()
        super(Circle,self).__init__(points,**kwargs)
        
    def __toPolygon__(self):
        return  np.array([(sin(i)*self.r,cos(i)*self.r) for i in np.arange(0,2*pi,2*pi/self.res)])
        
            
    def __get_r__(self):
        return self.__r__
        
    def __set_r__(self,r):
        self.__r__=r
        self.points=self.__toPolygon__()
        
    def __get_res__(self):
        return self.__res__
        
    def __set_res__(self,res):
        self.__res__=res
        self.points=self.__toPolygon__()
        
    r = property(__get_r__,__set_r__)
    res = property(__get_res__,__set_res__)
                
        
class Path(Polygon):
    def __init__(self,points,width=1,**kwargs):
        self.width=width
        super(Path,self).__init__(points,**kwargs)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return np.all(self.points == other.points) and self.width == other.width
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

        
    def __set_points__(self,points):
        points=np.array(points)
        if points.shape[1] == 2 and points.shape[0] > 1:
            self.__points__=points
        else:
            raise ValueError("invalid format for points")
            
    def __getGDS__(self,lib,xy=(0,0),angle=0,mag=1,layer=None,datatype=None,unitsfact=1E3,**kwargs):
        if layer == None:
            raise ValueError("Layer can not be 0")
        points=self.__calcPoints__(xy=xy,angle=angle,mag=mag,unitsfact=unitsfact)
        if datatype == None:
            datatype=layer
        elem = Elements.Path(layer,datatype,points)
        return [elem]
        
    def show(self,ax,xy=(0,0),angle=0,mag=1,layer=None,pltTransform=f,maxRegion=2.,cmap=colorMap(),**kwargs):
        points=self.__calcPoints__(xy=xy,angle=angle,mag=mag,unitsfact=1.)
        points=pltTransform(points)
        if not self.__inMaxRegion__(ax,maxRegion=maxRegion):
            return
        alpha=cmap.getAlpha(layer)
        color=cmap.getMPLColor(layer)
        if points[-1][0] == points[0][0] and points[-1][1] == points[0][1]:
            closed = True
        else:
            closed = False
        a=patches.Polygon(points,ec=color,fc="none",alpha=alpha,closed=closed,lw=self.width,**kwargs)
        ax.add_artist(a)  
        return [a]
        
    def __get_width__(self):
        return self.__width__
        
    def __set_width__(self,width):
        self.__width__=width
        
    width = property(__get_width__,__set_width__)
    

thispath = abspath(dirname(__file__))
__glyphLibPath__="ressources/lib_glyphs.gds"

class GlyphLib(dict):
    def __init__(self,path=__glyphLibPath__,height=1E5,**kwargs):
        f=open(path,"rb")
        glyphLib=Library.load(f)
        f.close()
        self.width=0.85
        for glyph in glyphLib:
            p=np.array([np.array(poly.xy)/height for poly in glyph])
            self.update({glyph.name:p})

class Text(Pattern):
    def __init__(self,text,height=10.,ha="center",va="center",spacing=0.5,glyphLib=GlyphLib(),**kwargs):
        self.__text__=text
        self.__height__=height
        self.__ha__=ha
        self.__va__=va
        self.__spacing__=spacing
        self.__gL__=glyphLib
        super(Text,self).__init__(**kwargs)
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            out=True
            out = out and self.text == other.text
            out = out and self.height == other.height
            out = out and self.ha == other.ha
            out = out and self.va == other.va
            out = out and self.spacing == other.spacing
            return out
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
        
    def getLayers(self,layer=None):
        if layer == None:
            raise ValueError("Layer can not be None")
        return set([layer])
                       
    def __getPoly__(self,xy=(0,0),angle=0,mag=1,layer=None,datatype=None,**kwargs):
        height=self.height  *mag
        lines = self.text.split("\n")
        #print type(height)
        #print type(self.__gL__.width)
        w=self.__gL__.width*height
        maxLength=max([len(l)*w for l in lines])
        
        rot=np.array([[cos(angle/180.*np.pi),-sin(angle/180.*np.pi)],[sin(angle/180.*np.pi),cos(angle/180.*np.pi)]])
        dx=np.array([w,0])
        dy=np.array([0,height*(1.+self.spacing)])
        dx=np.dot(rot,dx)
        dy=np.dot(rot,dy)
        
        topright=np.array([maxLength,height*len(lines)+(len(lines)-1)*height*self.spacing])
        topright=np.dot(rot,topright)
        bottomright=np.array([maxLength,0])
        bottomright=np.dot(rot,bottomright)
        topleft=np.array([0,height*len(lines)+(len(lines)-1)*height*self.spacing])
        topleft=np.dot(rot,topleft)
        px=np.array([i[0] for i in topright,bottomright,topleft])
        py=np.array([i[1] for i in topright,bottomright,topleft])
        if self.va == "center":
            y0=-topright[1]/2.
        elif self.va == "top":
            y0=-py[np.argmax(abs(py))]
        elif self.va == "bottom":
            y0=py[np.argmin(abs(py))]
        else:
            raise ValueError('use va=["top","center","bottom"]')
        if self.ha == "center":
            x0=-topright[0]/2.
        elif self.ha == "right":
            x0=-px[np.argmax(abs(px))]
        elif self.ha == "left":
            x0=px[np.argmin(abs(px))]
        else:
            raise ValueError('use ha=["left","center","right"]') 
        poly=[]
        for n,line in enumerate(lines[::-1]):
            for m,glyph in enumerate(line):
                if glyph == " ":
                    pass
                elif not self.__gL__.has_key(glyph):
                    temp=sorted(self.__gL__.keys())
                    raise ValueError("'"+glyph +"' not allowd. Please use only symbols in:" + str(temp))
                else:
                    for points in self.__gL__[glyph]:
                        points2=np.dot(points.copy(),rot.T)*height
                        points2[:,0]+=(m*dx[0]+n*dy[0]+x0+xy[0])
                        points2[:,1]+=(m*dx[1]+n*dy[1]+y0+xy[1])
                        points2=points2
                        poly.append(Polygon(points2))
                        ##TODO
        return poly

    def calcExtents(self,xy=(0,0),angle=0,mag=1,**kwargs):
        """returns np.array([[min_x,max_x],[min_y,max_y]])
        """
        poly=self.__getPoly__(xy=xy,angle=angle,mag=mag,**kwargs)
        if len(poly) == 0:
            return np.array([[0,0],[0,0]])
        ext=np.empty((len(poly),2,2))
        for n,polygon in enumerate(poly):
            ext[n]=polygon.calcExtents(xy=(0,0),angle=0)
#            ext[n]=polygon.calcExtents(xy=(0,0),angle=angle)
        ext=np.array([[ext[:,0,0].min(),ext[:,0,1].max()],[ext[:,1,0].min(),ext[:,1,1].max()]])
        return ext
        
        
    def __getGDS__(self,lib,xy=(0,0),angle=0,mag=1,layer=None,datatype=None,unitsfact=1E3,**kwargs):
        if layer == None:
            raise ValueError("Layer can not be 0")
        if datatype == None:
            datatype=layer
#        print "--------GDS"
#        print "angle",angle
#        print "xy",xy
        poly=self.__getPoly__(xy=xy,angle=angle,mag=mag,layer=layer,datatype=datatype,**kwargs)
        gds=[]
        for p in poly:
            gds.append(p.__getGDS__(lib,xy=(0,0),angle=0,mag=1,layer=layer,unitsfact=unitsfact)[0])
        return gds
                
    def show(self,ax,xy=(0,0),angle=0,mag=1,layer=None,pltTransform=f,maxRegion=2.,cmap=colorMap(),**kwargs):
        if layer == None:
            raise ValueError("Layer can not be 0")
#        print "--------show"
#        print "angle",angle
#        print "xy",xy
        poly=self.__getPoly__(xy=xy,angle=angle,mag=mag,layer=layer,**kwargs)
        annotations=[]
        for p in poly:
            a=p.show(ax,xy=(0,0),angle=0,mag=1,layer=layer,pltTransform=pltTransform,maxRegion=maxRegion,cmap=cmap)
            annotations.extend(a)
        return annotations
    
    def __calcExtent__(self):
        raise NotImplemented
    
    def __get_text__(self):
        return self.__text__
        
    def __set_text__(self,text):
        self.__text__=text
    
    def __get_height__(self):
        return self.__height__
        
    def __set_height__(self,height):
        self.__height__=height
    
    def __get_ha__(self):
        return self.__ha__
        
    def __set_ha__(self,ha):
        self.__ha__=ha
    
    def __get_va__(self):
        return self.__va__
        
    def __set_va__(self,va):
        self.__va__=va
        
    def __get_spacing__(self):
        return self.__spacing__
        
    def __set_spacing__(self,spacing):
        self.__spacing__=spacing
        
    spacing = property(__get_spacing__,__set_spacing__)
    va = property(__get_va__,__set_va__)
    ha = property(__get_ha__,__set_ha__)
    height = property(__get_height__,__set_height__)
    text = property(__get_text__,__set_text__)
    
    def __repr__(self):
        return super(Text,self).__repr__()+ ": "+ self.text
    
#if __name__ == "__main__":
##    t=Structure("t")
##    t.insertElement(Circle(100),layer=0)
##    t.insertElement(Circle(100),xy=(200,0),layer=0)
##    t.save("test.gds")
#    r=Structure("r")
##    r.insertElement(t)
#    #r.insertElement(t,xy=(200,0))
#    
#    t2=Structure("t2")
#    
##    t2.insertElement(Square(50),layer=0)
##    ar=Array(t2,200,200,4,4,centered=False)
#    tx1=Text("Wleft\ntest",ha="left",va="top",height=100.)
#    #tx2=Text("Wcenter",ha="center")
#    #tx3=Text("Wright",ha="right")
#    #ar.insertElement(t2,layer=1,xy=(0,0))
#    t2.insertElement(tx1,layer=1,xy=(0,0),angle=45)
#    #t2.insertElement(tx3,layer=1,xy=(0,-20))
#    #t2.insertElement(Rectangle(50,25),layer=0)
#    #t2.insertElement(Square(50),layer=0)
##    r.insertElement(ar,xy=(200,0),angle=0,mag=2)
#    r.insertElement(t2,xy=(0,0))
#    #r.insertElement(ar,xy=(-200,0))
#    fig=figure()
#    ax=fig.add_subplot(111)
#    ax.set_xlim((-700,700))
#    ax.set_ylim((-700,700))
#    r.show(ax)
#    r.save("test.gds")
