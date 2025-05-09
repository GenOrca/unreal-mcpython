#pragma once

#include "CoreMinimal.h"
#include "Interfaces/IPv4/IPv4Endpoint.h"
#include <memory>

class FTcpListener;
class FSocket;

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

	bool HandleIncomingConnection(FSocket* ClientSocket, const FIPv4Endpoint& ClientEndpoint);
}; 