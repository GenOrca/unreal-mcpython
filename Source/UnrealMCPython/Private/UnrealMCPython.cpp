// Copyright (c) 2025 GenOrca (by zenoengine). All Rights Reserved.

#include "UnrealMCPython.h"
#include "Sockets.h"
#include "SocketSubsystem.h"
#include "Common/TcpListener.h"
#include "IPythonScriptPlugin.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonReader.h"
#include "Dom/JsonObject.h"
#include "MCPythonTcpServer.h"

#define LOCTEXT_NAMESPACE "FUnrealMCPythonModule"

void FUnrealMCPythonModule::StartupModule()
{
	static const uint16 SERVER_PORT = 12029;
	static const FString SERVER_IP = TEXT("127.0.0.1");
	TcpServer = MakeUnique<FMCPythonTcpServer>();
	TcpServer->Start(SERVER_IP, SERVER_PORT);
}

void FUnrealMCPythonModule::ShutdownModule()
{
	if (TcpServer)
	{
		TcpServer->Stop();
		TcpServer.Reset();
	}
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FUnrealMCPythonModule, UnrealMCPython)