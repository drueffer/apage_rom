# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 17:22:04 2012

@author: rueffer

Defaults for some settings
"""
from matplotlib.cm import jet
from numpy import floor

Descriptor=[
#("markerArea",(200,200))
]
        
        
# tuples: (layer,color[r,g,b],alpha)
colorMap=[
(0,[0,128,128],0.1),
(1,[128,128,224],0.1),
(2,[96,224,96],0.1),
(3,[240,210,85],0.1),
(4,[220,75,202],0.1),
(100,[0,38,255],0.1),
(101,[255,0,0],0.05)
]
#colorMap=[]
#for i in range(100):
#    j=i*1.1
##    m=jet(j/8.)[0:3]
#    m=jet(j/8.-floor(j/8.))[0:3]
#    print (j/8.-floor(j/8.)),m
#    colorMap.append([i,[m[j]*255 for j in range(3)],0.1])
#    
#colorMap.append((100,[0,38,255],0.1))
#colorMap.append((101,[255,0,0],0.1))
