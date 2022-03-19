
from ctypes import *
import os
InterprocessServer=windll.LoadLibrary('InterprocessServer.dll')

hMem=c_longlong()
hMemView=c_longlong()
InterprocessServer.CreateMemMap(c_char_p('IPS'.encode("utf-8")),1024,pointer(hMem),pointer(hMemView))
print(hex(hMem.value),hex(hMemView.value))

m1=c_int.from_address(hMemView.value)
m1.value=12345
m2=c_int.from_address(hMemView.value)
print(m2.value)

print('press any key to delete memmap')
os.system('pause')

InterprocessServer.DeleteMemMap(hMem,hMemView)