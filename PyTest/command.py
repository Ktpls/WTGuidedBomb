
from base import *
from cons import cons

CALL_COMMAND_TIMEOUT=100
CALL_COMMAND_RETRY_TIME=0.1
def BootUp():
    InterprocessServer.CreateMemMap(c_char_p(IPSName.encode("utf-8")),1024,pointer(hMem),pointer(hMemView))
    print('hMem={}, hMemView={}'.format(hex(hMem.value),hex(hMemView.value)))
    WriteIPSInt32(cons['online'],cons['cmdstate'])
    while(True):
        if ReadIPSInt32(cons['exestate'])==cons['online']:
            break
        print('waiting')
        delay(1)
    print('all online')

def ShutDown():
    WriteIPSInt32(cons['logout'],cons['cmdstate'])
    InterprocessServer.DeleteMemMap(hMem,hMemView)


def CallCommand_RewriteKeyMousePress(CC):
    def newCallCommand(command,arg1=0,arg2=0):
        if(command==cons['keypress']):
            CC(cons['keydown'],arg1)
            CC(cons['keyup'],arg1)
        elif(command==cons['mousepress']):
            CC(cons['mousedown'],arg1)
            CC(cons['mouseup'],arg1)
        else:
            CC(command,arg1,arg2)
    return newCallCommand

#@exception: call command time out
@CallCommand_RewriteKeyMousePress
def CallCommand(command,arg1=0,arg2=0):
    failtimes=0
    while(True): #wait for command to finish
        if ReadIPSInt32(cons['cmdindex'])==ReadIPSInt32(cons['exeindex']):
            break
        failtimes+=1
        if(failtimes>=CALL_COMMAND_TIMEOUT):
            raise Exception('Calling command but time out')
        delay(CALL_COMMAND_RETRY_TIME)
    WriteIPSInt32(command,cons['cmd'])
    WriteIPSInt32(arg1,cons['arg1'])
    WriteIPSInt32(arg2,cons['arg2'])
    WriteIPSInt32(ReadIPSInt32(cons['cmdindex'])+1,cons['cmdindex'])
    #print(ReadIPSInt32(cons['cmdindex']),ReadIPSInt32(cons['exeindex']))
