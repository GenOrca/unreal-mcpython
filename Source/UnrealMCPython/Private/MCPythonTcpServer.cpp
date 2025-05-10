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

    // Set up the listener
    TcpListener = MakeShared<FTcpListener>(Endpoint, FTimespan::FromMilliseconds(100), false);
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
    UE_LOG(LogMCPython, Log, TEXT("Incoming connection from %s"), *ClientEndpoint.ToString());

    AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [this, ClientSocket, ClientEndpoint]() {
        TArray<uint8> ReceivedData;

        uint32 DataSize = 0;
        while (ClientSocket->HasPendingData(DataSize) || ReceivedData.IsEmpty())
        {
            TArray<uint8> Buffer;
            Buffer.SetNumZeroed(DataSize);
            int32 BytesRead = 0;
            ClientSocket->Recv(Buffer.GetData(), Buffer.Num(), BytesRead);
            Buffer.SetNum(BytesRead);
            ReceivedData.Append(Buffer);
        }
        ReceivedData.Add(NULL);

        FString ReceivedString = FString(UTF8_TO_TCHAR(reinterpret_cast<const char*>(ReceivedData.GetData())));

        AsyncTask(ENamedThreads::GameThread, [this, ReceivedString, ClientSocket, ClientEndpoint]() {
            ProcessDataOnGameThread(ReceivedString, ClientSocket, ClientEndpoint);
        });
    });

    return true;
}

void FMCPythonTcpServer::ProcessDataOnGameThread(const FString& Data, FSocket* ClientSocket, const FIPv4Endpoint& ClientEndpoint)
{
    UE_LOG(LogMCPython, Log, TEXT("Processing Data on Game Thread: %s"), *Data);

    // Parse JSON
    TSharedPtr<FJsonObject> JsonObj;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Data);
    FString TypeField;
    FString CodeField;
    FString ResultMsg;
    FString Result;
    bool bSuccess = false;

    if (FJsonSerializer::Deserialize(Reader, JsonObj) && JsonObj.IsValid())
    {
        if (JsonObj->TryGetStringField(TEXT("type"), TypeField) && JsonObj->TryGetStringField(TEXT("code"), CodeField))
        {
            if (TypeField == TEXT("python"))
            {
                if (IPythonScriptPlugin::Get())
                {
                    LogCapture.Clear();
                    GLog->AddOutputDevice(&LogCapture);
                    
                    FPythonCommandEx PythonCommand;
                    PythonCommand.Command = CodeField;
                    
                    bSuccess = IPythonScriptPlugin::Get()->ExecPythonCommandEx(PythonCommand);
                    
                    GLog->RemoveOutputDevice(&LogCapture);
                    FString CapturedLogs = LogCapture.GetLogs();

                    UE_LOG(LogMCPython, Log, TEXT("Python Command Result: %s"), *PythonCommand.CommandResult);

                    Result = PythonCommand.CommandResult;
                    ResultMsg = bSuccess ? TEXT("") : TEXT("Failed ExecPythonCommandEx");
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
    
    if (!LogCapture.GetLogs().IsEmpty())
    {
        ResultObj->SetStringField(TEXT("result"), LogCapture.GetLogs());
    }
    
    FString ResultJson;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResultJson);
    FJsonSerializer::Serialize(ResultObj.ToSharedRef(), Writer);

    // Convert to UTF-8 and send
    FTCHARToUTF8 ResultUtf8(*ResultJson);
    int32 Sent = 0;
    ClientSocket->Send((uint8*)ResultUtf8.Get(), ResultUtf8.Length(), Sent);

    ClientSocket->Close();
    ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(ClientSocket);
}