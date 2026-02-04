// Copyright (c) 2025 GenOrca (by zenoengine). All Rights Reserved.

#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "EdGraph/EdGraphNode.h"
#include "EdGraph/EdGraphPin.h"
#include "MCPythonHelper.generated.h"


USTRUCT(BlueprintType)
struct FMCPythonPinLinkInfo
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString NodeName;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString NodeTitle;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString PinName;
};

USTRUCT(BlueprintType)
struct FMCPythonBlueprintPinInfo
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString PinName;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString FriendlyName;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString Direction;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString PinType;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString PinSubType;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString DefaultValue;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    TArray<FMCPythonPinLinkInfo> LinkedTo;
};

USTRUCT(BlueprintType)
struct FMCPythonBlueprintNodeInfo
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString NodeName;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString NodeTitle;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    FString NodeComment;
    UPROPERTY(BlueprintReadOnly, Category="MCPython")
    TArray<FMCPythonBlueprintPinInfo> Pins;
};

UCLASS()
class UNREALMCPYTHON_API UMCPythonHelper : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // 모든 에디터에서 열려있는 에셋 반환
    UFUNCTION(BlueprintCallable, Category="Editor|MCPython", CallInEditor)
    static TArray<UObject*> GetAllEditedAssets();

    // (예시) 선택된 블루프린트 노드 반환
    UFUNCTION(BlueprintCallable, Category="Editor|MCPython", CallInEditor)
    static TArray<UObject*> GetSelectedBlueprintNodes();

    // 선택된 블루프린트 노드의 연결 정보 반환
    UFUNCTION(BlueprintCallable, Category="Editor|MCPython", CallInEditor)
    static TArray<FMCPythonBlueprintNodeInfo> GetSelectedBlueprintNodeInfos();
};
