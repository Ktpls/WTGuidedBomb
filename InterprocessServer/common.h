#pragma once
#ifdef IN_SERVER_DLL
#define FUNC_EXPORT_SERVER extern "C" __declspec(dllexport)
#else
#define FUNC_EXPORT_SERVER extern "C" __declspec(dllimport)
#endif