import csv
import os

def toCStyle(constlist):
	ret=""
	for c in constlist:
		if(len(c)<2):
			ret+='\n'
			continue
		ret+='const int {} = {};\n'.format(c[0],c[1])
	return ret

def toPythonStyle(constlist):
	ret=""
	for c in constlist:
		if(len(c)<2):
			ret+='\n'
			continue
		ret+='"{}": {},\n'.format(c[0],c[1])
	return ret

def toVBStyle(constlist):
	ret=""
	for c in constlist:
		if(len(c)<2):
			ret+='\n'
			continue
		ret+='const {} = {}\n'.format(c[0],c[1])
	return ret

def main():
	constlist=[]
	with open(r"D:\File\code\prog\InterprocessServer\PyTest\const.csv") as f:
		f_csv = csv.reader(f)
		for row in f_csv:
			constlist.append(row)

	print('###################')
	print('####PythonStyle####')
	print('###################')
	print(toPythonStyle(constlist))
	
	print('###############')
	print('####VBStyle####')
	print('###############')
	print(toVBStyle(constlist))
	
	os.system('pause')

main()