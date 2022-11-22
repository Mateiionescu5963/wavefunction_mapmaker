# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 20:50:04 2022

@author: Matei Ionescu
"""

import random
from PIL import Image
import numpy as np
import math


land = ["grassland", 
        "sand", 
        "dunes", 
        "trees",
        "forest",
        "deepWood",
        "hills",
        "mountain",
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
        "mountain":[225,110,0],
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
                "deepWood":True,
                "hills":True,
                "mountain":True,
                "coast":True,
                "ocean":True,
                "swamp":False,
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
                "mountain":True,
                "coast":True,
                "ocean":True,
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
                "mountain":True,
                "coast":True,
                "ocean":True,
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
                if int(t.weights.get(k))>0:
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
            
    # if t.hot:
    #     if "grassland" not in t.weights.keys():        
    #         t.weights["grassland"]=-10
    #     else:
    #         t.weights["grassland"]=t.weights.get("grassland")-10
    # elif t.cold:
    #     if "tundra" not in t.weights.keys():
    #         t.weights["tundra"]=10
    #     else:
    #         t.weights["tundra"]=10 + t.weights.get("tundra")
    
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
                if(x+i>=0 and x+i<size and y+j>=0 and y+j<size):
                    if wo[x+i][y+j].collapsed=="none":
                        if current=="mountain":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"mountain":8,"hills":4,"coast":2,"sand":0,"dunes":3})
                        elif current == "grassland":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"grassland":15,"hills":4,"sand":3,"trees":4,"swamp":4,"coast":3})
                        elif current == "sand":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"sand":4,"grassland":3,"dunes":0,"coast":2,"mountain":0})
                        elif current == "dunes":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"dunes":3,"sand":3,"mountain":0})
                        elif current == "trees":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"trees":9,"grassland":4,"forest":6})
                        elif current == "forest":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"forest":7,"trees":3,"deepWood":3,"hills":2})
                        elif current == "deepWood":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"deepWood":3,"forest":4,"hills":0})
                        elif current == "hills":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"hills":5,"mountain":0,"grassland":3,"trees":3})
                        elif current == "swamp":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"swamp":5,"grassland":0,"coast":4})
                        elif current == "coast":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"coast":0,"sand":0,"swamp":0,"mountain":0,"ocean":4,"grassland":0})
                        elif current == "ocean":
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"ocean":14,"coast":14})
                        else:
                            wo[x+i][y+j]=single_update(wo[x+i][y+j],{"all":1})
            
                        
                        #these tiles will have lower-energy superpositions than the rest 
                        #set them aside to collapse first
                        here = [x+i,y+j]
                        if here not in collapse_next:
                            collapse_next.append(here)

    
    return wo
                        
    
    
def findBlob(wo,x,y,size,name,tileset):
    blob = True
    checked = []
    non = []
    
    checked.append((x,y))
    
    while(True):
        adjacents = []
        for pair in checked:
            for i in range(-1,2):
                for j in range(-1,2):
                    if((not (i==0 and j==0)) and (i==0 or j==0)):
                        nPair = (pair[0]+i,pair[1]+j)
                        if nPair[0]<0 or nPair[0]>=size or nPair[1]<0 or nPair[1]>=size:
                            blob = False
                        else:
                            if nPair not in checked and nPair not in non and nPair not in adjacents:
                                adjacents.append(nPair)
        
        
        if len(adjacents)==0:
            break
        
        for a in adjacents:
            if not wo[a[0]][a[1]].collapsed==name and wo[a[0]][a[1]].collapsed in tileset:
                blob=False
                non.append(a)
            elif wo[a[0]][a[1]].collapsed==name:
                checked.append(a)
            else:
                non.append(a)
            
    return (checked,blob)
    
    
    
    
def blobfinding(wo,size,name,tileset):
    print("Blobfinding Enabled and Running:")
    blobs = []
    checked = []
    it = 0
    for i in range(1,size-1):
        for j in range(1,size-1):
            if (i,j) not in checked:
                if wo[i][j].collapsed==name:
                    it+=1
                    if it%int(size)==0:
                        print("|",end="")
                    b=findBlob(wo,i,j,size,name,tileset)
                    for c in b[0]:
                        checked.append(c)
                    if b[1]:
                        for pair in b[0]:
                            blobs.append(pair)
                                            
    
    for bl in blobs:
        wo[bl[0]][bl[1]].collapsed="none"
        
    for bl in blobs:
        wo=reset(wo,bl[0],bl[1],size)
        wo[bl[0]][bl[1]].states[name]=False
        wo[bl[0]][bl[1]]=collapse(wo[bl[0]][bl[1]])
        
    print("")
        
    return wo
                        
        
    
    
#poll the constant colors dictionary to convert tiles to rgb arrays
def output(ls):
    output = []
    for i in ls:
        for j in i:
            output.append(colors.get(j.collapsed))
    return output


def get_adj(wo,x,y,size):
    adj = []
    for i in range(-1,2):
        for j in range(-1,2):
            if((not (i==0 and j==0)) and (i==0 or j==0)):
                if x+i>=0 and x+i<size and y+j>=0 and y+j<size:
                    if not wo[x+i][y+j].collapsed=="none":
                        adj.append((x+i,y+j))
    
    return adj

def collapse_to_adj(wo,x,y,size):
    adj = get_adj(wo, x, y, size)
                    
    r = random.randint(0,len(adj)-1)
    wo[x][y].collapsed=wo[adj[r][0]][adj[r][1]].collapsed
    
    return wo
                
        
        
        
if __name__=="__main__":
    #RUNTIME VARIABLES:
    #size
    magnitude = 160    
    #do blobfinding algorithm after generation?
    do_post_processing = True
    
    do_coast_blobfind = True
    do_island_blobfind = False
    #float value percentages (each must be in range [0,0.5])
    percentCold = 0.2
    percentHot = 0.2
    
    
    
    #version control
    f = None
    name = None
    try:
        f = open("log.txt","r")
        name = f.read()
        f.close()
    except FileNotFoundError:
        name = "1"
    
    if name=="":
        name="1"
    else:
        name = str(int(name)+1)
    
    f = open("log.txt","w")
    f.write(name)
    f.close()
    
    f = open("rippleOut_collapse.py","r")
    thisFile = f.read()
    f.close()
    
    name = name+"_roc"
    
    f = open("./versions/"+name+"_wfc_mm.py","w")
    f.write(thisFile)
    f.close()
    
    
    
    
    
    
    theWorld = initWorld(magnitude,percentCold,percentHot)
    
    for i in range(magnitude):
        for j in [0]:
            for s in land:
                theWorld[j][i].states[s]=False
                theWorld[i][j].states[s]=False
                theWorld[magnitude-j-1][i].states[s]=False
                theWorld[i][magnitude-j-1].states[s]=False
                
            # theWorld[j][i]=collapse(theWorld[j][i])
            # theWorld[i][j]=collapse(theWorld[i][j])
            # theWorld[magnitude-j-1][i]=collapse(theWorld[magnitude-j-1][i])
            # theWorld[i][magnitude-j-1]=collapse(theWorld[i][magnitude-j-1])
            
            # theWorld = update(theWorld,j,i,magnitude)  
            # theWorld = update(theWorld,i,j,magnitude)  
            # theWorld = update(theWorld,magnitude-j-1,i,magnitude)  
            # theWorld = update(theWorld,i,magnitude-j-1,magnitude)  
            
            
    for i in range(int(math.sqrt(magnitude))):
        r1 = random.randint(1,magnitude-2)
        r2 = random.randint(1,magnitude-2)
        while(not theWorld[r1][r2].collapsed=="none"):
            r1 = random.randint(1,magnitude-2)
            r2 = random.randint(1,magnitude-2)
            
        for s in theWorld[r1][r2].states.keys():
            if s not in ["deepWood","mountain","grassland","dunes"]:
                theWorld[r1][r2].states[s]=False
            
    
        theWorld[r1][r2]=collapse(theWorld[r1][r2])
        theWorld = update(theWorld,r1,r2,magnitude)              
    
    
    try:
        resets=0
        it = 0
        skips = []
        print("Working: ")
        checkI=0
        while(True):
            if len(collapse_next)>0:
                minPos = 999
                choose = []
                chooseLand = []
                cl = False
                
                for nx in collapse_next:
                    if theWorld[nx[0]][nx[1]].collapsed=="none" and not theWorld[nx[0]][nx[1]].possibilities==0:
                        adj = get_adj(theWorld, nx[0], nx[1], magnitude)
                        for a in adj:
                            if theWorld[nx[0]][nx[1]].collapsed in land:
                                cl = True
                                chooseLand.append(nx)
                                break
                
                if not cl:
                    for nx in collapse_next:
                        if theWorld[nx[0]][nx[1]].collapsed=="none" and not theWorld[nx[0]][nx[1]].possibilities==0 and theWorld[nx[0]][nx[1]].possibilities<minPos:
                            minPos=theWorld[nx[0]][nx[1]].possibilities
                            choose.clear()
                            choose.append(nx)
                        elif theWorld[nx[0]][nx[1]].collapsed=="none" and not theWorld[nx[0]][nx[1]].possibilities==0 and theWorld[nx[0]][nx[1]].possibilities==minPos:
                            choose.append(nx)
                else:
                    for nx in chooseLand:
                        if theWorld[nx[0]][nx[1]].collapsed=="none" and not theWorld[nx[0]][nx[1]].possibilities==0 and theWorld[nx[0]][nx[1]].possibilities<minPos:
                            minPos=theWorld[nx[0]][nx[1]].possibilities
                            choose.clear()
                            choose.append(nx)
                        elif theWorld[nx[0]][nx[1]].collapsed=="none" and not theWorld[nx[0]][nx[1]].possibilities==0 and theWorld[nx[0]][nx[1]].possibilities==minPos:
                            choose.append(nx)
                
                if minPos==999:
                    collapse_next.clear()
                    continue
                
                
                rChoose = None
                if len(choose)==1:
                    rChoose=0
                else:
                    rChoose = random.randint(0,len(choose)-1)
                    
                r1 = choose[rChoose][0]
                r2 = choose[rChoose][1]
                collapse_next.remove(choose[rChoose])

            else:
                #brute force find another tile to collapse: rarely used but here to avoid infinite loops
                if it%int(magnitude*4)==0:
                    print(">",end="")
                done = False
                for i in range(magnitude):
                    for j in range(magnitude):
                        if i>=checkI:
                            if theWorld[i][j].collapsed=="none" and (i,j) not in skips:
                                checkI=i
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
            if it%int(magnitude*4)==0:
                print("|",end="")
                if it>=(magnitude**3 + 10*magnitude):
                      break
            it+=1
            
            # #a tile with 0 possibilities cannot be collapsed: reset and pray
            if theWorld[r1][r2].possibilities==0:
                if getPossibilities(theWorld[r1][r2].states)==0:
                    theWorld=reset(theWorld,r1,r2,magnitude)     
                    skips.append((r1,r2))
                    resets+=1
                    if resets%10==0:
                        print("-",end="")
                
                
            theWorld[r1][r2]=collapse(theWorld[r1][r2])
            theWorld = update(theWorld,r1,r2,magnitude)
            
          
            
          
        #buff out local minimums
        for s in skips:
            theWorld = collapse_to_adj(theWorld,s[0],s[1],magnitude)
                    
        
        
        print("")
        
        if do_post_processing:
            if do_coast_blobfind:
                print("Coast-in-land ",end="")
                theWorld=blobfinding(theWorld,magnitude,"coast",water)
            
            if do_island_blobfind:
                print("Excessive Island ",end="")
                theWorld=blobfinding(theWorld,magnitude,"grassland",land)
            #last pass
            print("Running Last-Pass cleanup routine",end="")
            for i in range(magnitude):
                for j in range(magnitude):
                    if theWorld[i][j].collapsed=="none":
                        theWorld = collapse_to_adj(theWorld,i,j,magnitude)   
                    elif theWorld[i][j].collapsed=="coast":
                        adj = get_adj(theWorld, i, j, magnitude)
                        nnil = 0
                        for a in adj:
                            if theWorld[a[0]][a[1]].collapsed not in land:
                                nnil+=1
                        if nnil==len(adj):
                            if theWorld[i][j].cold:
                                nnilr = random.randint(0,1)
                                if nnilr==0:
                                    theWorld[i][j].collapsed="seaIce"
                                else:
                                    theWorld[i][j].collapsed="ocean"
                            else:
                                theWorld[i][j].collapsed="ocean"
                    elif theWorld[i][j].collapsed=="ocean":
                        adj = get_adj(theWorld, i, j, magnitude)
                        brk = False
                        for a in adj:
                            if theWorld[a[0]][a[1]].collapsed in land:
                                theWorld[i][j].collapsed="coast"
                                brk = True
                                break
                            
                        if not brk and theWorld[i][j].cold:
                            sir = random.randint(0,1)
                            if sir==0:
                                theWorld[i][j].collapsed="seaIce"

                            
                    # elif theWorld[i][j].collapsed=="lake":
                    #     adj = get_adj(theWorld, i, j, magnitude)
                    #     for a in adj:
                    #         if theWorld[a[0]][a[1]].collapsed in water:
                    #             theWorld[i][j].collapsed="grassland"
                    #             break
                                
                    if theWorld[i][j].cold and theWorld[i][j].collapsed=="grassland":
                        theWorld[i][j].collapsed="tundra"
                    elif theWorld[i][j].hot and theWorld[i][j].collapsed=="deepwood":
                        theWorld[i][j].collapsed="jungle"
                if i%int(magnitude/3)==0:
                    print(".",end="")
                    
        print("")
                    
        
        
    except KeyboardInterrupt:
        pass
    
    
        
    
    #save outputs 
    f = open("./outputs/"+name+".txt","w")
    for i in range(magnitude):
        for j in range(magnitude):
            f.write(theWorld[j][i].collapsed+" ")
        f.write("\n\n")
    f.close()
    
    
    #esoteric image creation magic; (don't change any of this: it works fine and it would be best if it stayed that way)
    w, h = 6400, 6400
    data = np.zeros((h, w, 3), dtype=np.uint8)
    x=int(w/magnitude)
    y=int(h/magnitude)
    coloration = output(theWorld)
    
    
    for i in range(magnitude):
        for j in range(magnitude):
            data[j*x:(j+1)*x,i*y:(i+1)*y]=coloration[magnitude*i+j]

                
    img = Image.fromarray(data, 'RGB')
    img.save('./outputs/'+name+'.png')
    
    print(name+".txt and .png files created\nDONE!!!")
                              