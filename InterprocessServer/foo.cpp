#include "pch.h"
#define IN_SERVER_DLL
#include "common.h"

FUNC_EXPORT_SERVER void WINAPI CreateMemMap(char* name, size_t len, size_t* hMem,size_t* hMemView)
{
	*hMem = (size_t)CreateFileMappingA(INVALID_HANDLE_VALUE,NULL, PAGE_EXECUTE_READWRITE, 0, len, name);
	*hMemView = (size_t)MapViewOfFile((HANDLE)*hMem, FILE_MAP_ALL_ACCESS, 0, 0, 0);
}

FUNC_EXPORT_SERVER void WINAPI DeleteMemMap(size_t hMem, size_t hMemView)
{
	UnmapViewOfFile((LPCVOID)hMemView);
	CloseHandle((HANDLE)hMem);
}

FUNC_EXPORT_SERVER void WINAPI Write(char* buffer, char* ptr, size_t len)
{
	memcpy(ptr, buffer, len);
}

FUNC_EXPORT_SERVER void WINAPI Read(char* buffer, char* ptr, size_t len)
{
	memcpy(buffer, ptr, len);
}

FUNC_EXPORT_SERVER void WINAPI WriteInt32(int32_t content, char* ptr)
{
	*(int32_t*)ptr = content;
}

FUNC_EXPORT_SERVER int32_t WINAPI ReadInt32(char* ptr)
{
	return *(int32_t*)ptr;
}

FUNC_EXPORT_SERVER void WINAPI Test(char* content)
{
	MessageBoxA(NULL, content, "title", MB_OK);
}

FUNC_EXPORT_SERVER void WINAPI ISInfo()
{
	MessageBoxA(NULL, "Server using MemMap, stdcall", "title", MB_OK);
}

FUNC_EXPORT_SERVER void WINAPI RefTest(int val,int& ref)
{
	val = 1;
	ref = 2;
}
