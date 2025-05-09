#include "MCPythonTcpServer.h"
#include "Sockets.h"
#include "SocketSubsystem.h"
#include "Networking.h"
#include "Common/TcpListener.h"
#include "IPythonScriptPlugin.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonReader.h"
#include "Dom/JsonObject.h"

DEFINE_LOG_CATEGORY_STATIC(LogMCPython, Log, All);

FMCPythonTcpServer::FMCPythonTcpServer() {}
FMCPythonTcpServer::~FMCPythonTcpServer() { Stop(); }

bool FMCPythonTcpServer::Start(const FString& InIP, uint16 InPort)
{
	FIPv4Address IPAddr;
	FIPv4Address::Parse(InIP, IPAddr);
	FIPv4Endpoint Endpoint(IPAddr, InPort);
	FTimespan WaitTime = FTimespan::FromMilliseconds(100);
	TcpListener = MakeShared<FTcpListener>(Endpoint, WaitTime, false);
	TcpListener->OnConnectionAccepted().BindRaw(this, &FMCPythonTcpServer::HandleIncomingConnection);
	bShouldRun = true;
	UE_LOG(LogMCPython, Log, TEXT("TCP server started at %s:%d."), *InIP, InPort);
	return true;
}

void FMCPythonTcpServer::Stop()
{
	bShouldRun = false;
	TcpListener.Reset();
	UE_LOG(LogMCPython, Log, TEXT("TCP server stopped."));
}

bool FMCPythonTcpServer::HandleIncomingConnection(FSocket* ClientSocket, const FIPv4Endpoint& ClientEndpoint)
{
	UE_LOG(LogMCPython, Log, TEXT("Client connected: %s"), *ClientEndpoint.ToString());

	constexpr int32 MaxDataSize = 4096;
	TArray<uint8> ReceivedData;
	uint32 DataSize = 0;
	FString ReceivedString;

	// Receive data (up to 4096 bytes, UTF-8)
	while (ClientSocket->HasPendingData(DataSize))
	{
		int32 Read = 0;
		int32 ToRead = FMath::Min((uint32)MaxDataSize - ReceivedData.Num(), DataSize);
		if (ToRead <= 0) break;
		int32 StartIdx = ReceivedData.AddUninitialized(ToRead);
		ClientSocket->Recv(ReceivedData.GetData() + StartIdx, ToRead, Read);
	}
	if (ReceivedData.Num() == 0)
	{
		UE_LOG(LogMCPython, Warning, TEXT("No data received"));
		ClientSocket->Close();
		ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(ClientSocket);
		return false;
	}
	FUTF8ToTCHAR Converter((const char*)ReceivedData.GetData(), ReceivedData.Num());
	ReceivedString = FString(Converter.Length(), Converter.Get());

	// Parse JSON
	TSharedPtr<FJsonObject> JsonObj;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(ReceivedString);
	FString TypeField;
	FString CodeField;
	FString ResultMsg;
	bool bSuccess = false;
	if (FJsonSerializer::Deserialize(Reader, JsonObj) && JsonObj.IsValid())
	{
		if (JsonObj->TryGetStringField(TEXT("type"), TypeField) && JsonObj->TryGetStringField(TEXT("code"), CodeField))
		{
			if (TypeField == TEXT("python"))
			{
				// Execute Python command
				if (IPythonScriptPlugin::Get())
				{
					bSuccess = IPythonScriptPlugin::Get()->ExecPythonCommand(*CodeField);
					ResultMsg = bSuccess ? TEXT("Success") : TEXT("Failed: Execution error");
				}
				else
				{
					ResultMsg = TEXT("Failed: PythonScriptPlugin not found");
				}
			}
			else
			{
				ResultMsg = FString::Printf(TEXT("Failed: Unsupported type: %s"), *TypeField);
			}
		}
		else
		{
			ResultMsg = TEXT("Failed: Missing 'type' or 'code' field");
		}
	}
	else
	{
		ResultMsg = TEXT("Failed: JSON parse error");
	}

	// Create result JSON
	TSharedPtr<FJsonObject> ResultObj = MakeShareable(new FJsonObject);
	ResultObj->SetBoolField(TEXT("success"), bSuccess);
	ResultObj->SetStringField(TEXT("message"), ResultMsg);
	FString ResultJson;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResultJson);
	FJsonSerializer::Serialize(ResultObj.ToSharedRef(), Writer);

	// Convert to UTF-8 and send
	FTCHARToUTF8 ResultUtf8(*ResultJson);
	int32 Sent = 0;
	ClientSocket->Send((uint8*)ResultUtf8.Get(), ResultUtf8.Length(), Sent);

	ClientSocket->Close();
	ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(ClientSocket);

	return true;
} 