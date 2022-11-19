# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 20:50:04 2022

@author: Matei Ionescu
"""

import random
from PIL import Image
import numpy as np


land = ["grassland", 
        "sand", 
        "dunes", 
        "trees",
        "forest",
        "deepWood",
        "hills",
        "mountains",
        "swamp",
        "jungle",
        "lake",
        "tundra"]
water = ["seaIce",
         "coast",
         "ocean",
         "deepOcean"]
colors = {
        "grassland":[64,255,0], 
        "sand":[255,255,100], 
        "dunes":[160,160,63], 
        "trees":[0,180,0],
        "forest":[0,90,0],
        "deepWood":[0,30,0],
        "hills":[128,128,128],
        "mountains":[36,36,36],
        "coast":[40,120,180],
        "ocean":[0,60,110],
        "deepOcean":[0,30,55],
        "swamp":[35,80,20],
        "jungle":[30,60,0],
        "tundra":[0,255,155],
        "seaIce":[255,255,255],
        "lake":[0,35,255],
        "none":[255,0,0]
    }

#count the number of states that are possible
def getPossibilities(ls):
    pos = 0
    for i in ls.values():
        if bool(i):
            pos+=1
    return pos

#emergency reset a tile then update adjacent tiles to reacquire its restrictions
def reset(wo,x,y,size):
    t = wo[x][y]
    wo[x][y]=tile(t.hot,t.cold)
    
    if x+1 <size:
        wo=update(wo,x+1,y,size)
    if x-1>=0:
        wo=update(wo,x-1,y,size)
    if y+1 <size:
        wo=update(wo,x,y+1,size)
    if y-1 >=0:    
        wo=update(wo,x,y-1,size)
    
    return wo
    

#each tile has these attributes 
class tile:
    def __init__(self, isHot, isCold):
        self.collapsed="none"
        if isHot:
            self.states = {
                "grassland":True, 
                "sand":True, 
                "dunes":True, 
                "trees":True,
                "forest":True,
                "deepWood":False,
                "hills":True,
                "mountains":True,
                "coast":True,
                "ocean":True,
                "deepOcean":False,
                "swamp":True,
                "jungle":True,
                "tundra":False,
                "seaIce":False,
                "lake":False
            }
        elif isCold:
            self.states = {
                "grassland":True, 
                "sand":False, 
                "dunes":False, 
                "trees":True,
                "forest":True,
                "deepWood":False,
                "hills":True,
                "mountains":True,
                "coast":True,
                "ocean":True,
                "deepOcean":False,
                "swamp":False,
                "jungle":False,
                "tundra":True,
                "seaIce":True,
                "lake":True
            }
        else:
            self.states = {
                "grassland":True, 
                "sand":False, 
                "dunes":False, 
                "trees":True,
                "forest":True,
                "deepWood":True,
                "hills":True,
                "mountains":True,
                "coast":True,
                "ocean":True,
                "deepOcean":True,
                "swamp":True,
                "jungle":False,
                "tundra":False,
                "seaIce":False,
                "lake":True
            }
        self.weights = {}
        self.cold = isCold
        self.hot = isHot
        self.possibilities = getPossibilities(self.states)
        
        
#world dimensions
# [0][0] ---------------- [size][0]
# |    \                      |
# |       \                   |
# |           \               |
# |               \           |
# |                  \        |
# |                     \     |
# [0][size] ------------ [size][size]
        
        
#creates and returns an empty 2-D array of tiles
def initWorld(size,percentCold,percentHot):
    w = []
    for i in range(size):
        col = []
        for j in range(size):
            new = None
            #north and south poles
            if(j<=(size*(percentCold/2)) or j>=(size-(size*(percentCold/2)))):
                new=tile(False,True)
            #equator
            elif(j<=((size/2)+(size*(percentHot/2))) and j>=((size/2)-(size*(percentHot/2)))):
                new=tile(True,False)
            #the rest
            else:
                new=tile(False,False)
            col.append(new)
        w.append(col)
    return w

#collapse the uncertainty to a single state
def collapse(t):
    assert(isinstance(t, tile))
    
    r = None
    testing = []
    success= False
    if len(t.weights.keys())!=0:
        for k in t.weights.keys():
            if bool(t.states.get(k)):
                for n in range(int(t.weights.get(k))):
                    testing.append(k)
                    success=True
           
    if success:
        r = random.randint(0, len(testing)-1)     
        t.collapsed= testing[r]
            
    else:
        if t.possibilities<2:
            r=0    
        else:
            r = random.randint(0, t.possibilities-1)
        cur = 0
        
        for i in t.states.keys():
            if bool(t.states.get(i)):
                if cur==r:
                    t.collapsed = i
                    break
                elif cur>r:
                    t.collapsed="none"
                    break
                else:
                    cur+=1
    return t
              
#update a single tile's superposition
def single_update(t,ls):
    if("all" in ls.keys()):
        t.possibilities=getPossibilities(t.states)
        return t
    
    for k in ls.keys():
        if k not in t.weights.keys():
            t.weights[k]=ls.get(k)
        else:
            t.weights[k]=ls.get(k) + t.weights.get(k)
    
    #the list "ls" provided contains superpositions that are allowable
    #any states not in that list should be removed from the superposition
    for i in t.states.keys():
        if bool(t.states.get(i)) and (i not in ls.keys()):
            t.states[i]=False
    t.possibilities=getPossibilities(t.states)
    return t
               

collapse_next = []

#update a collapsed tile's adjacent tiles
#each dictionary key is a possible superposition of the adjacent states
#the value of each key in the dictionary is the weight-- a heigher weight means a greater proportion of tiles will collapse to that state
def update(wo,x,y,size):
    assert(type(x)==int and type(y)==int and x in range(size) and y in range(size))
    
    current = wo[x][y].collapsed
    
    for i in range(-1,2):
        for j in range(-1,2):
            if((not (i==0 and j==0)) and (i==0 or j==0)):
                if(x+i in range(size) and y+j in range(size)):
                    if current=="mountain":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"mountain":10,"hills":4,"coast":1,"ocean":1,"sand":2,"dunes":2})
                    elif current == "grassland":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"grassland":14,"hills":1,"sand":1,"trees":4,"swamp":2,"lake":2,"tundra":1,"coast":1,"jungle":2})
                    elif current == "sand":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"sand":15,"grassland":3,"dunes":5,"coast":5,"mountain":2})
                    elif current == "dunes":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"dunes":9,"sand":7,"mountain":2})
                    elif current == "trees":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"trees":15,"grassland":4,"forest":6,"tundra":2,"lake":3})
                    elif current == "forest":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"forest":6,"trees":3,"deepWood":3})
                    elif current == "deepWood":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"deepWood":2,"forest":1})
                    elif current == "hills":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"hills":8,"mountain":2,"grassland":2,"trees":3,"tundra":1})
                    elif current == "coast":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"coast":11,"sand":4,"swamp":4,"mountain":3,"tundra":3,"ocean":2,"grassland":5,"seaIce":1})
                    elif current == "ocean":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"ocean":9,"coast":8,"deepOcean":1,"seaIce":10,"mountain":6})
                    elif current == "deepOcean":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"deepOcean":1,"ocean":5,"seaIce":10})
                    elif current == "swamp":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"swamp":5,"grassland":4,"coast":1})
                    elif current == "jungle":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"jungle":2,"coast":1,"grassland":1})
                    elif current == "tundra":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"tundra":8,"coast":2,"grassland":1,"trees":3,"hills":2})
                    elif current == "seaIce":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"seaIce":11,"deepOcean":1,"ocean":5,"coast":5})
                    elif current == "lake":
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"lake":5,"trees":2,"grassland":3})
                    else:
                        wo[x+i][y+j]=single_update(wo[x+i][y+j],{"all":1})
        
                    
                    #these tiles will have lower-energy superpositions than the rest 
                    #set them aside to collapse first
                    here = [x+i,y+j]
                    if here not in collapse_next:
                        collapse_next.append(here)

    #attempt to disallow coasts acting like lakes
    # if x+1 <size and x-1 >=0:
    #     if current in water and wo[x+1][y].collapsed in land:
    #         for w in water:
    #             wo[x-1][y].states[w]=False
    #     elif current in water and wo[x-1][y].collapsed in land:
    #         for w in water:
    #             wo[x+1][y].states[w]=False
            
    # if y-1 >=0 and y+1<size:
    #     if current in water and wo[x][y+1].collapsed in land:
    #         for w in water:
    #             wo[x][y-1].states[w]=False
    #     elif current in water and wo[x][y-1].collapsed in land:
    #         for w in water:
    #             wo[x][y+1].states[w]=False
    
    return wo
                        
    
#poll the constant colors dictionary to convert tiles to rgb arrays
def output(ls):
    output = []
    for i in ls:
        for j in i:
            output.append(colors.get(j.collapsed))
    return output
        
        
        
if __name__=="__main__":
    
    #version control
    f = open("log.txt","r")
    name="1"
    
    if f:
        name = f.read()
        f.close()
    
    if name=="":
        name="1"
    
    f = open("log.txt","w")
    f.write(str(int(name)+1))
    f.close()
    
    f = open("dnd_wavefunctioncollapse_mapmaker.py","r")
    thisFile = f.read()
    f.close()
    
    f = open("./versions/"+name+"_wfc_mm.py","w")
    f.write(thisFile)
    f.close()
    
    
    
    
    
    #size
    magnitude = 100
    theWorld = initWorld(magnitude,0.2,0.2)
    
    for i in range(magnitude):
        for s in land:
            theWorld[0][i].states[s]=False
            theWorld[i][0].states[s]=False
            theWorld[magnitude-1][i].states[s]=False
            theWorld[i][magnitude-1].states[s]=False
            
        theWorld[0][i]=collapse(theWorld[0][i])
        theWorld[i][0]=collapse(theWorld[i][0])
        theWorld[magnitude-1][i]=collapse(theWorld[magnitude-1][i])
        theWorld[i][magnitude-1]=collapse(theWorld[i][magnitude-1])
        
        theWorld = update(theWorld,0,i,magnitude)  
        theWorld = update(theWorld,i,0,magnitude)  
        theWorld = update(theWorld,magnitude-1,i,magnitude)  
        theWorld = update(theWorld,i,magnitude-1,magnitude)  
            
            
    
    #choose a random tile to collapse first
    r1 = random.randint(0,magnitude-1)
    r2 = random.randint(0,magnitude-1)
    
    theWorld[r1][r2]=collapse(theWorld[r1][r2])
    theWorld = update(theWorld,r1,r2,magnitude)              
    
    resets=0
    it = 0
    print("Working: ")
    while(True):
        if len(collapse_next)>0:
            minPos = 999
            for nx in collapse_next:
                if theWorld[nx[0]][nx[1]].collapsed=="none" and theWorld[nx[0]][nx[1]].possibilities<minPos:
                    minPos=theWorld[nx[0]][nx[1]].possibilities
            
            if minPos==999:
                collapse_next.clear()
                continue
            
            for nx in collapse_next:
                if theWorld[nx[0]][nx[1]].collapsed=="none" and theWorld[nx[0]][nx[1]].possibilities==minPos:
                    r1=nx[0]
                    r2=nx[1]
                    collapse_next.remove(nx)
                    break
        else:
            #brute force find another tile to collapse: rarely used but here to avoid infinite loops
            done = False
            for i in range(magnitude):
                for j in range(magnitude):
                    if theWorld[i][j].collapsed=="none":
                        r1 = i
                        r2 = j
                        done = True
                    if done:
                        break
                if done:
                    break
            #if no uncollapsed tile was found, we're done
            if not done:
                break
        
        #prove to the user that we're still working and not infinite looping
        if it%250==0:
            print("|",end="")
            if it>=(magnitude**2 + 5*magnitude):
                 break
        it+=1
        
        # #a tile with 0 possibilities cannot be collapsed: reset and pray
        # if theWorld[r1][r2].possibilities==0:
        #     theWorld=reset(theWorld,r1,r2,magnitude)      
        #     resets+=1
        #     if resets%10==0:
        #         print("-",end="")
            
            
        theWorld[r1][r2]=collapse(theWorld[r1][r2])
        theWorld = update(theWorld,r1,r2,magnitude)
        
    
    #create image (don't change any of this: it works fine)
    w, h = 4000, 4000
    data = np.zeros((h, w, 3), dtype=np.uint8)
    x=int(w/magnitude)
    y=int(h/magnitude)
    coloration = output(theWorld)
    
    
    for i in range(magnitude):
        for j in range(magnitude):
            data[j*x:(j+1)*x,i*y:(i+1)*y]=coloration[magnitude*i+j]

                
    img = Image.fromarray(data, 'RGB')
    img.save('./outputs/'+name+'.png')
                              