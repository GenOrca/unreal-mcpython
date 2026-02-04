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

	bool HandleIncomingConnection(FSocket* ClientSocket, const FIPv4Endpoint& ClientEndpoint);
	void ProcessDataOnGameThread(const FString& Data, FSocket* ClientSocket, const FIPv4Endpoint& ClientEndpoint);
};