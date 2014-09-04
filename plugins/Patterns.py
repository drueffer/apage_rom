# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 11:17:55 2012

@author: rueffer
"""
import numpy as np
import time
from PatternGenerator import *

# Must always be (self,name,library,..*args,unitFact=1E3,**kwargs)
# Please indicate the name of the pattern and give a dict with name allPatterns


## TODO: "Private" variables to faciLaitate creation


#===============================================================================
# defined for NanoWire object:
# "top":(10,10)
# "bottom":(-10,-10)
#===============================================================================
    
class NanoWire(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs): 
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        self.updateDefaultValue("textsize",3.)
        self.updateDefaultValue("spacing",5.)
        self.updateDefaultValue("width",1.)
        self.updateDefaultValue("text","")
        super(NanoWire,self).__init__(name,descriptor=descriptor,layer=self.descriptor.commentLayer,**kwargs)
    
    def make(self):
        if self.end1[1]>self.end2[1]:
            top=np.array(self.end1)
            bot=np.array(self.end2)
        else:
            top=np.array(self.end2)
            bot=np.array(self.end1)
        center=(top+bot)/2.
        d=(top-bot)
        length=np.sqrt(np.dot(d,d))
        angle=np.mod((-np.arcsin(np.cross(d/length,[0.,1.]))*180./np.pi),180)
        x=-self.spacing
        nw=Structure(self.name+"_cont")
        if self.text == "":
            text = self.name
        else:
            text = self.text
        text=Text(text,height=self.textsize,ha="center",va="bottom")
        nw.insertElement(Rectangle(self.width,length),layer=self.layer)
        nw.insertElement(text,xy=(x,0),angle=270,layer=self.layer)
        self.insertElement(nw,xy=center,angle=angle)

class Antenna(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "thickSquare":50,
     	"lates":300,
        "radius":0.2,
        "number":1,
        "vertDistance":0.84,
        "radDistance":0.3,
        "layerDots":self.descriptor.defExposureLayer+1,
        "textHeight":50.
        })
        super(Antenna,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        t=self.name.split("_")[0]
        contacts.insertElement(Text(t,va="bottom",ha="right",height=self.textHeight),xy=[self.lates/2+self.thickSquare+self.textHeight+20,+self.lates/2+self.thickSquare],layer=self.layer,angle=270)
        contacts.insertElement(Text(t,va="bottom",ha="right",height=20),xy=[90,60],layer=self.layer,angle=270)
		
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        center=(top+bot)/2.
        rot=rotMatrix(angle)
        number=int(self.number)
        zero1=np.array([-self.radDistance/2.,-self.vertDistance*(number-1)/2.])
        zero2=np.array([self.radDistance/2.,-self.vertDistance*(number-1)/2.])
        rectangle1=[[-self.lates/2-self.thickSquare,self.lates/2],[self.lates/2+self.thickSquare,self.lates/2],[self.lates/2+self.thickSquare,self.lates/2+self.thickSquare],[-self.lates/2-self.thickSquare,self.lates/2+self.thickSquare]]
      	rectangle2=[[-self.lates/2-self.thickSquare,-self.lates/2],[self.lates/2+self.thickSquare,-self.lates/2],[self.lates/2+self.thickSquare,-self.lates/2-self.thickSquare],[-self.lates/2-self.thickSquare,-self.lates/2-self.thickSquare]]
        rectangle3=[[-self.lates/2-self.thickSquare,self.lates/2],[-self.lates/2,self.lates/2],[-self.lates/2,-self.lates/2],[-self.lates/2-self.thickSquare,-self.lates/2]]
        rectangle4=[[self.lates/2,self.lates/2],[self.lates/2+self.thickSquare,self.lates/2],[self.lates/2+self.thickSquare,-self.lates/2],[self.lates/2,-self.lates/2]]
        recsmall1=[[-60,50],[60,50],[60,60],[-60,60]]
        recsmall2=[[-60,-50],[60,-50],[60,-60],[-60,-60]]
        recsmall3=[[60,50],[60,-50],[50,-50],[50,50]]
        recsmall4=[[-60,50],[-60,-50],[-50,-50],[-50,50]]
        contacts=Structure(self.name+"_contacts")
        for i in range(number):
            p1=zero1+np.array([0.,self.vertDistance*i])
            contacts.insertElement(Circle(self.radius/2.),xy=p1,layer=self.layerDots)
            p2=zero2+np.array([0.,self.vertDistance*i])
            contacts.insertElement(Circle(self.radius/2.),xy=p2,layer=self.layerDots)
        contacts.insertElement(Polygon(recsmall1),layer=self.layer)
        contacts.insertElement(Polygon(recsmall2),layer=self.layer)
        contacts.insertElement(Polygon(recsmall3),layer=self.layer)
        contacts.insertElement(Polygon(recsmall4),layer=self.layer)
        contacts.insertElement(Polygon(rectangle1),layer=self.layer)
        contacts.insertElement(Polygon(rectangle2),layer=self.layer)
        contacts.insertElement(Polygon(rectangle3),layer=self.layer)
        contacts.insertElement(Polygon(rectangle4),layer=self.layer)
        self.createText(contacts)
        self.insertElement(contacts,angle=angle,xy=center)
		
    def getDefLayers(self):
        return super(Antenna,self).getDefLayers().union(set([self.layerDots]))
        
        
class Pt2Contacts(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "padSize":150.,
        "overlap":1.,
        "padContact":10.,
        "padSpacing":200.,
        "intLength":5.,
        "widthAtWire":2.,
        "textHeight":20.,
        })
        super(Pt2Contacts,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def make(self):
        if self.end1[1]>self.end2[1]:
            top=np.array(self.end1)
            bot=np.array(self.end2)
        else:
            top=np.array(self.end2)
            bot=np.array(self.end1)
        center=(top+bot)/2.
        d=(top-bot)
        length=np.sqrt(np.dot(d,d))
        angle=np.mod((-np.arcsin(np.cross(d/length,[0.,1.]))*180./np.pi),180)
        space=self.padSpacing
        pad=self.padSize
        pc=self.padContact
        waw=self.widthAtWire
        ol=self.overlap
        iL=self.intLength
        rot=rotMatrix(angle)
        waw=np.dot(rot,np.array([waw,0]))/2.
        ol=np.dot(rot,np.array([0,ol]))
        iL=np.dot(rot,np.array([0,iL]))
        p0=np.array([[space/2.+pc,space/2.],[space/2.+pad,space/2.],
             [space/2.+pad,space/2.+pad],[space/2.,space/2.+pad],[space/2.,space/2.+pc]])
        if top[0]>=center[0]:
            a=+1
            b=-1
            ang1=0
            ang2=180
        else:
            a=-1
            b=+1
            ang1=90
            ang2=270
        points1=np.vstack((np.array(top)+ol*a+waw*b,np.array(top)+iL*b+waw*b,
                           np.dot(rotMatrix(ang1),p0.T).T,
                           np.array(top)+iL*b+waw*a+np.array([waw[1]*a,0.]),np.array(top)+ol*a+waw*a))
        points2=np.vstack((np.array(bot)+ol*b+waw*a,np.array(bot)+iL*a+waw*a,
                           np.dot(rotMatrix(ang2),p0.T).T,
                           np.array(bot)+iL*a+waw*b+np.array([waw[1]*b,0.]),np.array(bot)+ol*b+waw*b))
        self.insertElement(Polygon(points1),layer=self.layer)
        self.insertElement(Polygon(points2),layer=self.layer)
        t=self.name.split("_")[0]
        self.insertElement(Text(t,va="bottom",ha="right",height=self.textHeight),xy=np.array([space/2.+pad,space/2.+pad])*1.1,layer=self.layer,angle=180)
        return rot,p0,ang1,ang2,top,bot,a,b
        

class Pt4Contacts(Pt2Contacts):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "contactDist":2.,
        "overlap2":1.,
        "intLength2":5.,
        "widthAtWire2":1.
        })
        super(Pt4Contacts,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def make(self):
        rot,p0,ang1,ang2,top,bot,a,b = super(Pt4Contacts,self).make()
        
        cD=self.contactDist
        cD=np.dot(rot,np.array([0,cD]))
        waw=self.widthAtWire2
        ol=self.overlap2
        iL=self.intLength2
        waw=np.dot(rot,np.array([waw,0]))/2.
        ol=np.dot(rot,np.array([0,ol]))
        iL=np.dot(rot,np.array([0,iL]))
        rot=rotMatrix(90)
        waw=np.dot(rot,waw)
        ol=np.dot(rot,ol)+cD
        iL=np.dot(rot,iL)-cD
        ang1+=90
        ang2+=90
        points3=np.vstack((np.array(top)+ol*a+waw*b,np.array(top)+iL*b+waw*b+np.array([0.,waw[0]*a]),
                           np.dot(rotMatrix(ang1),p0.T).T,
                           np.array(top)+iL*b+waw*a,np.array(top)+ol*a+waw*a))
        points4=np.vstack((np.array(bot)+ol*b+waw*a,np.array(bot)+iL*a+waw*a+np.array([0.,waw[0]*b]),
                           np.dot(rotMatrix(ang2),p0.T).T,
                           np.array(bot)+iL*a+waw*b,np.array(bot)+ol*b+waw*b))
        self.insertElement(Polygon(points3),layer=self.layer)
        self.insertElement(Polygon(points4),layer=self.layer)
        
        
class Pt2ContactsDots(Pt2Contacts):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "radius":0.5,
        "number":5,
        "distance":2.,
        "layerDots":self.descriptor.defExposureLayer+1
        })
        super(Pt2ContactsDots,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def getDefLayers(self):
        return super(Pt2ContactsDots,self).getDefLayers().union(set([self.layerDots]))
        
    def make(self):
        rot,p0,ang1,ang2,top,bot,a,b = super(Pt2ContactsDots,self).make()
        center=(top+bot)/2.
        d=(top-bot)
        length=np.sqrt(np.dot(d,d))
        direction=d/length
        number=int(self.number)
        zero=center-direction*self.distance*(number-1)/2.
        for i in range(number):
            p=zero+direction*self.distance*i
            self.insertElement(Circle(self.radius/2.),xy=p,layer=self.layerDots)
        
        
class Simple2Pt(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):     
        self.descriptor=descriptor      
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "padSpacing":200.,
        "pad":150.,
        "width":1.,
        "intLength":5.,
        "widthAtPad":10.,
        "overlap":1.,
        "textSpacing":20.,
        "textHeight":20.,
        "padLayer":1,
        "jointOverlap":2.,
        })
        super(Simple2Pt,self).__init__(name,descriptor=descriptor,**kwargs)
    
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        l=length-2.*self.overlap
        t=self.name.split("_")[0]+" L:"+"%.2f"%l
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.layer,xy=[0,(self.padSpacing/2.+self.pad+self.textSpacing)])
        
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        W=self.width
        D=length/2.-self.overlap
        ps=self.padSpacing
        p=self.pad
        wp=self.widthAtPad
        iL=self.intLength
        jO=self.jointOverlap
        p1a=[[wp/2.,ps/2.],[W/2.,D+iL],[-W/2.,D+iL],[-wp/2.,ps/2.],
            [-p/2.,ps/2.],[-p/2.,ps/2.+p],[p/2.,ps/2.+p],[p/2.,ps/2.]]
        p1b=[[W/2.,D+iL+jO],[W/2.,D],[-W/2.,D],[-W/2.,D+iL+jO]]
        p2a=myRotate(np.array(p1a),180)
        p2b=myRotate(np.array(p1b),180)
        contacts=Structure(self.name+"_contacts")
        contacts.insertElement(Polygon(p1a),layer=self.padLayer)
        contacts.insertElement(Polygon(p1b),layer=self.layer)
        contacts.insertElement(Polygon(p2a),layer=self.padLayer)
        contacts.insertElement(Polygon(p2b),layer=self.layer)
        self.createText(contacts)
        self.insertElement(contacts,angle=angle,xy=center)
        return W,D,p,ps,wp,length,angle,contacts
        
    def getDefLayers(self):
        return super(Simple2Pt,self).getDefLayers().union(set([self.padLayer]))
        
class pn_Junction(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):     
        self.descriptor=descriptor      
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "padSpacing":300.,
        "pad":200.,
        "width":1.,
        "intLength":5.,
        "widthAtPad":10.,
        "overlap":1.,
        "textSpacing":50.,
        "textHeight":80.,
        "layer_p":1,
        "layer_n":2,
        "jointOverlap":2.,
        })
        super(pn_Junction,self).__init__(name,descriptor=descriptor,**kwargs)
    
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        l=length-2.*self.overlap
        t=self.name.split("_")[0]+" L:"+"%.2f"%l
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.layer,xy=[0,(self.padSpacing/2.+self.pad+self.textSpacing)])
        
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        W=self.width
        D=length/2.-self.overlap
        ps=self.padSpacing
        p=self.pad
        wp=self.widthAtPad
        iL=self.intLength
        jO=self.jointOverlap
        p1a=[[wp/2.,ps/2.],[W/2.,D+iL],[-W/2.,D+iL],[-wp/2.,ps/2.],
            [-p/2.,ps/2.],[-p/2.,ps/2.+p],[p/2.,ps/2.+p],[p/2.,ps/2.]]
        p1b=[[W/2.,D+iL+jO],[W/2.,D],[-W/2.,D],[-W/2.,D+iL+jO]]
        p2a=myRotate(np.array(p1a),180)
        p2b=myRotate(np.array(p1b),180)
        contacts=Structure(self.name+"_contacts")
        contacts.insertElement(Polygon(p1a),layer=self.layer)
        contacts.insertElement(Polygon(p1b),layer=self.layer_n)
        contacts.insertElement(Polygon(p2a),layer=self.layer)
        contacts.insertElement(Polygon(p2b),layer=self.layer_p)
        self.createText(contacts)
        self.insertElement(contacts,angle=angle,xy=center)
        return W,D,p,ps,wp,length,angle,contacts
        
    def getDefLayers(self):
        return super(pn_Junction,self).getDefLayers().union(set([self.layer_p,self.layer_n]))
        
        
class pn_Antenna(pn_Junction,Simple2Pt):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "width2":0.5,
        "intLength2":5.,
        "gap":0.5,
        "lates":0.2,
        "number":5,
        "vertDistance":1.13,
        "antDistance":0.2,
        "layerTriangols":3
        })
        super(pn_Antenna,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def make(self):
        W,D,p,ps,wp,length,angle,contacts=super(pn_Antenna,self).make()
        number=int(self.number)
      	antennaDist= -self.antDistance
        zero1=np.array([-antennaDist/2.,-self.vertDistance*(number-1)/2.])
        zero2=np.array([antennaDist/2.,-self.vertDistance*(number-1)/2.])
        for i in range(number):
            p1=zero1+np.array([0.,self.vertDistance*i])
            t1=[[p1[0],p1[1]],[p1[0]+self.lates*np.sqrt(3)/2,p1[1]-self.lates/2],[p1[0]+self.lates*np.sqrt(3)/2,p1[1]+self.lates/2]]
            tri1=myRotate(np.array(t1),180)
            contacts.insertElement(Polygon(tri1),layer=self.layerTriangols)
            p2=zero2+np.array([0.,self.vertDistance*i])
            t2=[[p2[0],p2[1]],[p2[0]-self.lates*np.sqrt(3)/2,p2[1]-self.lates/2],[p2[0]-self.lates*np.sqrt(3)/2,p2[1]+self.lates/2]]
            tri2=myRotate(np.array(t2),180)
            contacts.insertElement(Polygon(tri2),layer=self.layerTriangols)
            
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        l=length-2.*self.gap-2.*self.overlap-self.width2
        t=self.name.split("_")[0]+"-%.3fum"%self.antDistance
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.padLayer,xy=[0,(self.padSpacing/2.+self.pad+self.textSpacing)])
        
			
    def getDefLayers(self):
        return super(pn_Antenna,self).getDefLayers().union(set([self.layerTriangols]))


class Simple4Pt(Simple2Pt):
    def __init__(self,name,descriptor=None,**kwargs):     
        self.descriptor=descriptor        
        self.updateDefaultValue("width2",0.5)
        self.updateDefaultValue("intLength2",5.)
        self.updateDefaultValue("gap",0.5)
        self.updateDefaultValue("makeGuide",False)        
        self.updateDefaultValue("guideWidth",20.)      
        self.updateDefaultValue("guideLength",200.)   
        self.updateDefaultValue("guideDist",50.)
        super(Simple4Pt,self).__init__(name,descriptor=descriptor,**kwargs)
               
    
    def createGuide(self,contacts):
        ps=self.padSpacing
        p=self.pad
        w=self.guideWidth
        l=self.guideLength
        d=self.guideDist
        points=np.array([[w/2.,p+ps+d],[w/2.,p+ps+d+l],[-w/2.,p+ps+d+l],[-w/2.,p+ps+d]])
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.])
        contacts.insertElement(Polygon(points*np.array([1.,-1.])),layer=self.layer,xy=[0.,0.])
        
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        l=length-2.*self.gap-2.*self.overlap-self.width2
        t=self.name.split("_")[0]+" L:"+"%.2f"%l
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.layer,xy=[0,(self.padSpacing/2.+self.pad+self.textSpacing)])
        
    def make(self,oneSide=False):
        W,D,p,ps,wp,length,angle,contacts=super(Simple4Pt,self).make()
        ## HERE THE NEW STUFF GOES IN
        D2=length/2.-self.gap-self.overlap-self.width2/2.
        W2=self.width2
        ol=self.overlap
        iL2=self.intLength2
        jO=self.jointOverlap        
        p1a=[[wp/2+D2,ps/2.],[W2/2.+D2,iL2],[-W2/2.+D2,iL2],[-wp/2.+D2,ps/2.],
            [-p/2.,ps/2.],[-p/2.,ps/2.+p],[p/2.,ps/2.+p],[p/2.,ps/2.]]
        p1b=[[W2/2.+D2,iL2+jO],[W2/2.+D2,-ol],[-W2/2.+D2,-ol],[-W2/2.+D2,iL2+jO]]
        p1a=myRotate(np.array(p1a),90)
        p2a=myRotate(np.array(p1a),180)
        if oneSide:
            p2a[:,0]=-p2a[:,0]
        p1b=myRotate(np.array(p1b),90)
        p2b=myRotate(np.array(p1b),180)
        if oneSide:
            p2b[:,0]=-p2b[:,0]
        contacts.insertElement(Polygon(p1a),layer=self.padLayer)
        contacts.insertElement(Polygon(p2a),layer=self.padLayer)
        contacts.insertElement(Polygon(p1b),layer=self.layer)
        contacts.insertElement(Polygon(p2b),layer=self.layer)
        ## HERE THE NEW STUFF IS DONE
        if self.makeGuide:
            self.createGuide(contacts)
        return W,D,p,ps,wp,length,angle,contacts
        
class Equiv4Pt(Simple2Pt):
    def __init__(self,name,descriptor=None,**kwargs):     
        self.descriptor=descriptor        
#        try:
#            self.kwargs
#        except:
#            self.kwargs={}
#        self.kwargs.update({
#        "width2":0.5,
#        "intLength2":5.,
#        "probelength":4.,
#        "padLayer":0.,
#        })
        self.updateDefaultValue("width2",0.5)
        self.updateDefaultValue("intLength2",5.)
        self.updateDefaultValue("probelength",4.)
        self.updateDefaultValue("padLayer",0)
        super(Equiv4Pt,self).__init__(name,descriptor=descriptor,**kwargs)
    
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        t=self.name.split("_")[0]
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.layer,xy=[0,(self.padSpacing/2.+self.pad+self.textSpacing)])
        
    def make(self,oneSide=False):
        W,D,p,ps,wp,length,angle,contacts=super(Equiv4Pt,self).make()
        ## HERE THE NEW STUFF GOES IN
        D2=self.probelength
        W2=self.width2
        ol=self.overlap
        iL2=self.intLength2
        jO=self.jointOverlap        
        p1a=[[wp/2+D2,ps/2.],[W2/2.+D2,iL2],[-W2/2.+D2,iL2],[-wp/2.+D2,ps/2.],
            [-p/2.,ps/2.],[-p/2.,ps/2.+p],[p/2.,ps/2.+p],[p/2.,ps/2.]]
        p1b=[[W2/2.+D2,iL2+jO],[W2/2.+D2,-ol],[-W2/2.+D2,-ol],[-W2/2.+D2,iL2+jO]]
        p1a=myRotate(np.array(p1a),90)
        p2a=myRotate(np.array(p1a),180)
        if oneSide:
            p2a[:,0]=-p2a[:,0]
        p1b=myRotate(np.array(p1b),90)
        p2b=myRotate(np.array(p1b),180)
        if oneSide:
            p2b[:,0]=-p2b[:,0]
        contacts.insertElement(Polygon(p1a),layer=self.padLayer)
        contacts.insertElement(Polygon(p2a),layer=self.padLayer)
        contacts.insertElement(Polygon(p1b),layer=self.layer)
        contacts.insertElement(Polygon(p2b),layer=self.layer)
        ## HERE THE NEW STUFF IS DONE
        return W,D,p,ps,wp,length,angle,contacts


class Hall(Simple2Pt):
    def __init__(self,name,descriptor=None,**kwargs):     
        self.descriptor=descriptor        
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "width2":0.5,
        "intLength2":5.,
        "gap":0.5
        })
        super(Hall,self).__init__(name,descriptor=descriptor,**kwargs)
    
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        l=length-2.*self.gap-2.*self.overlap-self.width2
        t=self.name.split("_")[0]+" L:"+"%.2f"%l
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.layer,xy=[0,(self.padSpacing/2.+self.pad+self.textSpacing)])
        
    def make(self,oneSide=False):
        W,D,p,ps,wp,length,angle,contacts=super(Hall,self).make()
        top,bot,center,d,length,angle=self.getCoords()
        ## HERE THE NEW STUFF GOES IN
        g=self.gap
        W2=self.width2
        iL2=self.intLength2
        jO=self.jointOverlap        
        p1a=[[wp/2,ps/2.],[W2/2.,iL2],[-W2/2.,iL2],[-wp/2.,ps/2.],
            [-p/2.,ps/2.],[-p/2.,ps/2.+p],[p/2.,ps/2.+p],[p/2.,ps/2.]]
        p1b=[[W2/2.,iL2+jO],[W2/2.,g/2],[-W2/2.,g/2],[-W2/2.,iL2+jO]]
        p1a=myRotate(np.array(p1a),90)
        p2a=myRotate(np.array(p1a),180)
        if oneSide:
            p2a[:,0]=-p2a[:,0]
        p1b=myRotate(np.array(p1b),90)
        p2b=myRotate(np.array(p1b),180)
        if oneSide:
            p2b[:,0]=-p2b[:,0]
        contacts.insertElement(Polygon(p1a),layer=self.padLayer)
        contacts.insertElement(Polygon(p2a),layer=self.padLayer)
        contacts.insertElement(Polygon(p1b),layer=self.layer)
        contacts.insertElement(Polygon(p2b),layer=self.layer)
        ## HERE THE NEW STUFF IS DONE
        return W,D,p,ps,wp,length,angle,contacts


class Gate2p(Simple2Pt):
    def __init__(self,name,descriptor=None,**kwargs):     
        self.descriptor=descriptor        
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "widthGate":0.5,
        "intLengthGate":5.,
		"gateLayer":2
        })
        super(Gate2p,self).__init__(name,descriptor=descriptor,**kwargs)
    
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        l=length-2.*self.overlap-self.widthGate
        t=self.name.split("_")[0]+" L:"+"%.2f"%l
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.layer,xy=[0,(self.padSpacing/2.+self.pad+self.textSpacing)])
        
    def make(self,oneSide=False):
        W,D,p,ps,wp,length,angle,contacts=super(Gate2p,self).make()
        top,bot,center,d,length,angle=self.getCoords()
        ## HERE THE NEW STUFF GOES IN
        W2=self.widthGate
        iL2=self.intLengthGate
        jO=self.jointOverlap        
        p1a=[[wp/2,ps/2.],[W2/2.,iL2],[-W2/2.,iL2],[-wp/2.,ps/2.],
            [-p/2.,ps/2.],[-p/2.,ps/2.+p],[p/2.,ps/2.+p],[p/2.,ps/2.]]
        p1b=[[W2/2.,iL2+jO],[W2/2.,-1.],[-W2/2.,-1.],[-W2/2.,iL2+jO]]
        p1a=myRotate(np.array(p1a),90)
        p2a=myRotate(np.array(p1a),180)
        if oneSide:
            p2a[:,0]=-p2a[:,0]
        p1b=myRotate(np.array(p1b),90)
        p2b=myRotate(np.array(p1b),180)
        if oneSide:
            p2b[:,0]=-p2b[:,0]
        contacts.insertElement(Polygon(p1a),layer=self.padLayer)
        contacts.insertElement(Polygon(p1b),layer=self.gateLayer)
        ## HERE THE NEW STUFF IS DONE
        return W,D,p,ps,wp,length,angle,contacts


class Dots2Pt(Simple2Pt):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "radius":0.15,


        "number":1,
        "vertDistance":2.,
        "radDistance":0.2,
        "layerDots":self.descriptor.defExposureLayer+1
        })
        super(Dots2Pt,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def make(self):
        W,D,p,ps,wp,length,angle,contacts=super(Dots2Pt,self).make()
        number=int(self.number)
        zero1=np.array([-self.radDistance/2.,-self.vertDistance*(number-1)/2.])
        zero2=np.array([self.radDistance/2.,-self.vertDistance*(number-1)/2.])
        for i in range(number):
            p1=zero1+np.array([0.,self.vertDistance*i])
            contacts.insertElement(Circle(self.radius/2.),xy=p1,layer=self.layerDots)
            p2=zero2+np.array([0.,self.vertDistance*i])
            contacts.insertElement(Circle(self.radius/2.),xy=p2,layer=self.layerDots)
        
    def getDefLayers(self):
        return super(Dots2Pt,self).getDefLayers().union(set([self.layerDots]))


class Dots4Pt(Simple4Pt):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "radius":0.2,
        "number":5,

        "vertDistance":1.13,
        "partDistance":0.2,
        "layerDots":self.descriptor.defExposureLayer+1
        })
        super(Dots4Pt,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def make(self):
        W,D,p,ps,wp,length,angle,contacts=super(Dots4Pt,self).make()
        number=int(self.number)
      	antennaDist= self.partDistance + self.radius
        zero1=np.array([-antennaDist/2.,-self.vertDistance*(number-1)/2.])
        zero2=np.array([antennaDist/2.,-self.vertDistance*(number-1)/2.])
        for i in range(number):
            p1=zero1+np.array([0.,self.vertDistance*i])
            contacts.insertElement(Circle(self.radius/2.),xy=p1,layer=self.layerDots)
            p2=zero2+np.array([0.,self.vertDistance*i])
            contacts.insertElement(Circle(self.radius/2.),xy=p2,layer=self.layerDots)
            
    def getDefLayers(self):
        return super(Dots4Pt,self).getDefLayers().union(set([self.layerDots]))
		
		
class Triangol4Pt(Simple4Pt):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "lates":0.2,
        "number":5,
        "vertDistance":1.13,
        "antDistance":0.2,
        "layerTriangols":self.descriptor.defExposureLayer+1
        })
        super(Triangol4Pt,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def make(self):
        W,D,p,ps,wp,length,angle,contacts=super(Triangol4Pt,self).make()
        number=int(self.number)
      	antennaDist= -self.antDistance
        zero1=np.array([-antennaDist/2.,-self.vertDistance*(number-1)/2.])
        zero2=np.array([antennaDist/2.,-self.vertDistance*(number-1)/2.])
        for i in range(number):
            p1=zero1+np.array([0.,self.vertDistance*i])
            t1=[[p1[0],p1[1]],[p1[0]+self.lates*np.sqrt(3)/2,p1[1]-self.lates/2],[p1[0]+self.lates*np.sqrt(3)/2,p1[1]+self.lates/2]]
            tri1=myRotate(np.array(t1),180)
            contacts.insertElement(Polygon(tri1),layer=self.layerTriangols)
            p2=zero2+np.array([0.,self.vertDistance*i])
            t2=[[p2[0],p2[1]],[p2[0]-self.lates*np.sqrt(3)/2,p2[1]-self.lates/2],[p2[0]-self.lates*np.sqrt(3)/2,p2[1]+self.lates/2]]
            tri2=myRotate(np.array(t2),180)
            contacts.insertElement(Polygon(tri2),layer=self.layerTriangols)
            
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        l=length-2.*self.gap-2.*self.overlap-self.width2
        t=self.name.split("_")[0]+"-%.3fum"%self.antDistance
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.padLayer,xy=[0,(self.padSpacing/2.+self.pad+self.textSpacing)])
        
			
    def getDefLayers(self):
        return super(Triangol4Pt,self).getDefLayers().union(set([self.layerTriangols]))
     
class OneSided4Pt(NanoWireTemplate): 
    def __init__(self,name,descriptor=None,**kwargs):     
        self.descriptor=descriptor      
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "padSpacing":100.,
        "pad":150.,
        "width":1.,
        "intLength":5.,
        "widthAtPad":10.,
        "overlap":1.,
        "textSpacing":20.,
        })
        super(OneSided4Pt,self).__init__(name,descriptor=descriptor,**kwargs)
    
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        W=self.width
        D=length/2.-self.overlap
        ps=self.padSpacing
        p=self.pad
        wp=self.widthAtPad
        iL=self.intLength
        p1=[[wp/2.,ps/2.],[W/2.,D+iL],[W/2.,D],[-W/2.,D],[-W/2.,D+iL],[-wp/2.,ps/2.],
            [-p/2.,ps/2.],[-p/2.,ps/2.+p],[p/2.,ps/2.+p],[p/2.,ps/2.]]
        p2=myRotate(np.array(p1),180)
        contacts=Structure(self.name+"_contacts")
        contacts.insertElement(Polygon(p1),layer=self.layer)
        contacts.insertElement(Polygon(p2),layer=self.layer)
        t=self.name.split("_")[0]
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.layer,xy=[0,(ps/2.+p+self.textSpacing)])
        self.insertElement(contacts,angle=angle,xy=center)
        
        return W,D,p,ps,wp,length,angle,contacts

class CPW_onlytap(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "stripWidth":2.,
        "gapWidth":1.092,
        "groundWidth":80.,
        "stripLength":50.,
        "contactWidth":50.,
        "contactGroundWidth":250.,
        "contactGapWidth":26.55,
        "contactLength":0.,
        "transitionLength":400.,
        "offset":0.0,
        "textHeight":50.,
        "flipped":0,
        })
        super(CPW_onlytap,self).__init__(name,descriptor=descriptor,**kwargs)
    
    def createStrip(self,contacts):
        points=[
        (-self.contactWidth/2.,self.stripLength/2.+self.transitionLength),
        (-self.stripWidth/2.,self.stripLength/2.)]
        points.extend([(i[0],i[1]*(-1))for i in points[::-1]])
        points.extend([(i[0]*(-1),i[1])for i in points[::-1]])
#        points=[(point[0],point[1]) for point in points]
        print "strip:;",points
        if self.flipped:
            a=-1.
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        else:
            a=1.
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[self.offset*a,0.])
        
    def createGround(self,contacts,xy=[0.,0.],mirrored=False):
        points=[
        (self.stripWidth/2.+self.gapWidth,self.stripLength/2.),
        (self.contactWidth/2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength),
        (self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth,self.stripLength/2.+self.transitionLength),
        (self.stripWidth/2.+self.gapWidth+self.groundWidth,self.stripLength/2.)
        ]
        points.extend([(i[0],i[1]*(-1))for i in points[::-1]])
#        points=[(point[0],point[1]) for point in points]
        if mirrored:
            points=[(point[0]*(-1.),point[1]) for point in points]
        if self.flipped:
            a=-1.
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        else:
            a=1.
#        points=points+[points[0]]
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[self.offset*a,0.])     
    
    def createText(self,contacts):
        t=self.name.split("_")[0]
        contacts.insertElement(Text(t,height=self.textHeight),layer=self.layer,xy=[self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth,0.],angle=90.)
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        contacts=Structure(self.name+"_contacts")
        self.createStrip(contacts)
        self.createGround(contacts)
        self.createGround(contacts,mirrored=True)
        self.createText(contacts)
        self.insertElement(contacts,angle=angle,xy=center)
     
class BentCPW(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "stripWidth":2.,
        "gapWidth":1.4,
        "groundWidth":20.,
        "stripLength":300.,
        "contactWidth":160.,
        "contactLength":250.,
        "contactGapWidth":87.,
        "transitionLength":300.,
        "offset":1,
        "textHeight":20.,
        "curveRadius":50.,
        "contactDistance":300.,
        "curveInterpolation":20,
        })
        super(BentCPW,self).__init__(name,descriptor=descriptor,**kwargs)
        
    #def getVectors(self,P0,P1,P2,R):
        #"""P0=intersction point"""
        #return P0,P1,P2,o1,o2,v1,v2,dv
        
            
    def getCurvePoints(self,P0,P1,P2,R,n=20):
        t0=time.time()
        P0=np.array(P0)
        P1=np.array(P1)
        P2=np.array(P2)
        o1=(P1-P0)/np.sqrt(np.dot(P1-P0,P1-P0))
        o2=(P2-P0)/np.sqrt(np.dot(P2-P0,P2-P0))
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
        circleCenter= P0+x[0]*o1+v1
        angle = np.arcsin(np.cross(v2/R,v1/R))
        points=[]
        for i in range(n+1):
            x=-i*angle/n
            rot = np.array([[np.cos(x),-np.sin(x)],
                             [np.sin(x),np.cos(x)]])
            points.append(circleCenter+np.dot(rot,-v1))
        return points
    
    def createStrip(self):
        top,bot,center,d,length,angle=self.getCoords()
        theta=abs(angle/180.*np.pi-np.pi/2.)
           
        # Contacts   
        temp=[
        (self.stripWidth/2.,self.contactDistance/2.),
        (self.contactWidth/2.,self.contactDistance/2.+self.transitionLength),
        (self.contactWidth/2.,self.contactDistance/2.+self.transitionLength+self.contactLength),
        ]
        # Top Contact   
        topContact=temp+[(p[0]*(-1.),p[1]) for p in temp[::-1]]
        topContact=[(p[0]+self.stripLength/2.*np.cos(theta)-self.stripWidth/2.*np.sin(theta),p[1]) for p in topContact]
        # Bottom Contact   
        bottomContact=[(p[0]*(-1.),p[1]*(-1.)) for p in topContact]
        
        #Edges:
        s=np.sin(theta)
        c=np.cos(theta)
        t=np.tan(theta)
        par1=self.stripWidth/2.
        par2=-self.stripWidth/2.
        yU0=c*par1+t*(topContact[-1][0]+s*par1)
        yU1=c*par1+t*(bottomContact[0][0]+s*par1)
        yU2=c*par2+t*(bottomContact[-1][0]+s*par2)
        yU3=c*par2+t*(topContact[0][0]+s*par2)
        edgePoints=[(topContact[-1][0],yU0),(bottomContact[0][0],yU1),(bottomContact[-1][0],yU2),(topContact[0][0],yU3)]
        
        #Curves
        curve1=self.getCurvePoints(edgePoints[0],topContact[-1],edgePoints[1],self.curveRadius,n=self.curveInterpolation)
        curve2=self.getCurvePoints(edgePoints[1],edgePoints[0],bottomContact[0],self.curveRadius+self.stripWidth,n=self.curveInterpolation)
        curve3=self.getCurvePoints(edgePoints[2],bottomContact[-1],edgePoints[3],self.curveRadius,n=self.curveInterpolation)
        curve4=self.getCurvePoints(edgePoints[3],edgePoints[2],topContact[0],self.curveRadius+self.stripWidth,n=self.curveInterpolation)
		#MiddelTop
        middleTop=curve1+curve2
        middleBottom=curve3+curve4
                
        points=topContact+middleTop+bottomContact+middleBottom
        
        offset=(-s*(self.offset+self.stripWidth/2.),c*(self.offset+self.stripWidth/2.))
        points=[(p[0]-offset[0],p[1]-offset[1]) for p in points]
        if top[0]>=center[0]:
            pass
        else:
            points=[(p[0]*(-1.),p[1]) for p in points]
        points=[(p[0]+center[0],p[1]+center[1]) for p in points]
        self.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.])
        
    def createGround(self,xy=[0.,0.],mirrored=False):            
            
        top,bot,center,d,length,angle=self.getCoords()
        theta=abs(angle/180.*np.pi-np.pi/2.)
           
        # Contacts      
        temp=[
        (self.stripWidth/2.+self.gapWidth+self.groundWidth,self.contactDistance/2.),
        (self.contactWidth*3./2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength),
        (self.contactWidth*3./2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength+self.contactLength),
        (self.contactWidth*3./2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength+self.contactLength),
        (self.contactWidth/2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength+self.contactLength),
        (self.contactWidth/2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength),
        (self.stripWidth/2.+self.gapWidth,self.contactDistance/2.),
        ]
        # Top Contact   
        topContact=[(p[0]+self.stripLength/2.*np.cos(theta)-self.stripWidth/2.*np.sin(theta),p[1]) for p in temp]
        # Bottom Contact   
        bottomContact=[(p[0]-(self.stripLength/2.*np.cos(theta)-self.stripWidth/2.*np.sin(theta)),p[1]*(-1.)) for p in temp[::-1]]
              
        #Edges:
        s=np.sin(theta)
        c=np.cos(theta)
        t=np.tan(theta)
        delta=-self.groundWidth/2.-self.gapWidth-self.stripWidth/2
        par1=self.groundWidth/2+delta
        par2=-self.groundWidth/2+delta
        yU0=c*par1+t*(topContact[-1][0]+s*par1)
        yU1=c*par1+t*(bottomContact[0][0]+s*par1)
        yU2=c*par2+t*(bottomContact[-1][0]+s*par2)
        yU3=c*par2+t*(topContact[0][0]+s*par2)
        edgePoints=[(topContact[-1][0],yU0),(bottomContact[0][0],yU1),(bottomContact[-1][0],yU2),(topContact[0][0],yU3)]
        
       
        #Curves
        curveRadius1=self.curveRadius+self.stripWidth+self.gapWidth
        curveRadius2=self.curveRadius-self.gapWidth
        curve1=self.getCurvePoints(edgePoints[0],topContact[-1],edgePoints[1],curveRadius1,n=self.curveInterpolation)
        curve2=self.getCurvePoints(edgePoints[1],edgePoints[0],bottomContact[0],curveRadius2,n=self.curveInterpolation)
        curve3=self.getCurvePoints(edgePoints[2],bottomContact[-1],edgePoints[3],curveRadius2-self.groundWidth,n=self.curveInterpolation)
        curve4=self.getCurvePoints(edgePoints[3],edgePoints[2],topContact[0],curveRadius1+self.groundWidth,n=self.curveInterpolation)
		#MiddelTop
        middleTop=curve1+curve2
        middleBottom=curve3+curve4
                
        points=topContact+middleTop+bottomContact+middleBottom
        
        if mirrored:
            s180=np.sin(np.pi)
            c180=np.cos(np.pi)
            points=[(c180*p[0]-s180*p[1],s180*p[0]+c180*p[1])for p in points]
        offset=(-s*(self.offset+self.stripWidth/2.),c*(self.offset+self.stripWidth/2.))
        points=[(p[0]-offset[0],p[1]-offset[1]) for p in points]
        
        if top[0]>=center[0]:
            pass
        else:
            points=[(p[0]*(-1.),p[1]) for p in points]
        points=[(p[0]+center[0],p[1]+center[1]) for p in points]
        
        self.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.])
    
    def createText(self):
        top,bot,center,d,length,angle=self.getCoords()
        t=self.name.split("_")[0]
        self.insertElement(Text(t,height=self.textHeight),layer=self.layer,xy=[0.,self.stripLength/2.+self.transitionLength+self.contactLength*1.5],angle=90.)
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        self.createStrip()
        self.createGround()
        self.createGround(mirrored=True)
        self.createText()
        
          
        
        
               
class BentCPWContact(BentCPW):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "padSize":150.,
        "padGap":150.,
        "padDistance":100.,
        "widthAtPad":25.,
        "widthAtInt":10.,
        "widthAtMid":15.,
        "intRadius":5.,
        "padRadius":25.,
        "midRadius":15,
        "midDistance":60.,
        "intDistance":10.,
        "width":0.5,
        "intLength":25.,
        "tipDist":0.5,
        "overlap":0.3,
        "contactDist":1.,
        })
        super(BentCPWContact,self).__init__(name,descriptor=descriptor,**kwargs)
    
    def createContact(self):
        
        top,bot,center,d,length,angle=self.getCoords()
        theta=abs(angle/180.*np.pi-np.pi/2.)
        s=np.sin(theta)
        c=np.cos(theta)
        t=np.tan(theta)
           
        # Contacts      
        contactBase=self.getCurvePoints((0.,self.padSize/2.-self.widthAtPad),(self.widthAtPad,self.padSize/2.-self.widthAtPad),(0.,self.padSize/2.-self.widthAtPad*2.),self.padRadius)+\
                    [(0.,-self.padSize/2.),(-self.padSize,-self.padSize/2.),(-self.padSize,self.padSize/2.),
                     (0.,self.padSize/2.),(self.widthAtPad,self.padSize/2.)]
        
        for i in range(4):                               
            if i in [0,1]:
                a=1.
            else:
                a=-1.
            
            if i in [0,3]:
                m=1.
            else:
                m=0.
                
            
            vec=np.array([-s,c])
            w=np.array([c*self.width/2.,s*self.width/2.])
            o=np.array([-s*self.overlap,c*self.overlap])
            edge=np.array([-(self.contactWidth*3./2.+self.contactGapWidth+self.stripLength/2.*np.cos(theta)-self.stripWidth/2.*np.sin(theta)),0.])
            
            x0=vec*(self.intLength+np.array([0.,self.intDistance])*1.5)+center
            #position /mirror pad
            points =[(p[0]+x0[0]-self.padDistance+edge[0],p[1]*a+x0[1]-self.padGap*3./2.-self.padSize*3./2.+i*(self.padSize+self.padGap)) for p in contactBase]

            if i in [0,1,2,3]:
                if i in [0,1]:
                    dist=np.array([c,s])*(i*self.contactDist+self.tipDist)
                else:
                    dist=np.array([c,s])*(length-np.mod(i+1,2)*self.contactDist-self.tipDist)
                  
                ptemp1=[
                        points[-1],
                        points[-1]+np.array([self.padDistance+m*(self.midDistance+self.widthAtPad),0.]),
                        (points[-1][0]+self.padDistance+m*(self.midDistance+self.widthAtPad),x0[1]-a*self.intDistance-a*m*(self.widthAtMid+self.midDistance)),
                        bot+vec*(self.intLength+self.intDistance*i)+dist+a*w+a*vec*self.width,
                        bot+dist+a*w-o
                        ]
                ptemp2=[
                        bot+dist-a*w-o,
                        bot+vec*(self.intLength+self.intDistance*i)+dist-a*w,
                        (points[-1][0]+self.widthAtMid+self.padDistance+m*(self.midDistance+self.widthAtPad),x0[1]-a*self.intDistance-a*self.widthAtMid-a*m*(self.widthAtMid+self.midDistance)),
                        points[0]+np.array([self.padDistance+self.widthAtMid+m*(self.midDistance+self.widthAtPad),0.]),
                        points[0],
                        ]
                        
                contWire=   self.getCurvePoints(ptemp1[1],ptemp1[0],ptemp1[2],self.padRadius)+\
                            self.getCurvePoints(ptemp1[2],ptemp1[1],ptemp1[3],self.midRadius+self.widthAtInt)+\
                            self.getCurvePoints(ptemp1[3],ptemp1[2],ptemp1[4],self.intRadius)+\
                            [ptemp1[4],ptemp2[0]]+\
                            self.getCurvePoints(ptemp2[1],ptemp2[0],ptemp2[2],self.intRadius+self.width)+\
                            self.getCurvePoints(ptemp2[2],ptemp2[1],ptemp2[3],self.midRadius)+\
                            self.getCurvePoints(ptemp2[3],ptemp2[2],ptemp2[4],self.padRadius+self.widthAtPad)
                            
            
                
                points.extend(contWire)
            
                
            if top[0]>=center[0]:
                pass
            else:
                points=[(p[0]*(-1.),p[1]) for p in points]
                points=[(p[0]+2*bot[0],p[1]) for p in points]
                
            self.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.])
        
         
    def createDummyPad(self,xy=[0.,0.],mirrored=False):        
            
        top,bot,center,d,length,angle=self.getCoords()
        theta=abs(angle/180.*np.pi-np.pi/2.)
        s=np.sin(theta)
        c=np.cos(theta)
        t=np.tan(theta)
           
        # Contacts      
        temp=[
        #(self.stripWidth/2.+self.gapWidth+self.groundWidth,self.contactDistance/2.),
        (self.contactWidth*3./2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength),
        (self.contactWidth*3./2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength+self.contactLength),
        (self.contactWidth*3./2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength+self.contactLength),
        (self.contactWidth/2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength+self.contactLength),
        (self.contactWidth/2.+self.contactGapWidth,self.contactDistance/2.+self.transitionLength),
        #(self.stripWidth/2.+self.gapWidth,self.contactDistance/2.),
        ]
        # Top Contact   
        topContact=[(p[0]+self.stripLength/2.*np.cos(theta)-self.stripWidth/2.*np.sin(theta),p[1]) for p in temp]
        
        points=topContact
        if mirrored:
            s180=np.sin(np.pi)
            c180=np.cos(np.pi)
            points=[(c180*p[0]-s180*p[1],s180*p[0]+c180*p[1])for p in points]
        else:
            points=[(p[0]-(self.contactWidth*2.+self.contactGapWidth*2.),p[1])for p in points]
        offset=(-s*self.offset,c*self.offset)
        points=[(p[0]+offset[0],p[1]+offset[1]) for p in points]
        
        if top[0]>=center[0]:
            pass
        else:
            points=[(p[0]*(-1.),p[1]) for p in points]
        points=[(p[0]+center[0],p[1]+center[1]) for p in points]
        
        self.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.])
    
    
    def createText(self):
        top,bot,center,d,length,angle=self.getCoords()
        l=length-3.*self.width-2.*self.tipDist-2.*self.contactDist
        t=self.name.split("_")[0]+" L:"+"%.2f"%l
        self.insertElement(Text(t,height=self.textHeight),layer=self.layer,xy=[0.,-(self.stripLength/2.+self.transitionLength+self.contactLength*1.5)])
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        self.createStrip()
        self.createGround()
        self.createDummyPad(mirrored=False)
        self.createDummyPad(mirrored=True)
        self.createContact()
        self.createText()
        
        
class CPWShort(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        self.updateDefaultValue("stripWidth",160.)
        self.updateDefaultValue("gapWidth",87.)
        self.updateDefaultValue("groundWidth",160.)
        self.updateDefaultValue("length",500.)
        self.updateDefaultValue("shortWidth",50.)
        self.updateDefaultValue("offset",0.7)
        self.updateDefaultValue("textHeight",50.)
        self.updateDefaultValue("flipped",False)
        super(CPWShort,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def createCPW(self,contacts):
        length=self.length
        strip=self.stripWidth
        short=self.shortWidth
        gap=self.gapWidth
        ground=self.groundWidth
        points=[
            [+length+short,     strip/2.],
            [+short,            strip/2.],
            [+short,            strip/2.+gap],
            [+length+short,     strip/2.+gap],
            [+length+short,     strip/2.+gap+ground],
            [0.,                strip/2.+gap+ground],
        ]
        points=points+[[point[0],-point[1]] for point in points[::-1]]
        contacts.insertElement(Polygon(points),layer=self.layer,
                               xy=[+self.offset,strip/2.+gap/2.])
        
        
    def createText(self,contacts):
        t=self.name.split("_")[0]
        contacts.insertElement(Text(t,height=self.textHeight),
                               layer=self.layer,
                               xy=[self.length+self.shortWidth+self.textHeight*2.,
                                   0.],angle=-90.)
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        contacts=Structure(self.name+"_contacts")
        self.createCPW(contacts)
        self.createText(contacts)
        self.insertElement(contacts,angle=angle,xy=center)

      
class CPWShortContact(CPWShort):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        self.updateDefaultValue("offset",2.)
        self.updateDefaultValue("padSize",200.)
        self.updateDefaultValue("padGap",100.)
        self.updateDefaultValue("padDistance",500.)
        self.updateDefaultValue("intLength",5.)
        self.updateDefaultValue("widthAtPad",20.)
        self.updateDefaultValue("width",0.5)
        self.updateDefaultValue("widthAtEnd",0.5)
        self.updateDefaultValue("tipDist",0.5)
        self.updateDefaultValue("overlap",0.2)
        self.updateDefaultValue("contactDist",0.5)
        self.updateDefaultValue("textDist",500.)
        self.updateDefaultValue("makeGuide",False)        
        self.updateDefaultValue("guideWidth",20.)      
        self.updateDefaultValue("guideLength",200.)    
        self.updateDefaultValue("guideDist",1000.) 
        self.updateDefaultValue("contactLayer",1)
        self.updateDefaultValue("equiDist",True)
        self.updateDefaultValue("midCont",True)
        super(CPWShortContact,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def getDefLayers(self):
        return super(CPWShortContact,self).getDefLayers().union(set([self.contactLayer]))
        
    
    def createGuide(self,contacts):
        w=self.guideWidth
        l=self.guideLength
        d=self.guideDist
        points=np.array([[w/2.,d],[w/2.,d+l],[-w/2.,d+l],[-w/2.,d]])
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.],angle=90.)
        contacts.insertElement(Polygon(points*np.array([1.,-1.])),layer=self.layer,xy=[0.,0.],angle=90.)
        points=np.array(points)+np.array([0.,d])
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.],angle=90.)
        contacts.insertElement(Polygon(points*np.array([1.,-1.])),layer=self.layer,xy=[0.,0.],angle=90.)
        
    def createMiddleContact(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        
        points=[
        (-self.padDistance,                      self.padSize*0.5),
        (-self.padDistance-self.padSize,         self.padSize*0.5),
        (-self.padDistance-self.padSize,        -self.padSize*0.5),
        (-self.padDistance,                     -self.padSize*0.5),
        (-self.padDistance,                     -self.widthAtPad/2.),
        (self.overlap-self.intLength-self.width,-self.width/2.),
        (self.overlap,                          -self.width/2.),
        (self.overlap,                           self.width/2.),
        (self.overlap-self.intLength-self.width, self.width/2.),
        (-self.padDistance,                      self.widthAtPad/2.),
        ]
        if self.flipped:
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.contactLayer,xy=[0.,0.])
        
    def createContact(self,contacts,no=0):
        top,bot,center,d,length,angle=self.getCoords()
                    
        if self.midCont:
            x=0.5
        else:
            x=0.
        if no in [0,3]:
            a=1.5+x
            b=2.+x
            c=1.+x
            d=0.
            e=0.
            cw=self.widthAtEnd
        elif no in [1,2]:
            a=0.5+x
            b=1.+x
            c=0.+x
            d=self.contactDist+self.widthAtEnd
            e=self.widthAtEnd
            cw=self.width
            
        if self.equiDist and no in [1,2] and self.midCont:
            dy=(length/2.-self.tipDist)/2.
        elif self.equiDist and no in [1,2]:
            dy=(length/2.-self.tipDist)/3.
        else:
            dy=length/2.-self.tipDist-d
        
        points=[
        (-self.padDistance,                 self.padGap*a+self.padSize*b),
        (-self.padDistance-self.padSize,    self.padGap*a+self.padSize*b),
        (-self.padDistance-self.padSize,    self.padGap*a+self.padSize*c),
        (-self.padDistance,                 self.padGap*a+self.padSize*c),
        (self.overlap-self.intLength-cw-e,  dy-cw/2.),
        (self.overlap,                      dy-cw/2.),
        (self.overlap,                      dy+cw/2.),
        (self.overlap-self.intLength-e,     dy+cw/2.),
        (-self.padDistance,                 self.padGap*a+self.padSize*c+self.widthAtPad*b-d),
        ]
        if no in [2,3]:
            points=[(point[0],point[1]*(-1.)) for point in points]
        if self.flipped:
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.contactLayer,xy=[0.,0.])
         
    def createDummyPad(self,contacts,xy=[0.,0.],mirrored=False):
        points=[
        (self.contactWidth/2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength),
        (self.contactWidth/2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength+self.contactLength),
        (self.contactWidth*3./2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength+self.contactLength),
        (self.contactWidth*3./2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength),
        ]
        if mirrored:
            points=[(point[0]*(-1.),point[1]) for point in points]
        points2=[(point[0]+self.stripWidth/2.,point[1]) for point in points]
        contacts.insertElement(Polygon(points2),layer=self.layer,xy=[self.offset,0.])  
        points=[(point[0]+self.stripWidth/2.,point[1]*(-1.)) for point in points]
        if self.flipped:
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[self.offset,0.])      
    
    def createContacts(self,contacts):
        for i in range(4):
            self.createContact(contacts,i)
    
    
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        if self.equiDist:
            t=self.name.split("_")[0]
        else:
            t=self.name.split("_")[0]
        if self.flipped:
            a=-1.
        else:
            a=1.
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),
                               layer=self.layer,
                               xy=[self.length+self.shortWidth+self.textHeight*2.,
                                   0.],angle=-90.)
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        contacts=Structure(self.name+"_contacts")
        self.createCPW(contacts)
        self.createContacts(contacts)
        if self.midCont:
            self.createMiddleContact(contacts)
        self.createText(contacts)
        if self.makeGuide:
            self.createGuide(contacts)
        self.insertElement(contacts,angle=angle,xy=center)
            
    
class CPW(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        self.updateDefaultValue("stripWidth",2.)
        self.updateDefaultValue("gapWidth",1.1)
        self.updateDefaultValue("groundWidth",20.)
        self.updateDefaultValue("stripLength",50.)
        self.updateDefaultValue("contactWidth",160.)
        self.updateDefaultValue("contactGroundWidth",160.)
        self.updateDefaultValue("contactGapWidth",87.)
        self.updateDefaultValue("contactLength",50.)
        self.updateDefaultValue("transitionLength",400.)
        self.updateDefaultValue("offset",0.0)
        self.updateDefaultValue("textHeight",50.)
        self.updateDefaultValue("flipped",False)
        self.updateDefaultValue("GNDLayer",0)
        self.updateDefaultValue("etchContacts",True)
        self.updateDefaultValue("etchNegative",True)
        self.updateDefaultValue("etchLength",100.)
        self.updateDefaultValue("etchLayer",1)
        super(CPW,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def getDefLayers(self):
        if self.etchContacts:
            l=[self.GNDLayer,self.etchLayer]
        else:
            l=[self.GNDLayer]
        return super(CPW,self).getDefLayers().union(set(l))
    
    def createStrip(self,contacts):
        points=[
        (-self.contactWidth/2.,self.stripLength/2.+self.transitionLength+self.contactLength),
        (-self.contactWidth/2.,self.stripLength/2.+self.transitionLength),
        (-self.stripWidth/2.,self.stripLength/2.)]
        points.extend([(i[0],i[1]*(-1))for i in points[::-1]])
        points.extend([(i[0]*(-1),i[1])for i in points[::-1]])
        if self.flipped:
            a=-1.
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        else:
            a=1.
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[self.offset*a,0.])
        
    def createGround(self,contacts,xy=[0.,0.],mirrored=False):
        points=[
        (self.stripWidth/2.+self.gapWidth,
             self.stripLength/2.),
        (self.contactWidth/2.+self.contactGapWidth,
             self.stripLength/2.+self.transitionLength),
        (self.contactWidth/2.+self.contactGapWidth,
             self.stripLength/2.+self.transitionLength+self.contactLength),
        (self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth,
             self.stripLength/2.+self.transitionLength+self.contactLength),
        (self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth,
             self.stripLength/2.+self.transitionLength),
        (self.stripWidth/2.+self.gapWidth+self.groundWidth,
             self.stripLength/2.)
        ]
        points.extend([(i[0],i[1]*(-1))for i in points[::-1]])
        if mirrored:
            points=[(point[0]*(-1.),point[1]) for point in points]
        if self.flipped:
            a=-1.
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        else:
            a=1.
        contacts.insertElement(Polygon(points),layer=self.GNDLayer,xy=[self.offset*a,0.])     
    
    def createContRectGround(self,contacts,mirrored=False):
        if self.etchLength>self.contactLength:
            dif=0
        else:
            dif=self.contactLength-self.etchLength
        points=[
            (self.contactWidth/2.+self.contactGapWidth,
                 self.stripLength/2.+self.transitionLength+dif),
            (self.contactWidth/2.+self.contactGapWidth,
                 self.stripLength/2.+self.transitionLength+self.contactLength),
            (self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth,
                 self.stripLength/2.+self.transitionLength+self.contactLength),
            (self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth,
                 self.stripLength/2.+self.transitionLength+dif)
        ]
        if self.etchLength>self.contactLength:
            dx1=(self.contactWidth/2.+self.contactGapWidth)-\
                (self.stripWidth/2.+self.gapWidth)
            dx2=(self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth)-\
                (self.stripWidth/2.+self.gapWidth+self.groundWidth)
            dy=self.transitionLength
            el=self.etchLength-self.contactLength
            x1=self.contactWidth/2.+self.contactGapWidth-\
                dx1/dy*el
            x2=self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth-\
                dx2/dy*el
            y=self.stripLength/2.+self.transitionLength+self.contactLength-\
                self.etchLength
            points=points+[(x2,y),(x1,y)]
        if mirrored:
            points=[(point[0]*(-1.),point[1]) for point in points]
        if self.flipped:
            a=-1.
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        else:
            a=1.
        contacts.insertElement(Polygon(points),layer=self.etchLayer,xy=[self.offset*a,0.]) 
        points=[(point[0],point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.etchLayer,xy=[self.offset*a,0.]) 
        
        
    def createContRectStrip(self,contacts):
        if self.etchLength>self.contactLength:
            dif=0
        else:
            dif=self.contactLength-self.etchLength
            
        points=[
                (self.contactWidth/2.,self.stripLength/2.+self.transitionLength+self.contactLength),
                (self.contactWidth/2.,self.stripLength/2.+self.transitionLength+dif),
               ]
        if self.etchLength>self.contactLength:
            dx=self.contactWidth/2.-self.stripWidth/2.
            dy=self.transitionLength
            el=self.etchLength-self.contactLength
            x=self.contactWidth/2.-dx/dy*el
            y=self.stripLength/2.+self.transitionLength+self.contactLength-self.etchLength
            points=points+[(x,y)]
            
        points=points+[(point[0]*(-1.),point[1]) for point in points[::-1]]
        contacts.insertElement(Polygon(points),layer=self.etchLayer,xy=[self.offset,0.]) 
        points=[(point[0],point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.etchLayer,xy=[self.offset,0.]) 
        
    def createInvEtch(self,contacts):
        point= (self.etchLength/2.,self.etchLength/2.)
        points=[
            point,
            (point[0]*(-1.),point[1]),
            (point[0]*(-1.),point[1]*(-1)),
            (point[0],point[1]*(-1)),
        ]
        contacts.insertElement(Polygon(points),layer=self.etchLayer,xy=[self.offset,0.]) 
    
    def createText(self,contacts):
        t=self.name.split("_")[0]
        contacts.insertElement(Text(t,height=self.textHeight),
                               layer=self.layer,
                               xy=[self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth,0.],
                               angle=90.)
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        contacts=Structure(self.name+"_contacts")
        self.createStrip(contacts)
        self.createGround(contacts)
        self.createGround(contacts,mirrored=True)
        self.createText(contacts)
        if self.etchContacts:
            if self.etchNegative:
                self.createInvEtch(contacts)
            else:
                self.createContRectGround(contacts)
                self.createContRectGround(contacts,mirrored=True)
                self.createContRectStrip(contacts)
        self.insertElement(contacts,angle=angle,xy=center)
       
 
        
               
class CPWContact(CPW):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        self.updateDefaultValue("offset",2.)
        self.updateDefaultValue("padSize",200.)
        self.updateDefaultValue("padGap",100.)
        self.updateDefaultValue("padDistance",500.)
        self.updateDefaultValue("intLength",5.)
        self.updateDefaultValue("widthAtPad",20.)
        self.updateDefaultValue("width",0.5)
        self.updateDefaultValue("widthAtEnd",0.5)
        self.updateDefaultValue("tipDist",0.5)
        self.updateDefaultValue("overlap",0.2)
        self.updateDefaultValue("contactDist",0.5)
        self.updateDefaultValue("textDist",500.)
        self.updateDefaultValue("makeGuide",True)        
        self.updateDefaultValue("guideWidth",20.)      
        self.updateDefaultValue("guideLength",200.)    
        self.updateDefaultValue("guideDist",1000.) 
        self.updateDefaultValue("contactLayer",1)
        self.updateDefaultValue("equiDist",True)
        self.updateDefaultValue("midCont",True)
        self.updateDefaultValue("sec",False)
        super(CPWContact,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def getDefLayers(self):
        return super(CPWContact,self).getDefLayers().union(set([self.contactLayer]))
        
    
    def createGuide(self,contacts):
        w=self.guideWidth
        l=self.guideLength
        d=self.guideDist
        points=np.array([[w/2.,d],[w/2.,d+l],[-w/2.,d+l],[-w/2.,d]])
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.])
        contacts.insertElement(Polygon(points*np.array([1.,-1.])),layer=self.layer,xy=[0.,0.])
        points=np.array(points)+np.array([0.,d])
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.])
        contacts.insertElement(Polygon(points*np.array([1.,-1.])),layer=self.layer,xy=[0.,0.])
        
    def createMiddleContact(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        
        points=[
        (-self.padDistance,                      self.padSize*0.5),
        (-self.padDistance-self.padSize,         self.padSize*0.5),
        (-self.padDistance-self.padSize,        -self.padSize*0.5),
        (-self.padDistance,                     -self.padSize*0.5),
        (-self.padDistance,                     -self.widthAtPad/2.),
        (self.overlap-self.intLength-self.width,-self.width/2.),
        (self.overlap,                          -self.width/2.),
        (self.overlap,                           self.width/2.),
        (self.overlap-self.intLength-self.width, self.width/2.),
        (-self.padDistance,                      self.widthAtPad/2.),
        ]
        if self.flipped:
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.contactLayer,xy=[0.,0.])
        
    def createContact(self,contacts,no=0):
        top,bot,center,d,length,angle=self.getCoords()
                    
        if self.midCont:
            x=0.5
        else:
            x=0.
        if no in [0,3]:
            a=1.5+x
            b=2.+x
            c=1.+x
            d=0.
            e=0.
            cw=self.widthAtEnd
        elif no in [1,2]:
            a=0.5+x
            b=1.+x
            c=0.+x
            d=self.contactDist+self.widthAtEnd
            e=self.widthAtEnd
            cw=self.width
            
        if self.equiDist and no in [1,2] and self.midCont:
            dy=(length/2.-self.tipDist)/2.0
        elif self.equiDist and no in [1,2]:
            dy=(length/2.-self.tipDist)/3.
        else:
            dy=length/2.-self.tipDist-d
        
        points=[
        (-self.padDistance,                 self.padGap*a+self.padSize*b),
        (-self.padDistance-self.padSize,    self.padGap*a+self.padSize*b),
        (-self.padDistance-self.padSize,    self.padGap*a+self.padSize*c),
        (-self.padDistance,                 self.padGap*a+self.padSize*c),
        (self.overlap-self.intLength-cw-e,  dy-cw/2.),
        (self.overlap,                      dy-cw/2.),
        (self.overlap,                      dy+cw/2.),
        (self.overlap-self.intLength-e,     dy+cw/2.),
        (-self.padDistance,                 self.padGap*a+self.padSize*c+self.widthAtPad*b-d),
        ]
        if no in [2,3]:
            points=[(point[0],point[1]*(-1.)) for point in points]
        if self.flipped:
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.contactLayer,xy=[0.,0.])
         
         
    def createSec(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        points=[
            (self.overlap,length/2.+self.overlap),
            (-self.overlap,length/2.+self.overlap),
            (-self.overlap,length/2.-self.overlap-self.width),
            (self.overlap,length/2.-self.overlap-self.width),
        ]
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.])
        points=[(point[0],point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[0.,0.])
         

    def createDummyPad(self,contacts,xy=[0.,0.],mirrored=False):
        points=[
        (self.contactWidth/2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength),
        (self.contactWidth/2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength+self.contactLength),
        (self.contactWidth*3./2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength+self.contactLength),
        (self.contactWidth*3./2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength),
        ]
        if mirrored:
            points=[(point[0]*(-1.),point[1]) for point in points]
        points2=[(point[0]+self.stripWidth/2.,point[1]) for point in points]
        contacts.insertElement(Polygon(points2),layer=self.layer,xy=[self.offset,0.])  
        points=[(point[0]+self.stripWidth/2.,point[1]*(-1.)) for point in points]
        if self.flipped:
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[self.offset,0.])      
    
    def createContacts(self,contacts):
        for i in range(4):
            self.createContact(contacts,i)
    
    
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        if self.equiDist:
            t=self.name.split("_")[0]
        else:
            t=self.name.split("_")[0]
        if self.flipped:
            a=-1.
        else:
            a=1.
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.layer,xy=[self.textDist*a,0],angle=90.)
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        contacts=Structure(self.name+"_contacts")
        self.createStrip(contacts)
        self.createGround(contacts,mirrored=False)
        self.createDummyPad(contacts,mirrored=True)
        self.createContacts(contacts)
        if self.midCont:
            self.createMiddleContact(contacts)
        self.createText(contacts)
        if self.makeGuide:
            self.createGuide(contacts)
        if self.sec:
            self.createSec(contacts)
        self.insertElement(contacts,angle=angle,xy=center)
        
        
class invertedCPW(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given   
        try:
            self.kwargs
        except:
            self.kwargs={}
        self.kwargs.update({
        "stripWidth":2.,
        "gapWidth":1.1,
        "groundWidth":35.,
        "stripLength":50.,
        "freeDist":200.,
        "contactWidth":50.,
        "contactGroundWidth":860.,
        "contactGapWidth":26.5,
        "contactLength":10.,
        "transitionLength":400.,
        "offset":0.0,
        "textHeight":50.,
        "GapLayer":0,
        })
        super(invertedCPW,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def getDefLayers(self):
        return super(invertedCPW,self).getDefLayers().union(set([self.GapLayer]))
    
    def createGap(self,contacts,mirrored=False):
        points=[
        (self.stripWidth/2.+self.gapWidth,self.stripLength/2.),
        (self.contactWidth/2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength),
        (self.contactWidth/2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength+self.contactLength),
#        (self.contactWidth/2.+self.contactGapWidth,self.stripLength/2.+self.transitionLength+self.contactLength+self.freeDist),
#        (self.contactWidth/2.,self.stripLength/2.+self.transitionLength+self.contactLength+self.freeDist),
        (self.contactWidth/2.,self.stripLength/2.+self.transitionLength+self.contactLength),
        (self.contactWidth/2.,self.stripLength/2.+self.transitionLength),
        (self.stripWidth/2.,self.stripLength/2.)]
        points.extend([(i[0],i[1]*(-1))for i in points[::-1]])
        if mirrored:
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.GapLayer,xy=[self.offset,0.])
    
    def createSurround(self,contacts,mirrored=False):
        points=[
        (self.stripWidth/2.+self.gapWidth+self.groundWidth,self.stripLength/2.),
        (self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth,self.stripLength/2.+self.transitionLength),
        (self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth,self.stripLength/2.+self.transitionLength+self.contactLength),
        (0.,self.stripLength/2.+self.transitionLength+self.contactLength),
        (0.,self.stripLength/2.+self.transitionLength+self.contactLength+self.freeDist),
        (self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth+self.freeDist,self.stripLength/2.+self.transitionLength+self.contactLength+self.freeDist),
        (self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth+self.freeDist,self.stripLength/2.+self.transitionLength-self.freeDist*0.5),
        (self.stripWidth/2.+self.gapWidth+self.groundWidth+self.freeDist*2.,self.stripLength/2.),
        ]
        points.extend([(i[0],i[1]*(-1))for i in points[::-1]])
        if mirrored:
            points=[(point[0]*(-1.),point[1]*(-1.)) for point in points]
        contacts.insertElement(Polygon(points),layer=self.layer,xy=[self.offset,0.])
          
    def createText(self,contacts):
        t=self.name.split("_")[0]
        dist=self.contactWidth/2.+self.contactGapWidth+self.contactGroundWidth+self.freeDist
        contacts.insertElement(Text(t,height=self.textHeight),layer=self.layer,xy=[dist+2*self.textHeight,0.],angle=90.)
        
    def make(self):
        top,bot,center,d,length,angle=self.getCoords()
        contacts=Structure(self.name+"_contacts")
        for mirrored in [False,True]:
            self.createGap(contacts,mirrored=mirrored)
            self.createSurround(contacts,mirrored=mirrored)
        self.createText(contacts)
        self.insertElement(contacts,angle=angle,xy=center)
    
class StarkContacts(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):
        self.descriptor=descriptor    # ensures that the default is set, if no descriptor is given  
        self.updateDefaultValue("padSize",150.)  
        self.updateDefaultValue("gap",1.)  
        self.updateDefaultValue("padSpacing",300.) 
        self.updateDefaultValue("padContact",10.) 
        self.updateDefaultValue("width",1.)
        self.updateDefaultValue("length",50.)
        self.updateDefaultValue("textHeight",50.)
        self.updateDefaultValue("shift",5.)
        super(StarkContacts,self).__init__(name,descriptor=descriptor,**kwargs)
        
    def make(self):
        if self.end1[1]>self.end2[1]:
            top=np.array(self.end1)
            bot=np.array(self.end2)
        else:
            top=np.array(self.end2)
            bot=np.array(self.end1)
        center=(top+bot)/2.
        d=(top-bot)
        length=np.sqrt(np.dot(d,d))
        angle=np.mod((-np.arcsin(np.cross(d/length,[0.,1.]))*180./np.pi),180)
        space=self.padSpacing
        pad=self.padSize
        pc=self.padContact
        gap=self.gap
        w=self.width
        l=self.length
        s=self.shift/2.
        rot=rotMatrix(angle)
        gap=np.dot(rot,np.array([gap,0]))
        wp=np.dot(rot,np.array([0,w]))
        w=np.dot(rot,np.array([w,0]))
        l=np.dot(rot,np.array([0,l]))
        s=np.dot(rot,np.array([0,s]))
        p0=np.array([[space/2.+pc,space/2.],[space/2.+pad,space/2.],
             [space/2.+pad,space/2.+pad],[space/2.,space/2.+pad],[space/2.,space/2.+pc]])
        print "Center: %s"%str(center)
        if top[0]>=center[0]:
            b=-1
            ang1=0
            ang2=180
            
        else:
            b=+1
            ang1=90
            ang2=270
        print angle
        if angle<45 or (angle>90 and angle < 135):
            a=1
        else:
            a=-1
        cont1= np.dot(rotMatrix(ang1),p0.T).T
        cont2= np.dot(rotMatrix(ang2),p0.T).T
        points1=np.vstack((
                    np.array(self.getCurvePoints(center+(-gap/2.-l/2.+s)*b,
                                                 center+(-gap/2.+l/2.+s)*b,
                                                 cont1[0],
                                                 self.width)),
                    cont1,
                    np.array(self.getCurvePoints(cont1[-1],
                                                 center+(-gap/2.+l/2.+s-w)*b-wp*a*b,
                                                 center+(-gap/2.-l/2.+s-w)*b,
                                                 self.width)),
                    center+(-gap/2.-l/2.+s-w)*b,
                    center+(-gap/2.-l/2.+s)*b,
                ))
        points2=np.vstack((
                    np.array(self.getCurvePoints(center+(+gap/2.+l/2.-s)*b,
                                                 center+(+gap/2.-l/2.-s)*b,
                                                 cont2[0],
                                                 self.width)),
                    cont2,
                    np.array(self.getCurvePoints(cont2[-1],
                                                 center+(+gap/2.-l/2.-s+w)*b+wp*a*b,
                                                 center+(+gap/2.+l/2.-s)*b,
                                                 self.width)),
                    center+(+gap/2.+l/2.-s+w)*b,
                    center+(+gap/2.+l/2.-s)*b,
                ))
        self.insertElement(Polygon(points1),layer=self.layer)
        self.insertElement(Polygon(points2),layer=self.layer)
        t=self.name.split("_")[0]
        self.insertElement(Text(t,va="bottom",ha="right",height=self.textHeight),xy=np.array([space/2.+pad,space/2.+pad])*1.1,layer=self.layer,angle=180)
        return rot,p0,ang1,ang2,top,bot,b
        

        
class SimpleStark(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):     
        self.descriptor=descriptor      
        self.updateDefaultValue("padSize",150.)  
        self.updateDefaultValue("gap",1.)  
        self.updateDefaultValue("padSpacing",300.) 
        self.updateDefaultValue("padContact",10.) 
        self.updateDefaultValue("width",1.)
        self.updateDefaultValue("length",50.)
        self.updateDefaultValue("textHeight",50.)
        self.updateDefaultValue("textSpacing",50.)
        self.updateDefaultValue("shift",5.)
        super(SimpleStark,self).__init__(name,descriptor=descriptor,**kwargs)
    
    def createText(self,contacts):
        top,bot,center,d,length,angle=self.getCoords()
        t=self.name.split("_")[0]
        contacts.insertElement(Text(t,va="bottom",height=self.textHeight),layer=self.layer,xy=[0,(self.padSpacing/2.+self.padSize+self.textSpacing)])
        
        
    def make(self):
        top,bot,center,lengthvector,length,angle=self.getCoords()
        W=self.width
        D=0
        ps=self.padSpacing
        p=self.padSize
        wp=self.padContact
        g=self.gap
        l=self.length
        s=self.shift/2.
        p1a=[[wp/2.+g,ps/2.],[W/2.+g,s+l/2.],[W/2.+g,s-l/2.],[-W/2.+g,s-l/2.],[-W/2.+g,s+l/2.],[-wp/2.+g,ps/2.],
            [-p/2.,ps/2.],[-p/2.,ps/2.+p],[p/2.,ps/2.+p],[p/2.,ps/2.]]
        p2a=myRotate(np.array(p1a),180)
        contacts=Structure(self.name+"_contacts")
        contacts.insertElement(Polygon(p1a),layer=self.layer)
        contacts.insertElement(Polygon(p2a),layer=self.layer)
        self.createText(contacts)
        self.insertElement(contacts,angle=angle,xy=center)
        return W,D,p,ps,wp,length,angle,contacts
        
        
        
class Example1(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):  # this line can be copied, don't change it
        self.descriptor=descriptor                     # this line has to be copied and not changed!
        self.updateDefaultValue("triangle",1.)         # this a line defining a user parameter
        self.updateDefaultValue("radius",2.)         # this a line defining a user parameter
        super(Example1,self).__init__(name,descriptor=descriptor,**kwargs) # call the __init__ of the parent classs, copy, do not change
        
    def make(self): # copy do not change
        # coordinates / values which define the position of the wire (automatic or manual)
        top,bot,center,lengthvector,length,angle=self.getCoords() # these values can be used 
        self.end1 # or this
        self.end2 # or that
        polygonpoints=[[1.,0.],[0.,1.],[-1.,0.]] #list of points which form the polygon
        polygonarray=np.array(polygonpoints)*self.triangle                 #makes an array out of the list
        p = Polygon(polygonarray)  # now we generate a circle with radius "parameter", which can be changed by the user
        c = Circle(self.radius)
        patterns=Structure(self.name+"_patterns") # create new structure, name must be unique, do keep self.name+"..."
        self.insertElement(patterns,xy=center,angle=angle) # insert the pattern into design at center of the naonwire and rotated
        patterns.insertElement(p,xy=[0.,length/2.],layer=self.layer) # insert polygon (triangle)
        patterns.insertElement(c,xy=[0.,0.],layer=self.layer) # insert circle
        
        
        
class Example2(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):  # this line can be copied, don't change it
        self.descriptor=descriptor                     # this line has to be copied and not changed!
        self.updateDefaultValue("triangle",1.)         # this a line defining a user parameter
        self.updateDefaultValue("radius",2.)         # this a line defining a user parameter
        super(Example2,self).__init__(name,descriptor=descriptor,**kwargs) # call the __init__ of the parent classs, copy, do not change
        
    def make(self): # copy do not change
        # coordinates / values which define the position of the wire (automatic or manual)
        top,bot,center,lengthvector,length,angle=self.getCoords() # these values can be used 
        self.end1 # or this
        self.end2 # or that
        polygonpoints=[[1.,0.],[0.,1.],[-1.,0.]] #list of points which form the polygon
        polygonarray=np.array(polygonpoints)*self.triangle                 #makes an array out of the list
        p = Polygon(polygonarray)  # now we generate a circle with radius "parameter", which can be changed by the user
        c = Circle(self.radius)
        self.insertElement(p,xy=self.end1,angle=angle,layer=self.layer) # insert polygon (triangle), layer is the same as for the structure
        self.insertElement(c,xy=center,angle=angle,layer=self.layer) # insert circle, layer is the same as for the structure
        
        
        
class Example3(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):  # this line can be copied, don't change it
        self.descriptor=descriptor                     # this line has to be copied and not changed!
        self.updateDefaultValue("triangle",1.)         # this a line defining a user parameter
        self.updateDefaultValue("radius",2.)         # this a line defining a user parameter
        self.updateDefaultValue("layer2",1)         # this a line defining a user parameter
        super(Example3,self).__init__(name,descriptor=descriptor,**kwargs) # call the __init__ of the parent classs, copy, do not change
        
    # We have to tell the software which parameters have
    def getDefLayers(self): # do not change this, just copy
        newlayers=[self.layer2] # give all new layers as a list
        return super(Example3,self).getDefLayers().union(set(newlayers)) # do change first value of super to class name, otherwise copy
        
    def make(self): # copy do not change
        # coordinates / values which define the position of the wire (automatic or manual)
        top,bot,center,lengthvector,length,angle=self.getCoords() # these values can be used 
        self.end1 # or this
        self.end2 # or that
        polygonpoints=[[1.,0.],[0.,1.],[-1.,0.]] #list of points which form the polygon
        polygonarray=np.array(polygonpoints)*self.triangle                 #makes an array out of the list
        p = Polygon(polygonarray)  # now we generate a circle with radius "parameter", which can be changed by the user
        c = Circle(self.radius)
        self.insertElement(p,xy=self.end1,angle=angle,layer=self.layer) # insert polygon (triangle), layer is the same as for the structure
        self.insertElement(c,xy=center,angle=angle,layer=self.layer2) # insert circle, we choose layer2 as layer for the circle
        
        
                
class Example4(NanoWireTemplate):
    def __init__(self,name,descriptor=None,**kwargs):  # this line can be copied, don't change it
        self.descriptor=descriptor                     # this line has to be copied and not changed!
        self.updateDefaultValue("triangle",1.)         # this a line defining a user parameter
        self.updateDefaultValue("radius",2.)         # this a line defining a user parameter
        super(Example4,self).__init__(name,descriptor=descriptor,**kwargs) # call the __init__ of the parent classs, copy, do not change
        
    def make(self): # copy do not change
        # coordinates / values which define the position of the wire (automatic or manual)
        top,bot,center,lengthvector,length,angle=self.getCoords() # these values can be used 
        self.end1 # or this
        self.end2 # or that
        polygonpoints=[[1.,0.],[1.,1.],[0.,1.],[0.,0.]] #list of points which form the polygon
        polygonarray=np.array(polygonpoints)*self.triangle                 #makes an array out of the list
        curve=self.getCurvePoints(polygonarray[0],polygonarray[1],polygonarray[2],self.radius,20)        
        curvearray=np.array(curve)
        roundpolygon=np.vstack([polygonarray[0],curvearray,polygonarray[2]])
        p=roundpolygon
        self.insertElement(Polygon(p),xy=self.end1,angle=angle,layer=self.layer) # insert polygon (triangle), layer is the same 
        
#allPatterns={"2PtContacts":Pt2Contacts,"4PtContacts":Pt4Contacts,"2Cont&Dots":Pt2ContactsDots,
#             "Simple2Pt":Simple2Pt,"Simple4Pt":Simple4Pt,"Dots2Pt":Dots2Pt,"Dots4Pt":Dots4Pt,
#             "CPW":CPW,"CPW Contact":CPWContact}
allPatterns={"pn_Junction":pn_Junction,"pn_Antenna":pn_Antenna,"2PtContacts":Pt2Contacts,"Antenna":Antenna,"4PtContacts":Pt4Contacts,"2Cont&Dots":Pt2ContactsDots,
             "Simple2Pt":Simple2Pt,"Simple4Pt":Simple4Pt,"Dots2Pt":Dots2Pt,"Dots4Pt":Dots4Pt,"Triangol4Pt":Triangol4Pt,
             "CPW":CPW,"CPW Only Tapper":CPW_onlytap,"CPW Contact":CPWContact,"Bent CPW":BentCPW,"Bent Contact CPW":BentCPWContact,
             "Hall Contact":Hall,"2p+Gate":Gate2p,"invertedCPW":invertedCPW,"Equiv4Pt":Equiv4Pt,
             "StarkContacts":StarkContacts,"SimpleStark":SimpleStark,"CPWShort":CPWShort,
             "CPWShortContact":CPWShortContact}
defaultPattern="Simple2Pt"

##
#from matplotlib import *
#from matplotlib import pylab
#
#nw=CPWContact("absbca",end1=(10.,0),end2=(-10.,0))
#fig=pylab.figure()
#ax=fig.add_subplot(111)
#ax.set_xlim((-50,50))
#ax.set_ylim((-50,50))
#a=Structure("a")
#a.insertElement(nw)
#a.show(ax)
#pylab.show()
#a.save("test2.gds")
