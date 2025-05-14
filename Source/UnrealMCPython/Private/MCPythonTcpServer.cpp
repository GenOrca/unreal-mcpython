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

// Helper function to convert FJsonValue to Python literal string
FString ConvertJsonValueToPythonLiteral(const TSharedPtr<FJsonValue>& JsonVal)
{
    if (!JsonVal.IsValid() || JsonVal->Type == EJson::Null) return TEXT("None");

    switch (JsonVal->Type)
    {
        case EJson::String:
        {
            FString EscapedString = JsonVal->AsString();
            // Order of replacement is important.
            // Escape backslashes: "\" -> "\\"
            EscapedString = EscapedString.Replace(TEXT("\\"), TEXT("\\\\"));
            // Escape single quotes: ' -> \'
            EscapedString = EscapedString.Replace(TEXT("\'"), TEXT("\\\'"));
            // Escape double quotes: \" -> \\\"
            EscapedString = EscapedString.Replace(TEXT("\""), TEXT("\\\""));
            // Escape newlines: \n -> \\n
            EscapedString = EscapedString.Replace(TEXT("\n"), TEXT("\\n"));
            // Escape carriage returns: \r -> \\r
            EscapedString = EscapedString.Replace(TEXT("\r"), TEXT("\\r"));
            // Escape tabs: \t -> \\t
            EscapedString = EscapedString.Replace(TEXT("\t"), TEXT("\\t"));
            return FString::Printf(TEXT("\'%s\'"), *EscapedString);
        }
        case EJson::Number:
            return JsonVal->AsString();
        case EJson::Boolean:
            return JsonVal->AsBool() ? TEXT("True") : TEXT("False");
        case EJson::Array:
        {
            FString ArrayLiteral = TEXT("[");
            const auto& Array = JsonVal->AsArray();
            for (int32 i = 0; i < Array.Num(); ++i) {
                ArrayLiteral += ConvertJsonValueToPythonLiteral(Array[i]);
                if (i < Array.Num() - 1) ArrayLiteral += TEXT(", ");
            }
            ArrayLiteral += TEXT("]");
            return ArrayLiteral;
        }
        case EJson::Object:
        {
            FString DictLiteral = TEXT("{");
            const auto& Object = JsonVal->AsObject();
            bool bFirst = true;
            for (const auto& Pair : Object->Values) {
                if (!bFirst) DictLiteral += TEXT(", ");
                
                FString KeyString = Pair.Key;
                // Escape key string as well (similar to EJson::String case)
                KeyString = KeyString.Replace(TEXT("\\"), TEXT("\\\\"));
                KeyString = KeyString.Replace(TEXT("\'"), TEXT("\\\'"));
                KeyString = KeyString.Replace(TEXT("\""), TEXT("\\\""));
                KeyString = KeyString.Replace(TEXT("\n"), TEXT("\\n"));
                KeyString = KeyString.Replace(TEXT("\r"), TEXT("\\r"));
                KeyString = KeyString.Replace(TEXT("\t"), TEXT("\\t"));

                DictLiteral += FString::Printf(TEXT("\'%s\': %s"), *KeyString, *ConvertJsonValueToPythonLiteral(Pair.Value));
                bFirst = false;
            }
            DictLiteral += TEXT("}");
            return DictLiteral;
        }
        default:
            return TEXT("None");
    }
}

FMCPythonTcpServer::FMCPythonTcpServer() {}
FMCPythonTcpServer::~FMCPythonTcpServer() { Stop(); }

bool FMCPythonTcpServer::Start(const FString& InIP, uint16 InPort)
{
    FIPv4Address IPAddr;
    FIPv4Address::Parse(InIP, IPAddr);
    FIPv4Endpoint Endpoint(IPAddr, InPort);

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

    TSharedPtr<FJsonObject> JsonObj;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Data);
    FString TypeField;
    FString CodeField;
    FString ResultMsg;
    bool bExecSuccess = false;

    if (FJsonSerializer::Deserialize(Reader, JsonObj) && JsonObj.IsValid())
    {
        if (JsonObj->TryGetStringField(TEXT("type"), TypeField))
        {
            if (TypeField == TEXT("python"))
            {
                if (!JsonObj->TryGetStringField(TEXT("code"), CodeField))
                {
                    ResultMsg = TEXT("Failed: 'code' field missing for type 'python'");
                    CodeField = TEXT("import json; print(json.dumps({'success': False, 'message': 'Error: code field missing'}))");
                }
            }
            else if (TypeField == TEXT("python_call"))
            {
                FString ModuleName, FunctionName;
                if (JsonObj->TryGetStringField(TEXT("module"), ModuleName) &&
                    JsonObj->TryGetStringField(TEXT("function"), FunctionName))
                {
                    const TSharedPtr<FJsonObject>* ArgsJsonObjectPtr = nullptr; // Changed from TArray<TSharedPtr<FJsonValue>>*
                    JsonObj->TryGetObjectField(TEXT("args"), ArgsJsonObjectPtr); // Changed from TryGetArrayField

                    FString PyArgsStringForCall;
                    if (ArgsJsonObjectPtr && ArgsJsonObjectPtr->IsValid()) // Check if the pointer and the object it points to are valid
                    {
                        // Wrap the FJsonObject in an FJsonValueObject to pass to ConvertJsonValueToPythonLiteral
                        TSharedPtr<FJsonValueObject> ArgsJsonValue = MakeShareable(new FJsonValueObject(*ArgsJsonObjectPtr));
                        PyArgsStringForCall = ConvertJsonValueToPythonLiteral(ArgsJsonValue);
                    }
                    else
                    {
                        PyArgsStringForCall = TEXT("{}"); // Default to an empty Python dictionary string if "args" is not a valid object or is missing
                    }

                    // Generate a short script to call the execute_action function from the mcp_unreal_actions module
                    // The first argument is the target module name, the second is the target function name, and the third is the argument dictionary.
                    CodeField = FString::Printf(TEXT("import mcp_unreal_actions;print(mcp_unreal_actions.execute_action(\'%s\', \'%s\', %s));"), // Removed [] around %s
                                                *ModuleName, 
                                                *FunctionName, 
                                                *PyArgsStringForCall); 

                    UE_LOG(LogMCPython, Log, TEXT("Generated Python Call (via execute_action):\\n%s"), *CodeField);
                }
                else
                {
                    ResultMsg = TEXT("Failed: Missing 'module' or 'function' field for type 'python_call'");
                    CodeField = TEXT("import json; print(json.dumps({'success': False, 'message': 'Error: module/function field missing'}))");
                }
            }
            else
            {
                ResultMsg = FString::Printf(TEXT("Failed: Unsupported type: %s"), *TypeField);
                FString EscapedTypeField = TypeField.Replace(TEXT("\'"), TEXT("\\\'"));
                CodeField = FString::Printf(TEXT("import json; print(json.dumps({'success': False, 'message': 'Unsupported type: %s'}))"), *EscapedTypeField);
            }

            if (IPythonScriptPlugin::Get())
            {
                LogCapture.Clear();
                GLog->AddOutputDevice(&LogCapture);
                
                FPythonCommandEx PythonCommand;
                PythonCommand.Command = CodeField;
                PythonCommand.ExecutionMode = EPythonCommandExecutionMode::ExecuteFile;

                bExecSuccess = IPythonScriptPlugin::Get()->ExecPythonCommandEx(PythonCommand);
                
                GLog->RemoveOutputDevice(&LogCapture);

                FString CapturedLogs = LogCapture.GetLogs().TrimStartAndEnd();

                bool bIsJson = false;
                if (CapturedLogs.StartsWith(TEXT("{")) || CapturedLogs.StartsWith(TEXT("["))) {
                    bIsJson = true;
                }
                if (!bIsJson) {
                    TSharedPtr<FJsonObject> ErrorJson = MakeShareable(new FJsonObject);
                    ErrorJson->SetBoolField(TEXT("success"), false);
                    ErrorJson->SetStringField(TEXT("message"), TEXT("Python did not return JSON"));
                    ErrorJson->SetStringField(TEXT("raw_result"), CapturedLogs);
                    FString WrappedJson;
                    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&WrappedJson);
                    FJsonSerializer::Serialize(ErrorJson.ToSharedRef(), Writer);
                    Writer->Close();
                    CapturedLogs = WrappedJson;
                }

                UE_LOG(LogMCPython, Log, TEXT("Python Command Executed. Success: %s. Output Log: %s"),
                    bExecSuccess ? TEXT("True") : TEXT("False"), *CapturedLogs);

                TSharedPtr<FJsonObject> ResponseToClient = MakeShareable(new FJsonObject);
                ResponseToClient->SetBoolField(TEXT("success"), bExecSuccess); // Overall success of ExecPythonCommandEx
                
                if (!ResultMsg.IsEmpty()) // If there was a pre-execution error message (e.g. bad JSON input from client)
                {
                     ResponseToClient->SetStringField(TEXT("message"), ResultMsg);
                }
                else if (!bExecSuccess) // Python execution itself failed
                {
                    if (!CapturedLogs.IsEmpty())
                    {
                        // If execution failed and logs are available, they likely contain the Python error
                        ResponseToClient->SetStringField(TEXT("message"), TEXT("Python execution failed. See result for details."));
                    }
                    else
                    {
                        // If execution failed and no logs, it's a more generic failure
                        ResponseToClient->SetStringField(TEXT("message"), TEXT("Python execution failed with no specific error log."));
                    }
                }
                else // bExecSuccess is true
                {
                     ResponseToClient->SetStringField(TEXT("message"), TEXT("Python command executed successfully."));
                }
                
                // The "result" field will contain whatever the Python script printed.
                ResponseToClient->SetStringField(TEXT("result"), CapturedLogs);

                FString ResultJson;
                TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResultJson);
                FJsonSerializer::Serialize(ResponseToClient.ToSharedRef(), Writer);
                Writer->Close();

                FTCHARToUTF8 ResultUtf8(*ResultJson);
                const uint8* DataPtr = (const uint8*)ResultUtf8.Get();
                int32 TotalSize = ResultUtf8.Length();
                int32 TotalSent = 0;
                while (TotalSent < TotalSize)
                {
                    int32 SentNow = 0;
                    if (!ClientSocket->Send(DataPtr + TotalSent, TotalSize - TotalSent, SentNow))
                    {
                        break; // Error occurred
                    }
                    if (SentNow == 0)
                    {
                        break; // Connection closed or can't send more
                    }
                    TotalSent += SentNow;
                }
            }
            else
            {
                ResultMsg = TEXT("Failed: PythonScriptPlugin not found");
                TSharedPtr<FJsonObject> ErrorResponse = MakeShareable(new FJsonObject);
                ErrorResponse->SetBoolField(TEXT("success"), false);
                ErrorResponse->SetStringField(TEXT("message"), ResultMsg);
                FString ErrorJson;
                TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ErrorJson);
                FJsonSerializer::Serialize(ErrorResponse.ToSharedRef(), Writer);
                Writer->Close();
                FTCHARToUTF8 ResultUtf8(*ErrorJson);
                const uint8* DataPtr = (const uint8*)ResultUtf8.Get();
                int32 TotalSize = ResultUtf8.Length();
                int32 TotalSent = 0;
                while (TotalSent < TotalSize)
                {
                    int32 SentNow = 0;
                    if (!ClientSocket->Send(DataPtr + TotalSent, TotalSize - TotalSent, SentNow))
                    {
                        break;
                    }
                    if (SentNow == 0)
                    {
                        break;
                    }
                    TotalSent += SentNow;
                }
            }
        }
        else
        {
            ResultMsg = TEXT("Failed: Missing 'type' field in JSON request");
            TSharedPtr<FJsonObject> ErrorResponse = MakeShareable(new FJsonObject);
            ErrorResponse->SetBoolField(TEXT("success"), false);
            ErrorResponse->SetStringField(TEXT("message"), ResultMsg);
            FString ErrorJson;
            TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ErrorJson);
            FJsonSerializer::Serialize(ErrorResponse.ToSharedRef(), Writer);
            Writer->Close();
            FTCHARToUTF8 ResultUtf8(*ErrorJson);
            const uint8* DataPtr = (const uint8*)ResultUtf8.Get();
            int32 TotalSize = ResultUtf8.Length();
            int32 TotalSent = 0;
            while (TotalSent < TotalSize)
            {
                int32 SentNow = 0;
                if (!ClientSocket->Send(DataPtr + TotalSent, TotalSize - TotalSent, SentNow))
                {
                    break;
                }
                if (SentNow == 0)
                {
                    break;
                }
                TotalSent += SentNow;
            }
        }
    }
    else
    {
        ResultMsg = TEXT("Failed: JSON parse error on received data");
        TSharedPtr<FJsonObject> ErrorResponse = MakeShareable(new FJsonObject);
        ErrorResponse->SetBoolField(TEXT("success"), false);
        ErrorResponse->SetStringField(TEXT("message"), ResultMsg);
        ErrorResponse->SetStringField(TEXT("raw_data"), Data);
        FString ErrorJson;
        TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ErrorJson);
        FJsonSerializer::Serialize(ErrorResponse.ToSharedRef(), Writer);
        Writer->Close();
        FTCHARToUTF8 ResultUtf8(*ErrorJson);
        const uint8* DataPtr = (const uint8*)ResultUtf8.Get();
        int32 TotalSize = ResultUtf8.Length();
        int32 TotalSent = 0;
        while (TotalSent < TotalSize)
        {
            int32 SentNow = 0;
            if (!ClientSocket->Send(DataPtr + TotalSent, TotalSize - TotalSent, SentNow))
            {
                break;
            }
            if (SentNow == 0)
            {
                break;
            }
            TotalSent += SentNow;
        }
    }

    ClientSocket->Close();
    ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(ClientSocket);
}