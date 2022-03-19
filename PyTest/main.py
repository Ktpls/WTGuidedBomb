'''
########################
configuration
########################
'''
ROUGH_GUIDING_INTERVAL=5
PRECISE_GUIDING_INTERVAL=0.1
YERROR_DROP_BOMB_LIMIT=125
DISTANCE_TO_LAUCHING_PRECISE_GUIDING=0.15

SERVER_RESPONSIVE_MODE=100
SERVER_LOW_COST_MODE=1000

ACTION_INTERVAL=0.25
BOMBING_RETRY_CHECK_INTERVAL=10
BOMBING_RETRY_DISTANCE=0.20

Climb4Bombing_CONTROL_INTERVAL=5
AFK_CONTROL_INTERVAL=10

'''
########################
plane related
########################
'''
HEIGHT_CONTROL_SAFE_CLIMB_RATE=15
BOMBING_ALT=4000
AFK_ALT=10000
class DropBombActionConfig_SM81:
    def __init__(self):
        self.stage=0
        self.stagemax=4

    def HaveBombLeft(self):
        return self.stage<self.stagemax

    def DropBombPrepare(self):
        print('preparing for boming')
        CallCommand(cons['setresponsetime'], SERVER_RESPONSIVE_MODE)
    
        CallCommand(cons['keydown'],162) #ctrl
        delay(ACTION_INTERVAL)

        CallCommand(cons['keypress'],115) #f4
        delay(ACTION_INTERVAL)

        CallCommand(cons['keyup'],162) #ctrl
        delay(1)

        CallCommand(cons['mousepress'],1) #rightclick
        delay(ACTION_INTERVAL)

        CallCommand(cons['keypress'],192) #~
        delay(ACTION_INTERVAL)

        ##set to 2,4,8,16
        #for i in range(4):
        #    CallCommand(cons['keypress'],53) #5
        #    delay(ACTION_INTERVAL)

    def DropBombDone(self):
        print('bomb done')
        CallCommand(cons['setresponsetime'], SERVER_LOW_COST_MODE)

        CallCommand(cons['keypress'],113) #f2
        delay(ACTION_INTERVAL)

        ##set to S, N
        #for i in range(4):
        #    CallCommand(cons['keypress'],53) #5
        #    delay(ACTION_INTERVAL)

    def DropBomb(self):
        #CallCommand(cons['keydown'],90) #Z
        #delay(1)
        #CallCommand(cons['keyup'],90)
        
        CallCommand(cons['keypress'],keys['Space'])
        self.stage+=1
class DropBombActionConfig_B18B:
    def __init__(self):
        self.stage=0
        self.stagemax=2

    def HaveBombLeft(self):
        return self.stage<self.stagemax

    def DropBombPrepare(self):
        print('preparing for boming')

        CallCommand(cons['keypress'],192) #~
        delay(ACTION_INTERVAL)

        CallCommand(cons['setresponsetime'], SERVER_RESPONSIVE_MODE)
    
        CallCommand(cons['keydown'],162) #ctrl
        delay(ACTION_INTERVAL)

        CallCommand(cons['keypress'],115) #f4
        delay(ACTION_INTERVAL)

        CallCommand(cons['keyup'],162) #ctrl
        delay(1)

        CallCommand(cons['mousepress'],1) #rightclick
        delay(ACTION_INTERVAL)

        ##set to 2,4,8,16
        #for i in range(4):
        #    CallCommand(cons['keypress'],53) #5
        #    delay(ACTION_INTERVAL)

    def DropBombDone(self):
        print('bomb done')
        CallCommand(cons['setresponsetime'], SERVER_LOW_COST_MODE)


        CallCommand(cons['keypress'],113) #f2
        delay(ACTION_INTERVAL)

        ##set to S, N
        #for i in range(4):
        #    CallCommand(cons['keypress'],53) #5
        #    delay(ACTION_INTERVAL)

    def DropBomb(self):
        #CallCommand(cons['keydown'],90) #Z
        #delay(1)
        #CallCommand(cons['keyup'],90)
        
        #CallCommand(cons['keypress'],keys['Space'])
        CallCommand(cons['keypress'],32)
        self.stage+=1

planeConfig=DropBombActionConfig_B18B()

import os
import time
import matplotlib.pyplot as plt
from cons import cons,keys
from base import *
from command import *
from mymath import *
from algorithm import *

'''
########################
action layer
########################
'''
#unused
def climbControl(cr):
    ctrlc=pid(1,0,1)
    while(True):
        err=cr-GetClimb()
        CallCommand(cons['mouserelativemove'],0,-int(ctrlc.next(cr-GetClimb())))
        yield err

def limitTo(lim,x):
    if(abs(x)>lim):
        return x*lim/abs(x)
    else:
        return x

class heightControl:
    def __init__(self):
        self.ctrlh=pid(0.5,0,0.5)
        self.ctrlc=pid(1,0,1)

    def next(self,h_tar):
        height=GetHeight()
        climb=GetClimb()
        errh=h_tar-height
        c_tar=limitTo(HEIGHT_CONTROL_SAFE_CLIMB_RATE,self.ctrlh.next(errh))
        CallCommand(cons['mouserelativemove'],0,-int(limitTo(100,self.ctrlc.next(c_tar-climb))))
        
HC=heightControl()
HC_TargetAlt=0

def dropbombprepare():
    planeConfig.DropBombPrepare()


def dropbombdone():
    planeConfig.DropBombDone()

def dropbomb():
    planeConfig.DropBomb()


BOMBING_SUCCEED=0
BOMBING_FAILED=1
BOMBING_RECOVERABLE=2
ROUGH_GUIDING_EPSILON=2 #in degree
def bombing(base):
    
    #rough guiding
    dctrl=pid(3,0,3) #direction control

    while(True):

        #guiding

        #cal direction
        player=GetPlayer()
        dx,dy=base['x']-player['x'], base['y']-player['y']
        crossproduct=player['dx']*dy-player['dy']*dx
        dotproduct=player['dx']*dx+player['dy']*dy
        sintheta=crossproduct/(mod(dx,dy)*mod(player['dx'],player['dy']))
        costheta=dotproduct/(mod(dx,dy)*mod(player['dx'],player['dy']))
        theta=180/3.14159*math.acos(costheta) #use cosine and sine to cal theta
        if(sintheta<0):
            theta=-theta
        print('rough guiding, theta={}'.format(theta))

        #apply
        CallCommand(cons['mouserelativemove'],-int(dctrl.next(0-theta)),0)
        HC.next(HC_TargetAlt)

        #distance:
        #malta,b34,3000m400kph,0.06
        #moscow,b34,3000m400kph,0.035
        print('dist',mod(dx,dy))
        if(mod(dx,dy)<DISTANCE_TO_LAUCHING_PRECISE_GUIDING):
            if(abs(theta)>=ROUGH_GUIDING_EPSILON):
                #too close to adjust
                return BOMBING_RECOVERABLE
            else:
                #lauch precise guiding
                break

        delay(ROUGH_GUIDING_INTERVAL)

    dropbombprepare()

    #precise guiding and trying dropping bomb
    lastP2BDist=GetPlayer2BaseDistance(GetPlayer(),base)
    while(True):
        result=FindBase()
        if(result is not None):

            #cal err and apply
            xerror,yerror=result['x']-XCENTER_OF_SCREEN, -(result['y']-YCENTER_OF_SCREEN)
            movdistance=0.25*xerror
            print('precise guiding, xe={}, ye={}'.format(xerror,yerror))
            CallCommand(cons['mouserelativemove'],int(movdistance),0)

            #close enough
            if(yerror<YERROR_DROP_BOMB_LIMIT):
                dropbomb()
                dropbombdone()
                return BOMBING_SUCCEED
                break

        HC.next(HC_TargetAlt)

        #judge if missed
        dist=GetPlayer2BaseDistance(GetPlayer(),base)
        if(dist>lastP2BDist): #flying away
            dropbombdone()
            return BOMBING_FAILED
        lastP2BDist=dist

        delay(PRECISE_GUIDING_INTERVAL)

def Climb4Bombing():
    global HC_TargetAlt
    HC_TargetAlt=BOMBING_ALT
    while(True):
        HC.next(HC_TargetAlt)
        err=HC_TargetAlt-GetHeight()
        print('Climbing for bombing, herr={}'.format(err))
        if(err<0):
            break
        delay(Climb4Bombing_CONTROL_INTERVAL)

def AFK():
    global HC_TargetAlt
    HC_TargetAlt=AFK_ALT
    while(True):
        HC.next(HC_TargetAlt)
        err=HC_TargetAlt-GetHeight()
        print('AFK, herr={}'.format(err))
        delay(AFK_CONTROL_INTERVAL)

#unused
def setHwnd():
    hWnd=ctypes.windll.user32.FindWindowW('DagorWClass',0)
    print('hwnd=',hex(hWnd))
    CallCommand(cons['sethwnd'],hWnd)


'''
########################
main
########################
'''

def main():
    print('booting up')
    BootUp()

    #side climb
    #CallCommand(cons['mouserelativemove'],500,0)

    #climb
    Climb4Bombing()

    ##no climb
    #global HC_TargetAlt
    #HC_TargetAlt=GetHeight()

    #bomb all base
    basetried=[]
    while(True):
        print('start bombing')
        
        #load base list
        baselist=GetBaseList()
        if(len(baselist)==0):
            return False

        #find a base not tried
        base=None
        for b2b in baselist:
            found=False
            for bt in basetried:
                if(base_eq(b2b,bt)):
                    found=True
                    break
            if(not found):
                base=b2b
                break
        if(base is None):
            print('no base to bomb')
            break
        print('bombing base ', base)


        #bomb and analyze result
        result=bombing(base)
        if(result==BOMBING_SUCCEED):
            print('bomb succeed')
            if(not planeConfig.HaveBombLeft()):
                break
            delay(10) #wait a little bit
        elif(result==BOMBING_FAILED):
            print('bomb failed')
            basetried.append(base)
        elif(result==BOMBING_RECOVERABLE):
            #fly away and retry
            print('bomb failed but recoverable')
            while(True):
                HC.next(HC_TargetAlt)
                dist=GetPlayer2BaseDistance(GetPlayer(),base)
                print('flying away from base trying to recover, dist={}'.format(dist))
                if(dist>BOMBING_RETRY_DISTANCE):
                    break
                delay(BOMBING_RETRY_CHECK_INTERVAL)
    AFK()
    #ShutDown()



def test():
    print('booting up')
    BootUp()
    planeConfig.DropBombPrepare()
    planeConfig.DropBomb()
    planeConfig.DropBombDone()
    
test()
