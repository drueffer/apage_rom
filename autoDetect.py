# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 14:45:30 2012

@author: rueffer
"""

import time
import numpy as np
import numexpr as ne
#import cv2 as cv
import cv2
from matplotlib import pylab as plt
from matplotlib.patches import Rectangle
from matplotlib import transforms as MPLTransforms
from copy import deepcopy
from PatternGenerator import Descriptor,myRotate
from PatternGenerator import version as PatternGeneratorVersion
from PatternGenerator import GDSGeneratorVersion

version="0.981"
latest_changes="""allowed to detect more than one circle per bit --> inverse markers
"""

##TODO make all these object more efficient / 
class WireObject(object):
    def __init__(self,contour):
        self.Center,(a,b),c=cv2.minAreaRect(contour)
        if a >= b:
            self.Length = a
            self.Width = b
            c=c+90.
        else:
            self.Length = b
            self.Width = a
            while c < 0:
                c+=360.       
        self.Angle=np.mod(c,180)
        self.leftBottomCorner=(self.Center[0]-self.Width/2.,self.Center[1]-self.Length/2.)
        self.End1,self.End2=self.__getEnds__()
    
    def getPoints(self,rotated=True):
        L=self.Length
        W=self.Width
        points=np.array([(W/2.,L/2.),(-W/2.,L/2.),(-W/2.,-L/2.),(W/2.,-L/2)])
        if rotated:
            s=np.sin(self.Angle)
            c=np.cos(self.Angle)
            def rot(xy):
                return (xy[0]*c-xy[1]*s,xy[0]*s+xy[1]*c)
            points=np.array([np.array(self.Center)+rot(i) for i in points])
        return points
    
    def __getEnds__(self):
        length=self.Length/2.
        angle=(self.Angle)/180.*np.pi
        end1=self.Center+np.array([np.sin(angle),-np.cos(angle)])*length
        end2=self.Center+np.array([-np.sin(angle),np.cos(angle)])*length
        return end1,end2
        
    def getEnds(self,imageObject):
        End1=imageObject.transForm(self.End1)
        End2=imageObject.transForm(self.End2)
        return End1,End2
        
    def getTopBot(self,imageObject):
        End1=imageObject.transForm(self.End1)
        End2=imageObject.transForm(self.End2)
        if End1[1]>End2[1]:
            top=End1
            bottom=End2
        else:
            top=End2
            bottom=End1
        return top,bottom
    
    def getLength(self,imageObject):
        return self.Length*imageObject.scale
        
    def getWidth(self,imageObject):
        return self.Width*imageObject.scale
        

class EllipseObject(object):
    def __init__(self,contour):
        if len(contour) < 5:
            raise RuntimeError("Contour must have at least 5 points")
        self.Contour = contour
        self.Perim = cv2.arcLength(contour,True)
        self.Area= cv2.contourArea(contour)
        self.Center,self.Axes,self.Angle=cv2.fitEllipse(contour)
        self.Radius = (self.Axes[0]+self.Axes[1])/4.
        self.fgRect=cv2.boundingRect(contour)
        
        self.X = self.Center[0]
        self.Y = self.Center[1]
        if self.Area < 1:
            self.Area = 1
        self.Circ = (self.Perim**2)/(4*np.pi*self.Area)
        self.flattening=abs(self.Axes[0]-self.Axes[1])/max(self.Axes[0],self.Axes[1]) 
        
    def __get_Center__(self):
        return self.__Center__
    def __set_Center__(self,Center):
        self.__Center__=np.array(Center)
        
    Center=property(__get_Center__,__set_Center__)

class CircleObject(EllipseObject):
    def __init__(self,contour,**kwargs):
        super(CircleObject,self).__init__(contour)
        if not self.circleCheck(**kwargs):
            raise TypeError("Not an circle")
        
    def circleCheck(self,areaRatio=0.5,minPoly=6,minRadius=5,maxRadius=None,
                        polyAccu=2,maxFlattening=0.4,
                       checkFlattening=True,checkRadius=True,
                       checkArea=True,checkPoly=False,verboose=0,**kwargs):
        condition = True
        if checkFlattening and condition:
            try:
                condition = self.flattening < maxFlattening 
                if verboose >=2:
                    print "flaettening: " +str(self.flattening) + " - " + str(condition)
                elif verboose == 1 and not condition:
                    print "flaettening: " +str(self.flattening) + " - " + str(condition)
            except:
                print self.Axes
                condition = False
        if checkRadius and condition:
            condition = self.Radius>minRadius and (self.Radius < maxRadius or not maxRadius)
            if verboose >=2:
                print "radius: "+str(self.Radius)  + " - " + str(condition)
            elif verboose == 1 and not condition:
                print "radius: "+str(self.Radius)  + " - " + str(condition)   
        if checkArea and condition:
            par = abs(self.Radius**2*np.pi - self.Area)/self.Area
            condition =  par < areaRatio
            if verboose >=2:
                print "area ratio: "+str(par)  + " - " + str(condition)
            elif verboose == 1 and not condition:
                print "area ratio: "+str(par)  + " - " + str(condition)
        if checkPoly and condition:
            poly=cv2.approxPolyDP(self.Contour,polyAccu,True)
            condition = len(poly)>minPoly 
            if verboose >=2:
                print "length polynome: "+str(len(poly))  + " - " + str(condition)
            elif verboose == 1 and not condition:
                print "area ratio: "+str(par)  + " - " + str(condition)
        if condition:
            return True
            
        return False
        
    
class ImageObject(object):
    def __init__(self,image,bitTolerance=None,descriptor=Descriptor(),crop_x=(0,-1),crop_y=(0,-1),
        bitx=[(1,0),(2,0),(3,0),(0,1),(1,1),(2,1),(3,1)],bity=[(2,3),(1,3),(0,3),(3,2),(2,2),(1,2),(0,2)]):
        ##TODO: calculate bitx & bity
        t0=time.time()
        self.__IMG_input__=None
        self.__IMG_gray__=None
        self.__filename__=None
        if isinstance(image,str) or isinstance(image,unicode):
            self.__filename__=image
            self.__load__(crop_x=crop_x,crop_y=crop_y)
        else:
            self.__IMG_input__=deepcopy(image)
            if len(self.__IMG_input__.shape)==3:
                self.__IMG_gray__=cv2.cvtColor(self.IMG_input,cv2.cv.CV_BGR2GRAY)[crop_y[0]:crop_y[1],crop_x[0]:crop_x[1]]
            elif len(self.IMG_input.shape)==2:
                self.__IMG_gray__=self.__IMG_input__[crop_y[0]:crop_y[1],crop_x[0]:crop_x[1]]
                self.__IMG_input__=None
            else:
                raise TypeError("Unknown type")
        self.bits=np.array([bitx,bity])
        if bitTolerance == None:
            self.bitTolerance=descriptor.markerSize
        else:
            self.bitTolerance=bitTolerance
        self.descriptor=descriptor
        self.bitsFound=None
            
        self.center=None
        self.angle=None
        self.scale=None
        self.transForm=None
        self.invTransForm=None
        self.cell=None
        self.markers={}
        self.nanoWires=None
    
        
    def __get_shape__(self):
        return self.IMG_gray.shape
    def __set_shape__(self):
        raise RuntimeError("not allowed")
        
    shape = property(__get_shape__,__set_shape__)
    
    def __get_IMG_input__(self):
        if self.__IMG_input__ == None:
            return self.IMG_gray
        else:
            return self.__IMG_input__
        
    def __set_IMG_input__(self):
        raise RuntimeError("not allowed")
        
    def __get_IMG_gray__(self):
        if self.__IMG_gray__ == None:
            if self.__filename__ == None:
                raise RuntimeError("missing filename")
            else:
                self.__load__()
                out =self.__IMG_gray__
                self.__IMG_gray__=None
                return out
        else:
            return self.__IMG_gray__
        
    def __set_IMG_gray__(self):
        raise RuntimeError("not allowed")
        
    IMG_gray = property(__get_IMG_gray__,__set_IMG_gray__)
        
    IMG_input = property(__get_IMG_input__,__set_IMG_input__)

    
    def __get_desc__(self):
        return self.__desc__
        
    def __set_desc__(self,descriptor):
        if descriptor == None:
            self.__desc__=Descriptor()
        else:
            self.__desc__=descriptor
            
    descriptor = property(__get_desc__,__set_desc__)
    
    def checkCircle(self,contour,**kwargs):
        try:
            circle=CircleObject(contour,**kwargs)
            return circle
        except:
            return False
        
    def __load__(self,crop_x=(0,-1),crop_y=(0,-1)):
        self.__IMG_input__=cv2.imread(self.__filename__)
        if len(self.__IMG_input__.shape)==3:
            self.__IMG_gray__=cv2.imread(self.__filename__,0)[crop_y[0]:crop_y[1],crop_x[0]:crop_x[1]]
        else:                
            self.__IMG_gray__=cv2.imread(self.__filename__,0)[crop_y[0]:crop_y[1],crop_x[0]:crop_x[1]]
            self.__IMG_input__=None
    
        
    def reduceMemoryFoodPrint(self,toggle=True):
        if toggle:
            if self.__filename__==None:
                raise RuntimeError("not possible if not initialized with path")
            else:
                self.__IMG_gray__=None
        else:
            self.__load__()
        
    
    def getMedian(self,image=None,ksize=3,**kwargs):
        if image==None:
            image=self.IMG_gray
        timage=deepcopy(image)
        timage2 = cv2.medianBlur(timage,ksize)
        return timage2
#        timage3 = cv2.equalizeHist(timage2)
#        return timage3
        
    def getBinary(self,image=None,what=None,**kwargs):
        if image==None:
            image=self.IMG_gray
        timage=deepcopy(image)
#        timage=cv2.equalizeHist(timage)
        temp=cv2.adaptiveThreshold(timage,128,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,101,-10)
        th_otsu,img_bin=cv2.threshold(temp,128, 255,cv2.THRESH_OTSU)
#        img_bin=cv2.adaptiveThreshold(I.IMG_gray,128,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,101,-10))
#        th_otsu,img_bin=cv2.threshold(timage,(255-np.mean(timage)*2/3), 255,cv2.THRESH_BINARY)
        if np.average(timage) > th_otsu:
            img_bin=255-img_bin
        return img_bin
        
    def getFloodFilled(self,image=None,newVal=255,seedPoint=(0,0),**kwargs):
        if image==None:
            image=self.IMG_gray
        timage=deepcopy(image)
        h,w = timage.shape[:2]
        floodfilled = np.zeros((h+2, w+2), np.uint8)
        cv2.floodFill( timage,floodfilled,seedPoint,newVal,flags=cv2.FLOODFILL_MASK_ONLY)
        return floodfilled[1:-1,1:-1]
        
    def getMorphed(self,image=None,dilate=True,erode=True,dilateIter=3,erodeIter=3,kernel=(5,5),**kwargs):
        if image==None:
            image=self.IMG_gray
        timage=deepcopy(image)
        kernel = cv2.getStructuringElement(cv2.MORPH_DILATE,kernel)
        if dilate:
            timage=cv2.dilate(timage,kernel,iterations=dilateIter)
        if erode:
            timage=cv2.erode(timage,kernel,iterations=erodeIter)
        return timage
        
        
    def getRotated(self,image, point,angle,cutoff=1):
        timage=deepcopy(image)
        rot_mat=cv2.getRotationMatrix2D((point[0],point[1]),angle*180/np.pi,1.0)
        result = cv2.warpAffine(timage, M=rot_mat,dsize=(timage.shape[1],timage.shape[0]),
                                flags=cv2.INTER_LINEAR)
        cond=result<cutoff
        med= np.array(np.round(np.median(result)),dtype=result.dtype)
        x=np.ones(result.shape,dtype=med.dtype)*med
        return np.where(cond,x,result)        
    
    def getTrimmed(self,image,cutoff=3):
        result = self.getRotated(image,(self.center[0],self.center[1]),-self.angle/180.*np.pi)
        zero=np.round(self.center)
        factx=abs((self.bits.max()+1)*self.descriptor.bitDistance-self.descriptor.markerArea[0]/2.)/self.scale
        facty=abs((self.bits.max()+1)*self.descriptor.bitDistance-self.descriptor.markerArea[1]/2.)/self.scale
        x0=round(zero[0]-factx)
        x1=round(zero[0]+factx)
        y0=round(zero[1]-facty)
        y1=round(zero[1]+facty)
        med= np.array(np.round(np.median(result[y0:y1,x0:x1])),dtype=result.dtype)
        result[0:y0]=med
        result[:,0:x0]=med
        result[y1::]=med
        result[:,x1::]=med
        result = self.getRotated(result,(self.center[0],self.center[1]),self.angle/180.*np.pi)
        return result
      
    def meanThresh(self,image):
        a=np.mean(image)
        timage=np.empty(image.shape,dtype=image.dtype)
        timage.fill(a)
        timage=np.array(ne.evaluate("where(image>a,timage,image)"),dtype=image.dtype)
        return timage
#        
#    def prepareDetection_dif(self,image,doFloodFill=False,**kwargs): 
#        median=self.getMedian(image,**kwargs)
#        thresh=cv2.threshold(median,0,255,cv2.THRESH_OTSU)[0]
#        pre=cv2.Canny(median,thresh*0.5,thresh)
#        return self.getMorphed(pre,**kwargs)
        
    def prepareDetection(self,image,doFloodFill=False,**kwargs):   
        median=self.getMedian(image,**kwargs)
        binary=self.getBinary(median)
        if doFloodFill:
            pre=self.getFloodFilled(binary,**kwargs)
        else:
            pre=binary
        return self.getMorphed(pre,**kwargs)
    

    def findContours(self,image,**kwargs):
        timage=deepcopy(image)
        contours, hierarchy = cv2.findContours(timage,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
    def findCircles(self,contours,retResiduals=False,**kwargs):
        allCircles=[]
        if retResiduals:
            res=[]
        for n,contour in enumerate(contours):
            circle=self.checkCircle(contour,maxRadius=self.shape[0]/2.,minRadius=15,**kwargs)
            if circle:
                allCircles.append(circle)
            elif retResiduals:
                res.append(contour)
        if retResiduals:
            return allCircles,res
        else:
            return allCircles
    
    def findMarkers(self,image=None,**kwargs):
        t0=time.time()
        prep=self.prepareDetection(image,**kwargs)
        t1=time.time()
        contours=self.findContours(prep,**kwargs)
#        print str(len(contours)) +" contours found"
        circles,noncircles=self.findCircles(contours,retResiduals=True,**kwargs)
#        print str(len(circles)) +" circles found"

        try:
            markers=self.sortMarkers(circles,indices=False)
        except:
            self.cell=None
            return "Could not find markers"
        string1=self.calcTransformation(markers,**kwargs)   
        try:
            string2=self.calcPosition(markers["others"])
        except:
            self.cell=None
            return "Could not resolve bitpattern"
        return "found markers in: %.3fms (%.3fms image trans)\n"%(((time.time()-t0)*1000),(t1-t0)*1000)+string2+string1
        
        
    def findAllCircles(self,image=None,**kwargs):
        prep=self.prepareDetection(image,**kwargs)
        contours=self.findContours(prep,**kwargs)
        return self.findCircles(contours,retResiduals=False,**kwargs)
        
    def findNanowires(self,image=None,minLength=5):
        t0=time.time()
        if image == None:
            image=self.IMG_gray
#        thresh=self.meanThresh(image)
        t1=time.time()
        thresh=cv2.adaptiveThreshold(image,128,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,201,0)
        t2=time.time()
#        prep=self.prepareDetection(thresh)
        contours=self.findContours(thresh)
        liste=[]
#        print contours
        for contour in contours:
            wire=WireObject(contour)
            if wire.Length*self.scale > minLength and wire.Length*self.scale < min(self.descriptor.markerArea) and wire.Length > 2.* wire.Width:
                liste.append(WireObject(contour))
        self.nanoWires=liste
        return "found %d wires in: %.3fms (%.3fms adaptive threshold)\n"%((len(liste),(time.time()-t0)*1000,(t2-t1)*1000))
       
    def getLongestWire(self):
         l=np.argmax([wire.Length/wire.Width for wire in self.nanoWires])
         return self.nanoWires[l],l
        
    def sortMarkers(self,circles,indices=False,**kwargs):
        coordinates=np.empty((len(circles),2))
        for n,circle in enumerate(circles):
            coordinates[n][0]=circle.Center[0]
            coordinates[n][1]=circle.Center[1]
        br=np.argmax(coordinates[:,0]+coordinates[:,1])
        tl=np.argmax(-coordinates[:,0]-coordinates[:,1])
        tr=np.argmax(coordinates[:,0]-coordinates[:,1])
        bl=np.argmax(-coordinates[:,0]+coordinates[:,1])
        d={}
        d.update({"bottomRight":circles[br]})
        d.update({"topRight":circles[tr]})
        d.update({"bottomLeft":circles[bl]})
        d.update({"topLeft":circles[tl]})
        for i in sorted([br,tr,bl,tl])[::-1]:
            circles.pop(i)
        d.update({"others":circles})
        self.markers.update(d)
        return d
        
        
    def calcTransformation(self,markers,**kwargs): 
        # not the inverted y axis in images!!!
        l=["topLeft","topRight","bottomRight","bottomLeft","topLeft"]
#        for li in l:
#            print markers[li].Center
        vectors=np.empty((4,2))
        for i in range(4):
            vectors[i]=(markers[l[i+1]].Center-markers[l[i]].Center)
        centers=np.empty((4,2))
        scales=np.empty(4)
        angles=np.empty(4)
        s=np.array(self.descriptor.markerArea,dtype=np.float)
        origUnitVectors=np.array([[1.,0.],[0.,1.],[-1.,0.],[0.,-1.]])
        magnitudes=np.sqrt(vectors[:,0]**2+vectors[:,1]**2)
        unitVectors=np.divide(vectors.T,magnitudes).T
        for i in range(4):
            ba=s[np.mod(i+1,2)]/s[np.mod(i,2)]
            a=np.arctan(ba)*180/np.pi
            centers[i]=myRotate(unitVectors[i],a)*magnitudes[i]/2.*np.sqrt(1.+(ba)**2)+markers[l[i]].Center
            scales[i]=np.divide(s[np.mod(i,2)],np.sqrt(vectors[i,0]**2+vectors[i,1]**2))
            angles[i]=np.arcsin(np.cross(origUnitVectors[i],unitVectors[i]))*(-1)
        center=np.average(centers,0)
        stdCenter=np.std(centers,0)
        scale=np.average(scales)
        stdScale=np.std(scales)
        angle=np.average(angles)*180./np.pi
        stdAngle=np.std(angles)*180./np.pi
        string=""
        string += "Calculated coordinate system:\n"
        string +=  "Center: (%.3f,%.3f, +- %.3f,%.3f)px [+- %.3f,%.3f nm]\n"%(center[0],center[1],stdCenter[0],stdCenter[1],stdCenter[0]*scale*1000,stdCenter[1]*scale*1000)
        string +=  "Scale: (%.3f +- %.3f)nm/px\n"%(scale*1000,stdScale*1000)
        string +=  u"Angle: (%.3f +- %.3f)°\n"%(angle,stdAngle)
        transForm=self.descriptor.createTransformFunc(center,angle,scale)
        invTransForm=self.descriptor.createInverseTransformFunc(center,angle,scale)
        self.center=center
        self.angle=angle
        self.scale=scale
        self.transForm=transForm
        self.invTransForm=invTransForm
        d={"center":center,"angle":angle,"scale":scale,"transForm":transForm,"invTransForm":invTransForm,
           "std":{"center":stdCenter,"angle":stdAngle,"scale":stdScale}
            }
        return string
            
    def calcCircleCoordinates(self,circles,**kwargs):
        temp=np.empty((len(circles),2))
        for n,circle in enumerate(circles):
            temp[n]=circle.Center
        return self.transForm(temp)  
        
        
    def calcPosition(self,circles,**kwargs):
        coords=self.calcCircleCoordinates(circles,**kwargs)
#        print coords
        pos=np.array([0,0])
        bitsFound=np.empty(self.bits[0].shape,dtype=np.bool)
        for n,bits in enumerate(self.bits):
            for m,bit in enumerate(bits):
                x=-self.descriptor.markerArea[0]/2.+bit[0]*self.descriptor.bitDistance
                y=-self.descriptor.markerArea[1]/2.+bit[1]*self.descriptor.bitDistance
                a=np.logical_and(coords[:,0]<x+self.bitTolerance,coords[:,0]>x-self.bitTolerance)
                b=np.logical_and(coords[:,1]<y+self.bitTolerance,coords[:,1]>y-self.bitTolerance)
                w= np.argwhere(np.logical_and(a,b))
                if len(w) == 0:
                    bitsFound[m,n]=False
                elif len(w) >= 1:
                    pos[n]+=2**m
                    bitsFound[m,n]=True
                else:
                    raise RuntimeError("could not resolve bitpattern")
        self.cell=pos
        return  "Cell: " + str(int(pos[0])) + ", " + str(int(pos[1]))
        

    def showMarkers(self,ax,color=[128,0,0],lw=1,ms=10,marker="+",cellFrame=False):
        color=[c/255. for c in color]
        for key in self.markers.keys():
            if key != "others":
                ax.add_artist(plt.Line2D([self.markers[key].Center[0]],
                                         [self.markers[key].Center[1]],
                                         color=color,marker=marker,ms=ms))
        ax.add_artist(plt.Line2D([self.center[0]],
                                 [self.center[1]],
                                 color=color,marker=marker,ms=ms*2))
                                         
        if cellFrame:
            xy=self.invTransForm([-self.descriptor.markerArea[0]/2.,self.descriptor.markerArea[1]/2.])
            t = MPLTransforms.Affine2D().rotate_around(xy[0],xy[1],-self.angle/180.*np.pi) + ax.transData
            p = Rectangle(xy,width=self.descriptor.markerArea[0]/self.scale,height=self.descriptor.markerArea[1]/self.scale,
                          fc="none",lw=lw,color=color)
            p.set_transform(t)
            ax.add_artist(p)

    def showBitPositions(self,ax,color=[0,0,255]):
        color=[c/255. for c in color]
        px,py,tx,ty=self.descriptor.getBits(self.cell)
        truth=np.hstack((tx,ty))
        for i,pos in enumerate(np.vstack((px,py))):
            if truth[i]:
                fc="r"
            else:
                fc="none"
            xy=self.invTransForm([(pos[0]-0.5/self.scale),(pos[1]-0.5/self.scale)])
            p = Rectangle(xy,width=self.descriptor.bitDistance/self.scale,height=-self.descriptor.bitDistance/self.scale,
                          fc=fc,lw=1,alpha=0.3)
            t = MPLTransforms.Affine2D().rotate_around(xy[0],xy[1],-self.angle/180.*np.pi) + ax.transData
            p.set_transform(t)
            ax.add_artist(p)
            
    def showNanowires(self,ax,wires,color=[0,0,128],color_best=[128,0,0],alpha=0.5):
        color=[c/255. for c in color]
        color_best=[c/255. for c in color_best]
        bestAspect=np.argmax([wire.Length for wire in wires])
        for n,wire in enumerate(wires):
            if n == bestAspect:
                c=color_best
            else:
                c=color
            p1 = Rectangle(wire.leftBottomCorner,width=wire.Width,height=wire.Length,color="none",fc=c,alpha=0.2)
            p2 = Rectangle(wire.leftBottomCorner,width=wire.Width,height=wire.Length,color=c,fc="none",lw=1)
            t = MPLTransforms.Affine2D().rotate_around(wire.Center[0],wire.Center[1],wire.Angle) + ax.transData
            p1.set_transform(t)
            p2.set_transform(t)
            ax.add_artist(p1)
            ax.add_artist(p2)
    
    def showImage(self,ax):
        ax.imshow(self.IMG_input,interpolation="none",cmap="gray")
#
#fn=r"D:\transfer\test Daniel\13.jpg"
#a=cv2.imread(fn,0)            
##print a
##t0=time.time()                  
#I=ImageObject(a)
##t1=time.time()            
##print "init: %.3fms"%((t1-t0)*1000)
##I.findMarkers()
##print "total time: %.3fms"%((time.time()-t0)*1000)
###
##fig = plt.figure()
##axes = fig.add_subplot(111)
##axes.imshow(I.IMG_input,interpolation="none",cmap="gray")
##I.showMarkers(axes)
###I.showBitPositions(axes)
###
##l= I.findNanowires()
###I.showNanowires(axes,l)
#
#
#fn=r"D:\transfer\test Daniel\26.jpg"
#a2=cv2.imread(fn,0)            
##print a
##t0=time.time()                  
#I2=ImageObject(a2)
##t1=time.time()            
##print "init: %.3fms"%((t1-t0)*1000)
#I2.findMarkers()



#imshow(cv2.adaptiveThreshold(I.IMG_gray,128,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,501,0))