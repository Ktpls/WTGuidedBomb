
from ctypes import *
import json
from PIL import ImageGrab
import aircv
import numpy as np
import requests
import time
FIND_BASE_OBJ_PATH='pic/base_big.jpg'
WIDTH_OF_SCREEN=1920
HEIGHT_OF_SCREEN=1080
XCENTER_OF_SCREEN=WIDTH_OF_SCREEN/2 #960
YCENTER_OF_SCREEN=HEIGHT_OF_SCREEN/2 #540
FIND_BASE_XRANGE=0.1*WIDTH_OF_SCREEN/2
FIND_BASE_YRANGE=0.75*HEIGHT_OF_SCREEN/2
InterprocessServer=windll.LoadLibrary('InterprocessServer.dll')
hMem=c_longlong()
hMemView=c_longlong()
IPSName='IPS'
imgobj=aircv.imread(FIND_BASE_OBJ_PATH)

def ReadIPSInt32(pos):
    return c_int.from_address(hMemView.value+pos*4).value

def WriteIPSInt32(content,pos):
    c_int.from_address(hMemView.value+pos*4).value=content

def FindBase():
    rect=(XCENTER_OF_SCREEN-FIND_BASE_XRANGE, YCENTER_OF_SCREEN-FIND_BASE_YRANGE, XCENTER_OF_SCREEN+FIND_BASE_XRANGE, YCENTER_OF_SCREEN+FIND_BASE_YRANGE)
    imgscr = ImageGrab.grab(rect)
    imgscr = np.array(imgscr.getdata(),dtype='uint8')\
    .reshape((imgscr.size[1],imgscr.size[0],3))
    match_result=aircv.find_template(imgscr,imgobj,0.22)
    if match_result is not None:
        return {\
            'x':match_result['result'][0]+rect[0],\
            'y':match_result['result'][1]+rect[1],\
            'c':match_result['confidence']}
    else:
        return None

def Get8111Json(file):
    return json.loads(requests.get('http://laptop-hlemg33h:8111/{}'.format(file)).text)

def GetBaseList():
    map_obj_json=Get8111Json('map_obj.json')
    baselist=[{\
        'x':base['x'],\
        'y':base['y']}\
        for base in map_obj_json if base['type'] == 'bombing_point'
        ]
    return baselist

def GetPlayer():
    map_obj_json=Get8111Json('map_obj.json')
    playerlist=[x for x in map_obj_json if x["icon"] == "Player"]
    if(len(playerlist)>=0):
        info=playerlist[0]
        return {\
            'x':info['x'],\
            'y':info['y'],\
            'dx':info['dx'],\
            'dy':info['dy'],\
            }
    else:
        return None

def GetClimb():
    state_json=Get8111Json('state')
    if(state_json['valid']):
        return state_json['Vy, m/s']
    else:
        return None

def GetHeight():
    state_json=Get8111Json('state')
    if(state_json['valid']):
        return state_json['H, m']
    else:
        return None

def delay(t):
    time.sleep(t)