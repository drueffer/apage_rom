# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 10:23:40 2012

@author: rueffer
"""
import os
import tarfile
import shutil
import tempfile
#import json as dumper
import pickle as dumper
import StringIO
from autoDetect import Descriptor
from autoDetect import ImageObject
from createCJOB import CjobFile,CincFile,FtxtFile
import re
import time

from autoDetect import version as autoDetectVersion
from createCJOB import version as createCJOBVersion
from autoDetect import PatternGeneratorVersion
from autoDetect import GDSGeneratorVersion
#dynamic loading of Patterns Plugin:

import sys
sys.path.append("./plugins/")
from Patterns import *
import EbeamSettings

version = "0.982"
latest_changes="""
0.982: no error if an option in pattern is not existing: uses default then
0.981: introduces MSF for LB, takes it from EbeamSettings.py
0.981: multiple layers considered in PEC if the same camps settting is chosen
"""
pat1=re.compile(".+\.([a-zA-Z0-9_]+)'>.*")


class ContactProject(object):
    def __init__(self,descriptor=Descriptor(),):
        self.version=version
        self.filename=None
        self.paths=[]
        self.settings=[]
        self.exposure=set()
        self.fitLogs=[]
        self.imageObjects=[]
        self.descriptor=descriptor
        self.saved=False
        self.allPatterns=allPatterns
        self.defaultPattern=defaultPattern
        self.exposureSettings={"layer":set(),"dose":{},"beam":{},"res":{},"mPEC_beamsize":{},
                               "camps":{},"doPEC":{},"beta":{},"eta":{},"multiPEC":{},
                                "ignoreHeightError":{},"MSF":{},"PECLayers":{},"negativeMarker":{}}
#                               "camps":{},"doPEC":{},"alpha":{},"beta":{},"eta":{}}
        self.defExposureSetting=EbeamSettings.defExposureSettings
        self.beams=EbeamSettings.beams
        self.beamsizes=EbeamSettings.beamsizes
        self.MSF=EbeamSettings.MSF
        self.minRes=EbeamSettings.minRes
        self.maxRes=EbeamSettings.maxRes

    def getPECLayers(self,layer):
        CAMP=self.exposureSettings["camps"][layer]
        layers=list(self.getLayers())
        cl=[]
        for l in layers:
            if self.exposureSettings["camps"][l]==CAMP:
                cl.append(l)
        return sorted(cl)
            
        
    def getExposureSettings(self,layer):
#        print "layer:"+str(layer)
        d={}
        for i in self.exposureSettings.keys():
            if not i == "layer":
                try:
                    d.update({i:self.exposureSettings[i][layer]})
                except Exception as e:
                    print str(e)
        d.update({"beamsize":self.beamsizes[self.exposureSettings["beam"][layer]]})
        d.update({"MSF":self.MSF[self.exposureSettings["res"][layer]]})
        d.update({"PECLayers":self.getPECLayers(layer)})
        
        return d
              
        
    
    def __refit__(self,index):
        string = self.fit(index,firstLine=False)
        self.fitLogs[index]=string
        self.saved=False
        return string
        
    def refitImages(self,indices):
        if not isinstance(indices,list):
            indices=[indices]
        indices=sorted(indices)[::-1]
        for index in indices:
            self.__refit__(index)
        
            
    def addImage(self,path):
        if not os.path.isfile(path):
            raise IOError(path + " is not a valid file")
        self.paths.append(path)
        self.imageObjects.append(None)
        self.settings.append({"mode":"auto","fit":False,"contactOptions":{}})
#        self.settings.append({"mode":"auto","fit":False,"contact":self.defaultPattern,"contactOptions":{}})
#        options=self.getContactOptions(self.defaultPattern)
#        for key in options.keys():
#            self.settings[-1]["contactOptions"].update({key:options[key]})
        string = self.fit(-1,firstLine=False)
        self.fitLogs.append(string)
        self.changeContactType(-1,self.defaultPattern)
        self.saved=False
        return string
    
    def addImages(self,paths):
        if not isinstance(paths,list):
            paths=[paths]
        for path in paths:
            self.addImage(path)
        
    def __removeImage__(self,index):
        self.paths.pop(index)
        self.settings.pop(index)
        self.fitLogs.pop(index)
        self.imageObjects.pop(index)
        self.saved=False
    
    def removeImages(self,indices):
        if not isinstance(indices,list):
            indices=[indices]
        indices=sorted(indices)[::-1]
        for index in indices:
            self.__removeImage__(index)
        
    def save(self,filename):
        self.version=version
        p=[os.path.relpath(path,os.path.dirname(filename)) for path in self.paths]
        tar=tarfile.open(filename,mode="w:bz2")
        string1=dumper.dumps(p)
        info1 = tarfile.TarInfo(name="paths")
        info1.size=len(string1)
#        self.version=version
        tar.addfile(tarinfo=info1, fileobj=StringIO.StringIO(string1))
        for name,obj in [("settings",self.settings),("descriptor",self.descriptor),
                         ("exposure",self.exposureSettings),("fitLogs",self.fitLogs),("version",self.version)]:
            string=dumper.dumps(obj)
            info = tarfile.TarInfo(name=name)
            info.size=len(string)
            tar.addfile(tarinfo=info, fileobj=StringIO.StringIO(string))
        tar.close()
        self.filename=filename
        self.saved=True

    def load(self,filename):
        tar=tarfile.open(filename,mode="r:bz2")
        self.filename=filename
        paths=dumper.loads(tar.extractfile("paths").read())
        d=os.path.dirname(filename)
        self.paths=[os.path.join(d,p) for p in paths]
        self.settings=dumper.loads(tar.extractfile("settings").read())
        self.descriptor=dumper.loads(tar.extractfile("descriptor").read())
        self.exposureSettings=dumper.loads(tar.extractfile("exposure").read())
        self.fitLogs=dumper.loads(tar.extractfile("fitLogs").read())
        try:
            self.version=dumper.loads(tar.extractfile("version").read())
        except KeyError:
            self.version="<0.970"
        for p in self.paths: self.imageObjects.append(None)
        tar.close()
        self.saved=True
        
    def __idsToList__(self,imageIDs=None):
        if imageIDs == None:
            imageIDs = range(len(self.paths))
        elif imageIDs == -1:
            imageIDs = [len(self.paths)-1]
        elif isinstance(imageIDs,int):
            imageIDs = [imageIDs]
        elif isinstance(imageIDs,list):
            pass
        else: 
            raise TypeError
        return imageIDs
    
    def getLongestWire(self,imageID):
        lengths=[]
        for wire in self.settings[imageID]["wires"]:
            end1=wire["end1"]
            end2=wire["end2"]
            vec=np.array([end1[0],end1[1]])-np.array([end2[0],end2[1]])
            lengths.append(np.sqrt(vec[0]**2+vec[1]**2)/wire["w"])
        try:
            return np.argmax(lengths)
        except ValueError:
            return None
    
    def getEnds(self,imageID,wireID):
        end1=self.settings[imageID]["wires"][wireID]["end1"]
        end2=self.settings[imageID]["wires"][wireID]["end2"]
        return end1,end2
    
    def setEnd(self,imageID,name,new):
        self.settings[imageID][name]=new
    
    def setMode(self,imageID,mode="auto"):
        if mode == "auto":
            wireID=self.getLongestWire(imageID)
            if wireID != None:
                end1,end2=self.getEnds(imageID,wireID)
            else:
                end1=np.array([10.,0])
                end2=np.array([-10.,0])
            self.settings[imageID].update({"mode":"auto","selected":wireID,"end1":end1, "end2":end2})
        elif mode in ["select","manual"]:
            self.settings[imageID].update({"mode":mode})
        else:
            raise ValueError("Unknown mode: "+mode)
            
    def changeWire(self,imageID,wireID):
        if self.settings[imageID]["mode"]=="auto":
            raise ValueError("can't change wire in auto mode")
        end1,end2=self.getEnds(imageID,wireID)
        self.settings[imageID].update({"selected":wireID,"end1":end1, "end2":end2})
        
    def getWireNo(self,imageID):
        return self.settings[imageID]["selected"]
        
    def __auto__(self,imag,i):
        self.settings[i].update({"cell":imag.cell})
        l=[]
        for wire in imag.nanoWires:
            end1,end2=wire.getEnds(imag)
            d={"end1":end1,"end2":end2,"w":wire.getWidth(imag)}
            l.append(d)
        self.settings[i].update({"wires":l})
        l=[]
        for key in imag.markers.keys():
            if key != "others":
                l.append(imag.markers[key].Center.tolist())
        self.settings[i].update({"markers":l})
        self.saved=False
        self.setMode(i,mode="auto")
        
    def changeMode(self,imageIDs,mode):
        imageIDs=self.__idsToList__(imageIDs)
        if mode not in ["auto","select","manual"]:
            raise ValueError("Unknown type: "+mode)
        for i in imageIDs:
            self.setMode(i,mode)
        
    def changeExposureSetting(self,key,layer,value):
        if key == "res":
            value=float(value)
            if value <= self.maxRes and value >= self.minRes:
                self.exposureSettings["res"].update({layer:value})
            else:
                raise KeyError("Unknown resolution: "+str(value))
        elif key == "beam":
            if self.beams.has_key(value) and self.beamsizes.has_key(value):
                self.exposureSettings["beam"].update({layer:value})
            else:
                raise KeyError("Unknown beam: "+str(value))
        elif key in ["beamsize","MSF","PECLayers"]:
            raise KeyError("This parameter cannot be changed manually")
        elif key == "camps":
            value=int(value)
            if value <= self.descriptor.maxMarker and  value >=0:
                self.exposureSettings["camps"].update({layer:value})
            else:
                raise KeyError("Marker selection out of range: "+str(value))
        elif type(self.exposureSettings[key][layer]) == bool:
            if value in ["true","True","TRUE"]:
                value=True
            elif value  in ["false","False","FALSE"]:
                value=False
            else:
                value=bool(value)
            self.exposureSettings[key].update({layer:value})
        else:
            value=type(self.exposureSettings[key][layer])(value)
            self.exposureSettings[key].update({layer:value})
            
            
    def updateLayers(self):
        self.exposureSettings["layer"]=self.getLayers()
        for layer in self.exposureSettings["layer"]:
            for key in self.exposureSettings.keys():
                if key != "layer":
                    if not self.exposureSettings[key].has_key(layer):
                        self.exposureSettings[key].update({layer:EbeamSettings.defExposureSettings[key]})
        for key in self.exposureSettings.keys():
            if key != "layer":
                for layer in self.exposureSettings[key].keys():
                    if not layer in self.exposureSettings["layer"]:
                        self.exposureSettings[key].pop(layer)

    
    def changeContactType(self,imageIDs,contactName):
        imageIDs=self.__idsToList__(imageIDs)
        options=self.getContactOptions(contactName)
        self.changeContactOptions(imageIDs,contactName,options)
        self.updateLayers()
        
    def getContactOptions(self,contactName):
        obj=self.allPatterns[contactName]("test")
        return obj.getOptions()
        
    def changeSingleContactOptions(self,imageIDs,key,value):
        imageIDs=self.__idsToList__(imageIDs)
        for i in imageIDs:
            contactName=self.settings[i]["contact"]
            oldt=type(self.getContactOptions(contactName)[key])
            if not self.settings[i]["contactOptions"].has_key(key):
                value=self.getContactOptions(contactName)[key]
            if oldt==bool:
                if value in ["True","true","yes","Yes","TRUE","YES","1","ON","on","On"]:
                    value=True
                else:
                    value=False
            else:
                value=oldt(value)
#            print key + ": "+str(oldt) +" converted to " + str(type(value))
            self.settings[i]["contactOptions"].update({key:value})
        self.updateLayers()
        
    def changeContactOptions(self,imageIDs,contactName,options):
        imageIDs=self.__idsToList__(imageIDs)
        for i in imageIDs:
            self.settings[i]["contact"]=contactName
            self.settings[i].pop("contactOptions")
            self.settings[i].update({"contactOptions":{}})
            for key in options.keys():
                value=options[key]
#                oldt=type(options[key])
#                value=type(self.settings[i]["contactOptions"][key])(options[key])
#                print key+": "+str(oldt) +" converted to " + type(value)
                self.settings[i]["contactOptions"].update({key:value})
        
    
    def showCell(self,ax,imageID,contact=Pt2Contacts,fitextents=False,**kwargs):
        if self.settings[imageID]["fit"]:
            CELL=Cell(self.settings[imageID]["cell"],descriptor=self.descriptor)
            for m,wire in enumerate(self.settings[imageID]["wires"]):
                nw=NanoWire("C"+CELL.name[5:]+"_wire_%d"%m,end1=wire["end1"],
                                            end2=wire["end2"],width=wire["w"],text="W_%d"%m)
                nw.make()
                CELL.insertElement(nw)
            end1=self.settings[imageID]["end1"]
            end2=self.settings[imageID]["end2"]
            obj=self.allPatterns[self.settings[imageID]["contact"]]
            kw=self.settings[imageID]["contactOptions"]
            kwargs.update(kw)
            elem=obj("C"+CELL.name[4:]+"_contact",end1=end1,end2=end2,**kwargs)
            elem.make()
            CELL.insertElement(elem)
            pltTransform=self.createInverseTransformFunc(imageID)
            if fitextents:
                extents=CELL.calcExtents()
                minimum=pltTransform(extents[:,0])*1.1
                maximum=pltTransform(extents[:,1])*1.1
#                print extents
                ax.set_xlim(minimum[0],maximum[0])
                ax.set_ylim(minimum[1],maximum[1])
            return CELL.show(ax,pltTransform=pltTransform)
            
    def getLayers(self,imageIDs=None):
        layers=set()
        imageIDs=self.__idsToList__(imageIDs)
        for i in imageIDs:
            if self.settings[i]["fit"]:
                obj=self.allPatterns[self.settings[i]["contact"]]
                end1=self.settings[i]["end1"]
                end2=self.settings[i]["end2"]
                kw=self.settings[i]["contactOptions"]
                elem=obj("temp",end1=end1,end2=end2,**kw)
                layers=layers.union(elem.getDefLayers())
        #blocks,blockTuples,blockNumbers,layers=self.__blockTuples__(imageIDs)
        return layers
        
    def __blockTuples__(self,imageIDs,**kwargs):
        blocks={}
        blockNumbers={}
        blockTuples=[]
        layers=set()
        imageIDs=self.__idsToList__(imageIDs)
        for i in imageIDs:
            if self.settings[i]["fit"]:
                CELL=Cell(self.settings[i]["cell"],descriptor=self.descriptor)
                bn=CELL.getBlockNo()
                sbn=str(bn[0])+","+str(bn[1])
                if not blocks.has_key(sbn):
                    BLOCK=Block(bn,descriptor=self.descriptor)
                    blocks.update({sbn:BLOCK})
                    blockNumbers.update({sbn:bn})
                    blockTuples.append(bn)
                else:
                    BLOCK=blocks[sbn]
                BLOCK.insertElement(CELL)
                for m,wire in enumerate(self.settings[i]["wires"]):
                    nw=NanoWire("C"+CELL.name[4:]+"_wire_%d"%m,end1=wire["end1"],
                                                end2=wire["end2"],width=wire["w"],text="W_%d"%m)
                    nw.make()
                    CELL.insertElement(nw)
                end1=self.settings[i]["end1"]
                end2=self.settings[i]["end2"]
                obj=self.allPatterns[self.settings[i]["contact"]]
                kwargs2=deepcopy(kwargs)
                kw=self.settings[i]["contactOptions"]
                kwargs2.update(kw)
                elem=obj("C"+CELL.name[4:]+"_contact",end1=end1,end2=end2,**kwargs2)
                elem.make()
                CELL.insertElement(elem)
                layers=layers.union(elem.getLayers())
        return blocks,blockTuples,blockNumbers,layers
        
    def exportSettings(self,path,imageIDs=None):
        outputFile=open(path,"w")
        imageIDs=self.__idsToList__(imageIDs)
        d={}
        nf=[]
        for i in imageIDs:
            if self.settings[i]["fit"]:
                contactType=self.settings[i]["contact"]
                if d.has_key(contactType):
                    d[contactType].append(i)
                else:
                    d.update({contactType:[i]})
            else:
                nf.append(i)
        t=""
        for typ in d:
            co=self.settings[d[typ][0]]["contactOptions"]
            if t != "":
                t+="\n"
            t+=typ+"\n"
            t+="Cell\tLength\tposition (mm)\t"
            for o in co:
                t+=o+"\t"
            t+="\n"
            for i in d[typ]:
                cell=self.settings[i]["cell"]
                vec=self.settings[i]["end2"]-self.settings[i]["end1"]
                length=np.sqrt(np.dot(vec,vec))
                t+=str(cell[0])+"-"+str(cell[1])+"\t%.2f\t%.3f,%.3f\t"%((length,self.descriptor.getCellPosition(cell)[0]/1000.,self.descriptor.getCellPosition(cell)[1]/1000.))
                for o in co:
                    t+=str(self.settings[i]["contactOptions"][o])+"\t"
                t+="\n"
                    
        outputFile.write(t)
        outputFile.close()
        
    # removed from below: contact=Pt2Contacts,
    def export(self,path,imageIDs=None,fileType="GDS",**kwargs):
        """fileType = "GDS" or "CATS"
        """
        if fileType == "GDS":
            gds=FlexiPattern("Wafer",descriptor=self.descriptor)
        elif fileType == "CATS":
            if not path[-5:] == ".nwco":
                path=path+".nwco"
            fd=tempfile.mkdtemp()
        else:
            raise ValueError("only GDS or CATS fileType")
        blocks,blockTuples,blockNumbers,layers=self.__blockTuples__(imageIDs,**kwargs)
        del blockTuples ## NOT NEEDED
        filenames=[]
        blockTOC={}
        for l in self.exposureSettings["layer"]:
            blockTOC.update({l:[]})
        for key in blocks.keys():
            BLOCK=blocks[key]
            if fileType == "CATS":
                BLOCK=BLOCK.insertPatterns(details=0)
                fn=os.path.join(fd,os.path.basename(path)[:-5]+"_"+BLOCK.name+".gds")
                filenames.append(fn)
                for l in BLOCK.getLayers():
                    if l < 100: ##TODO HARDLIMIT-> NOT GOOD
                        blockTOC[l].append(blockNumbers[key])
                BLOCK.save(fn)
            else:
                gds.insertElement(BLOCK)
        if fileType == "CATS":
            layers=list(self.exposureSettings["layer"])
            beams=self.exposureSettings["beam"]
            doses=self.exposureSettings["dose"]
            blocks=[blockTOC[l] for l in layers]
            camps=self.exposureSettings["camps"]
            res=self.exposureSettings["res"]
            negativeMarker=self.exposureSettings["negativeMarker"]
#            print layers
#            print doses
#            print beams
#            print camps
#            d=deepcopy(self.exposureSettings)
#            d.update({"blocks":blocks})
            tf=tarfile.open(path,mode="w:bz2")
            for fn in filenames:
                tf.add(fn,arcname=os.path.basename(fn))
#            print doses
            cjob=CjobFile(descriptor=self.descriptor,beams=self.beams)
            string=cjob.getString(os.path.basename(path)[:-5],layers,blocks,doses,
                                  beams,camps,negativeMarker=negativeMarker)
            info = tarfile.TarInfo(name=os.path.basename(path)[:-5]+".cjob")
            info.size=len(string)
            tf.addfile(tarinfo=info, fileobj=StringIO.StringIO(string))
            cinc=CincFile(descriptor=self.descriptor)
            for n,layer in enumerate(layers):
                for m,block in enumerate(blocks[n]):
                    string=cinc.getCinc(os.path.basename(path)[:-5],block,layer,res[layer])
                    info = tarfile.TarInfo(name="%d_%d.cinc"%((n,m)))
                    info.size=len(string)
                    tf.addfile(tarinfo=info, fileobj=StringIO.StringIO(string))
#            ftxt=FtxtFile(descriptor=self.descriptor)
            ftxt=FtxtFile()
            for n,layer in enumerate(layers):
                exposureSettings=self.getExposureSettings(layer)
                for m,block in enumerate(blocks[n]):
                    string=ftxt.getFtxt(os.path.basename(path)[:-5],block,layer,exposureSettings)
                    info = tarfile.TarInfo(name="%d_%d.ftxt"%((n,m)))
                    info.size=len(string)
                    tf.addfile(tarinfo=info, fileobj=StringIO.StringIO(string))
                if exposureSettings["ignoreHeightError"]:
                    string="pg set hgtmode 0"
                    info = tarfile.TarInfo(name=os.path.basename(path)[:-5]+"_L%02d.ini"%n)
                    info.size=len(string)
                    tf.addfile(tarinfo=info, fileobj=StringIO.StringIO(string))
            tf.close()
            string=get_nwcp_convert()
            f=open(os.path.dirname(path)+"/nwcp_convert","wb")
            f.write(string)
            f.close()
            string=get_nwcp_convert_lb()
            f=open(os.path.dirname(path)+"/nwcp_convert_lb","wb")
            f.write(string)
            f.close()
            shutil.rmtree(fd)
        else:
            gds.insertPatterns(details=2)
            gds.save(path)
        
    def fit(self,imageIDs=None,firstLine=True):
        imageIDs=self.__idsToList__(imageIDs)
        if firstLine:
            string="Fitting %d images:\n"%len(imageIDs)
        else:
            string=""
        t0=time.time()
        for i in imageIDs:
            string+="------%d------\n"%i
            string+="Filename: "+os.path.basename(self.paths[i])+"\n"
            imag=ImageObject(self.paths[i],descriptor=self.descriptor)
            string+=imag.findMarkers()
            if imag.cell == None:
                self.settings[i]["cell"]=None
                return string
            string+=imag.findNanowires()
            imag.reduceMemoryFoodPrint()
            self.imageObjects[i]=imag
            self.settings[i].update({"fit":True,"scale":imag.scale,"angle":imag.angle,"center":imag.center})
            self.__auto__(imag,i)
        string+="---FINISHED---\n"
        string+="Total time: %.3fs"%(time.time()-t0)
        self.saved=False
        return string
    
                  
    
    def createInverseTransformFunc(self,index):   
        center=self.settings[index]["center"]
        scale=self.settings[index]["scale"]
        angle=self.settings[index]["angle"]
        sub=center*np.array([1,-1])*scale
        return self.descriptor.createInverseTransformFunc(center,angle,scale)
           
    def createTransformFunc(self,index):   
        center=self.settings[index]["center"]
        scale=self.settings[index]["scale"]
        angle=self.settings[index]["angle"]
        sub=center*np.array([1,-1])*scale
        return self.descriptor.createTransformFunc(center,angle,scale)
        
    def __repr__(self):
        if self.filename == None:
            f=""
        else:
            f=self.filename+", "
        if len(self.paths)==1:
            l="1 image"
        else:
            l="%d images"%len(self.paths)
        return "<"+re.sub(pat1,r"\1: ",str(type(self)))+f+l+">"

def get_nwcp_convert():
    string = """#!/usr/bin/python
#===============================================================================
# This tool helps to automatically convert *.nwco files created by GUIContact
# to cjob and gpf files, which are autoamtically transferred to the EBEAM.
# IMPORTANT: This tool uses CATS, if you want to use LayoutBeamer use 
#            nwcp_convert_lb.
# At the ebeam computer the tool nwcp_unpack helps to avoid chaos...
# 
# Copyright Daniel Rueffer, EPFL 2012
#===============================================================================
import tarfile
from optparse import OptionParser
import tempfile
import os
import glob
import shutil
import re
from sys import argv as sysargv

usage = "usage: %prog [options] FILE"
parser = OptionParser(usage=usage)
parser.add_option("-u", "--user", dest="userid",default="",
                  help="use specific userid", metavar="USER")
(options, args) = parser.parse_args()

if len(args)!=1:
    raise ValueError("not enough arguments")

def getScript():
    return $$"$$#!/usr/bin/python

from optparse import OptionParser
import tarfile
import os

usage = "usage: %prog [options] FILE"
parser = OptionParser(usage=usage)

(options, args) = parser.parse_args()

if len(args)!=1:
    raise ValueError("not enough arguments")


tar=tarfile.open(args[0],mode="r:bz2")
for member in tar:
    tar.extract(member)
tar.close()
os.system("mv "+args[0][:-5]+".cjob ../jobs/")
os.system("mv "+args[0][:-5]+"_L*.ini ../jobs/")
$$"$$

cwd=os.getcwd()
if options.userid == "":
    founduser=re.match(r"/home/cad/data/([a-z]+)/.*",os.getcwd()+"/")
    if founduser == None:
        raise RuntimeError("no user name found, please use the -u option")
    user=founduser.groups()[0]
    print "Username found, using: " + user
else:
    user=options.userid
    
#try:
tar=tarfile.open(args[0],mode='r:bz2')
tempdir=tempfile.mkdtemp()
print "Temp. directory: "+tempdir
print "Extracting all files"
for member in tar:
    tar.extract(member,tempdir)
#tar.extractall(tempdir)
tar.close()
os.chdir(tempdir)
files=glob.glob("*.cinc")

print "Fracturing %d files"%len(files)
for f in files:
    os.system("cats %s"%f)
    #    call(["cats","convert.cinc"])
os.system("writefile *.cflt") ##TODO: -f or something to omit user interaction?

tar=tarfile.open(args[0][:-5]+".nwcj",mode="w:bz2")
files = glob.glob("*.gpf")
for f in files:
	tar.add(f)
files = glob.glob("*.ini")
for f in files:
	tar.add(f)
cjobFile=args[0][:-5]+".cjob"
tar.add(cjobFile)	
tar.close()
string=getScript()
f=open("nwcp_unpack","w")
f.write(string)
f.close()
os.system("ebeam_transfer " +args[0][:-5]+".nwcj "+user)
os.system("ebeam_transfer nwcp_unpack "+user)
os.chdir(cwd)
print "removing temp. directory: "+tempdir
shutil.rmtree(tempdir)
#except Exception,exc:
#    os.chdir(cwd)
#    try:
#	pass
#        shutil.rmtree(tempdir)
#    except:
#        pass
#    raise RuntimeError(exc)
"""
    string,n=re.subn(r"\$\$\"\$\$","\"\"\"",string)
    return string

def get_nwcp_convert_lb():
    string = """#!/usr/bin/python
#===============================================================================
# This tool helps to automatically convert *.nwco files created by GUIContact
# to cjob and gpf files, which are autoamtically transferred to the EBEAM.
# IMPORTANT: This tool uses LayoutBeamer, if you want to use CATS use 
#            nwcp_convert.
# At the ebeam computer the tool nwcp_unpack helps to avoid chaos...
# 
# Copyright Daniel Rueffer, EPFL 2012
#===============================================================================
import tarfile
from optparse import OptionParser
import tempfile
import os
import glob
import shutil
import re
from sys import argv as sysargv

usage = "usage: %prog [options] FILE"
parser = OptionParser(usage=usage)
parser.add_option("-u", "--user", dest="userid",default="",
                  help="use specific userid", metavar="USER")
(options, args) = parser.parse_args()

if len(args)!=1:
    raise ValueError("not enough arguments")

def getScript():
    return $$"$$#!/usr/bin/python

from optparse import OptionParser
import tarfile
import os

usage = "usage: %prog [options] FILE"
parser = OptionParser(usage=usage)

(options, args) = parser.parse_args()

if len(args)!=1:
    raise ValueError("not enough arguments")


tar=tarfile.open(args[0],mode="r:bz2")
for member in tar:
    tar.extract(member)
tar.close()
os.system("mv "+args[0][:-5]+".cjob ../jobs/")
os.system("mv "+args[0][:-5]+"_L*.ini ../jobs/")
$$"$$

cwd=os.getcwd()
if options.userid == "":
    founduser=re.match(r"/home/lb/users/([a-z]+)/.*",os.getcwd()+"/")
    if founduser == None:
        raise RuntimeError("no user name found, please use the -u option")
    user=founduser.groups()[0]
    print "Username found, using: " + user
else:
    user=options.userid
    
#try:
tar=tarfile.open(args[0],mode='r:bz2')
tempdir=tempfile.mkdtemp()
print "Temp. directory: "+tempdir
print "Extracting all files"
for member in tar:
    tar.extract(member,tempdir)
#tar.extractall(tempdir)
tar.close()
os.chdir(tempdir)
files=glob.glob("*.ftxt")
print "Fracturing %d files, using lb"%len(files)
for n,f in enumerate(files):
    os.system("lb %s"%f)
    print "---------------------------------"
    print "-----       Done %.1f %%  --------"%(((n*100.)/len(files)))
    print "---------------------------------"

tar=tarfile.open(args[0][:-5]+".nwcj",mode="w:bz2")
files = glob.glob("*.gpf")
for f in files:
	tar.add(f)
files = glob.glob("*.ini")
for f in files:
	tar.add(f)
cjobFile=args[0][:-5]+".cjob"
tar.add(cjobFile)	
tar.close()
string=getScript()
f=open("nwcp_unpack","w")
f.write(string)
f.close()
os.system("ebeam_transfer " +args[0][:-5]+".nwcj "+user)
os.system("ebeam_transfer nwcp_unpack "+user)
os.chdir(cwd)
print "removing temp. directory: "+tempdir
shutil.rmtree(tempdir)
#except Exception,exc:
#    os.chdir(cwd)
#    try:
#	pass
#        shutil.rmtree(tempdir)
#    except:
#        pass
#    raise RuntimeError(exc)
"""
    string,n=re.subn(r"\$\$\"\$\$","\"\"\"",string)
    return string
#            
#            
#a=ContactProject()
#a.addImage(r'/home/drueffer/Desktop/366F0467.JPG')
#print a.fit()
#print a.getLayers()
#a.save("test.nwcpr")
#a.load("test.nwcpr")
#a.export("tempGDS.gds",fileType="GDS")
