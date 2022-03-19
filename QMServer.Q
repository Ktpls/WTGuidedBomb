[General]
SyntaxVersion=2
BeginHotkey=121
BeginHotkeyMod=0
PauseHotkey=0
PauseHotkeyMod=0
StopHotkey=123
StopHotkeyMod=0
RunOnce=1
EnableWindow=
MacroID=dc9896d4-e4d8-48db-9f1b-c2460bcf0f1a
Description=QMServer
Enable=0
AutoRun=0
[Repeat]
Type=0
Number=1
[SetupUI]
Type=2
QUI=
[Relative]
SetupOCXFile=
[Comment]

[Script]

'#######################################
'#######################################
'DONT QUIT MANUALLY ONCE STARTED RUNNING
'#######################################
'#######################################


'##################
'base layer
'##################

Declare Sub WriteInt32 Lib "InterprocessServer.dll"(byval content as long,byval ptr As Long)
Declare function ReadInt32 Lib "InterprocessServer.dll"(byval ptr As Long) As Long

Declare Function CreateFileMapping Lib "kernel32.dll" Alias "CreateFileMappingA" (ByVal hFile As Long, ByRef lpFileMappigAttributes As SECURITY_ATTRIBUTES, ByVal flProtect As Long, ByVal dwMaximumSizeHigh As Long, ByVal dwMaximumSizeLow As Long, ByVal lpName As String) As Long
Declare Function MapViewOfFile Lib "kernel32.dll" (ByVal hFileMappingObject As Long, ByVal dwDesiredAccess As Long, ByVal dwFileOffsetHigh As Long, ByVal dwFileOffsetLow As Long, ByVal dwNumberOfBytesToMap As Long) As Long
Declare Function UnmapViewOfFile Lib "kernel32.dll" (ByRef lpBaseAddress As Any) As Long
Declare Function CloseHandle Lib "kernel32.dll" (ByVal hObject As Long) As Long

Const PAGE_EXECUTE_READWRITE  = &H40
Const INVALID_HANDLE_VALUE  = -1

Const FILE_MAP_ALL_ACCESS  = &HF001F

Dim hMem, hMemView

Dim ProcessInterval
ProcessInterval = 1000
hWnd=0

Sub CreateMemMap_QM(name, length)
	hMem=CreateFileMapping(INVALID_HANDLE_VALUE,0, PAGE_EXECUTE_READWRITE,0,length,name)
	hMemView=MapViewOfFile(hMem,FILE_MAP_ALL_ACCESS,0,0,0)
End Sub

Sub DeleteMemMap_QM()
	UnmapViewOfFIle (hMemView)
	CloseHandle (hMem)
End Sub

Sub WriteIPSInt32(content, pos)
	WriteInt32 content,hMemView+pos*4
End Sub

function ReadIPSInt32(pos)
	ReadIPSInt32=ReadInt32(hMemView+pos*4)
End function



'##################
'command layer
'##################

'alloc
const cmdstate = 0
const exestate = 1
const cmdindex = 2
const exeindex = 3
const cmd = 4
const arg1 = 5
const arg2 = 6
Const ret1 = 7
Const ret2 = 8

'cmd/exe state
const default = 0
const online = 1
Const logout = 2

'cmd
const nop=0
const exitserver=1
const setresponsetime=2
const servertest=3
const pykeypress=4
const pykeydown=5
const pykeyup=6
const mousepress=7
const mousedown=8
const mouseup=9
const mousemove=10
Const mouserelativemove = 11
Const sethwnd = 12


Sub BootUp
	CreateMemMap_QM "IPS", 1024
	WriteIPSInt32 online, exestate
	TracePrint "waiting"
	Do
		If ReadIPSInt32(cmdstate) = online Then 
			Exit Do
		End If
		Delay 1000
	Loop
	TracePrint "all online"
	SetSimMode 2
End Sub

Sub ShutDown
	WriteIPSInt32 logout, exestate
	DeleteMemMap_QM 
End Sub


Sub ProcessCommand()
	CommandedExit=False
	Do
		do 'waiting for new command
			if ReadIPSInt32(cmdindex)>ReadIPSInt32(exeindex) then exit do
			delay ProcessInterval
		loop
		command=ReadIPSInt32(cmd)
		a1=ReadIPSInt32(arg1)
		a2=ReadIPSInt32(arg2)
		
		select case command
			case exitexe
				CommandedExit=True
			case setresponsetime
				ProcessInterval=a1
			case pykeypress
				KeyPress a1, 1
			case pykeydown
				keydown a1, 1
			case pykeyup
				KeyUp a1, 1
			Case mousepress
				Select Case a1
					Case 0
						LeftClick 1
					Case 1
						RightClick 1
					Case 2
						MiddleClick 1
				End Select
			Case mousedown
				Select Case a1
					Case 0
						LeftDown 1
					Case 1
						RightDown 1
					Case 2
						MiddleClick 1
				End Select
			Case mouseup
				Select Case a1
					Case 0
						LeftUp 1
					Case 1
						RightUp 1
					Case 2
						MiddleClick 1
				End Select
			Case mousemove
				MoveTo a1, a2
			Case mouserelativemove
				MoveR a1, a2
			Case sethwnd
				hWnd=a1
			case servertest
				msgbox "wonderful V18!"
			Case Else
				MsgBox "unknown command:" &command
		end select
		
		WriteIPSInt32 ReadIPSInt32(exeindex)+1, exeindex
		if CommandedExit then exit do
	Loop
End Sub





'##################
'main
'##################

BootUp
ProcessCommand
ShutDown
