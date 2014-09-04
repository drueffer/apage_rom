# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 14:23:57 2012

@author: rueffer
"""

from autoDetect import *
import time
import numpy as np


def find(a,min,max):
   minV=0
   for n,i in enumerate(a):
       if i > min:
         minV = n
         break
   for n,i in enumerate(a[minV::]):
       if i > max:
         t=n+minV-1
         return minV,t
         
def find2(a,order):
    l=[]
    s=[]
    m=[]
    for i in range(order):
        l.append(find(a,a[0]*(i+0.9),a[0]*(i+1.1)))
        s.append(np.std(a[l[-1][0]:l[-1][1]]))
        m.append(np.mean(a[l[-1][0]:l[-1][1]])/(i+1))
    all=[]
    for n,i in enumerate(l):
        all.extend((a[i[0]:i[1]+1]/(n+1)).tolist())
    amean=np.mean(all)
    astd=np.std(all)
    return amean,astd,l,s,m
    

fn=r"D:\Measurements\OriginalData\Optical@Z1CMI\p4u-50x.JPG"             
#fn=r"D:\Measurements\OriginalData\Optical@Z1CMI\TestPattern\50x-2u.JPG"
I=ImageObject(fn)
t=[time.time()]
allCircles=I.findAllCircles(minRadius=1)
t.append(time.time())
print "found %d circles in %f milliseconds"%((len(allCircles),(t[-1]-t[-2])*1000))
l=[]
for circle in allCircles:
    l.append([circle.Center[0],circle.Center[1]])
coordinates=np.array(l)
t.append(time.time())
print "array created in %f milliseconds"%((t[-1]-t[-2])*1000)

n=len(coordinates)
distances=np.empty((n*(n-1))/2)
k=0
l=n-1
d=[]
for i in range(n-1):
    distances[k:k+l]=np.sqrt((coordinates[-(i+1),0]-coordinates[0:-(i+1),0])**2+(coordinates[-(i+1),1]-coordinates[0:-(i+1),1])**2)
#    d.extend(np.sqrt((coordinates[-(i+1),0]-coordinates[0:-(i+1),0])**2+(coordinates[-(i+1),1]-coordinates[0:-(i+1),1])**2).tolist())
    k+=l
    l-=1
t.append(time.time())
print "distances calculated  in %f milliseconds"%((t[-1]-t[-2])*1000)

sortIndices=np.argsort(distances)
sortedDist=distances[sortIndices]


amean,astd,l,s,m=find2(sortedDist,5)


t.append(time.time())
print "mean distance calculated  in %f milliseconds"%((t[-1]-t[-2])*1000)

n=len(coordinates)
vectors=np.empty(((n*(n-1))/2,2))
k=0
l=n-1
d=[]
for i in range(n-1):
    vectors[k:k+l]=coordinates[-(i+1)]-coordinates[0:-(i+1)]
    k+=l
    l-=1
t.append(time.time())
print "vectors calculated  in %f milliseconds"%((t[-1]-t[-2])*1000)

xvectors=vectors[np.where(np.logical_and(vectors[:,1] > 0,vectors[:,1] < amean/2.))]
xvectors2=(xvectors.T/np.sqrt(xvectors[:,0]**2+xvectors[:,1]**2)).T
temp=xvectors[:,0]>0
xvectors2[:,0]=np.where(temp,xvectors[:,0],xvectors[:,0]*(-1.))
xvectors2[:,1]=np.where(temp,xvectors[:,1],xvectors[:,1]*(-1.))

t.append(time.time())
print "xvectors calculated  in %f milliseconds"%((t[-1]-t[-2])*1000)