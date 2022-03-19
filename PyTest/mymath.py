
import math
def mod(x,y):
    return math.sqrt(x**2+y**2)

def LDVS(vold,vnew,n):
    return (vold*n+vnew)/(n+1)

def GetPlayer2BaseDistance(player,base):
    return  mod(base['x']-player['x'], base['y']-player['y'])
