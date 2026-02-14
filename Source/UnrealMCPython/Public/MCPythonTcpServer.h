// Copyright (c) 2025 GenOrca (by zenoengine). All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Interfaces/IPv4/IPv4Endpoint.h"
#include <memory>
#include "Misc/OutputDeviceRedirector.h"

class FTcpListener;
class FSocket;

class FPythonLogCapture : public FOutputDevice
{
public:
	FPythonLogCapture() : FOutputDevice() {}

	virtual void Serialize(const TCHAR* InData, ELogVerbosity::Type Verbosity, const FName& Category) override
	{
		if (Category == FName("LogPython"))
		{
			CapturedLogs.Append(InData);
			CapturedLogs.Append(TEXT("\n"));
		}
	}

	void Clear() { CapturedLogs.Empty(); }
	FString GetLogs() const { return CapturedLogs; }

private:
	FString CapturedLogs;
};

using FNativeCommandHandler = TFunction<void(TSharedPtr<FJsonObject> JsonObj, FSocket* ClientSocket)>;

class FMCPythonTcpServer
{
public:
	FMCPythonTcpServer();
	~FMCPythonTcpServer();

	bool Start(const FString& InIP, uint16 InPort);
	void Stop();

private:
	TSharedPtr<FTcpListener> TcpListener;
	FSocket* ListenSocket = nullptr;
	bool bShouldRun = false;
	FPythonLogCapture LogCapture;
	TMap<FString, FNativeCommandHandler> NativeHandlers;

	void RegisterNativeHandlers();
	bool HandleIncomingConnection(FSocket* ClientSocket, const FIPv4Endpoint& ClientEndpoint);
	void ProcessDataOnGameThread(const FString& Data, FSocket* ClientSocket, const FIPv4Endpoint& ClientEndpoint);
	void SendJsonResponse(TSharedPtr<FJsonObject> ResponseJson, FSocket* ClientSocket, bool bCloseSocket = true);

	// Native command handlers
	void HandleLiveCodingCompile(TSharedPtr<FJsonObject> JsonObj, FSocket* ClientSocket);
};