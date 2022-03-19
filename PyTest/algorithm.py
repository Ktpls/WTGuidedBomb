
import time

def myfind(container,pred):
    for i in container:
        if(pred(i)):
            return i
    return None
    
def base_eq(base1,base2):
    BASE_EQ_EPISLON=0.001
    return (abs(base1['x']-base2['x'])<BASE_EQ_EPISLON and abs(base1['y']-base2['y'])<BASE_EQ_EPISLON)


PID_USE_REAL_TIME=-1
class pid:
    def __init__(self,kp,ki,kd):
        self.kp=kp
        self.ki=ki
        self.kd=kd
        self.lasterr=0
        self.integral=0
        self.lasttime=time.time()
    
    def next(self,err,dt=PID_USE_REAL_TIME):
        
        if(dt<=0):
            nowtime=time.time()
            dt=nowtime-self.lasttime
            self.lasttime=nowtime
        deri=(err-self.lasterr)/dt
        self.integral+=err*dt
        
        self.lasterr=err
        
        return dt*(self.kp*err+self.ki*self.integral+self.kd*deri)

class StableCounter:
    def __init__(self,Tmax,stableRange):
        self.Tmax=Tmax
        self.stableRange=stableRange
        self.stableTime=0

    def next(self,err):
        if(abs(err)<self.stableRange):
            self.stableTime+=1
            if(self.stableTime>self.Tmax):
                return True
        else:
            self.stableTime=0
            return False
