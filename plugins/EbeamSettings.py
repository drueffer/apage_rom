# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 16:13:43 2013

@author: rueffer

EXAMPLE:
-------------------------------------------------------------------
defExposureSettings={"beam":"150nA","dose":1100,"res":0.025,
                  "alpha":0,"beta":31.,"eta":0.65,"ignoreHeightError":False,
                  "doPEC":True,"camps":0}
beams={
    "100nA":"100na_300um.beam_100",
    "150nA":"150na_300um.beam_100"
    }

beamsizes={
    "150nA":0.075,
    "100nA":0.050,
    }
minRes=0.001
maxRes=0.050
-------------------------------------------------------------------
"""

defExposureSettings={"beam":"150nA","dose":1100.,"res":0.025,"mPEC_beamsize":0.1,
                  "alpha":0,"beta":31.,"eta":0.65,"ignoreHeightError":False,
                  "doPEC":False,"camps":0,"multiPEC":False,"negativeMarker":False}
beams={
    "100nA":"100na_300um.beam_100",
    "100pA":"100pa_300um.beam_100",
    "10nA":"10na_300um.beam_100",
    "150nA":"150na_300um.beam_100",
    "15nA":"15na_300um.beam_100",
    "1nA":"1na_300um.beam_100",
    "200nA":"200na_300um.beam_100",
    "200pA":"200pa_300um.beam_100",
    "20nA":"20na_300um.beam_100",
    "2nA":"2na_300um.beam_100",
    "30nA":"30na_300um.beam_100",
    "3nA":"3na_300um.beam_100",
    "40nA":"40na_300um.beam_100",
    "500pA":"500pa_300um.beam_100",
    "50nA":"50na_300um.beam_100",
    "5nA":"5na_300um.beam_100",
    "700pA":"700pa_300um.beam_100",
    "70nA":"70na_300um.beam_100",
    "7nA":"7na5_300um.beam_100"
    }

beamsizes={
    "200nA":0.100,
    "150nA":0.075,
    "100nA":0.050,
    "70nA":0.038,
    "40nA":0.020,
    "20nA":0.015,
    "10nA":0.009,
    }
defExposureSettings.update({"beamsize":beamsizes[defExposureSettings["beam"]]}) 
    
#MSF for LB: not sure what this is, but it has to be specified correctly
MSF={
    0.1:(13,205),
    0.75:(10,154),
    0.05:(7,103),
    0.025:(4,52),
    0.020:(3,41),
    0.015:(2,31),
    0.010:(2,21),
    }
defExposureSettings.update({"MSF":MSF[defExposureSettings["res"]]}) 

minRes=0.001
maxRes=0.100

defExposureSettings.update({"PECLayers":[0]}) 