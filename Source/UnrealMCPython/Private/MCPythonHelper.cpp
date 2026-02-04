// Copyright (c) 2025 GenOrca (by zenoengine). All Rights Reserved.

#include "MCPythonHelper.h"
#include "Editor.h"
#include "Subsystems/AssetEditorSubsystem.h"
#include "Toolkits/AssetEditorToolkit.h"
#include "BlueprintEditor.h"

TArray<UObject*> UMCPythonHelper::GetAllEditedAssets()
{
    if (!GEditor) return {};
    return GEditor->GetEditorSubsystem<UAssetEditorSubsystem>()->GetAllEditedAssets();
}

TArray<UObject*> UMCPythonHelper::GetSelectedBlueprintNodes()
{
    TArray<UObject*> Result;
    if (!GEditor) return Result;
    auto* Subsystem = GEditor->GetEditorSubsystem<UAssetEditorSubsystem>();
    for (UObject* Asset : Subsystem->GetAllEditedAssets())
    {
        IAssetEditorInstance* AssetEditorInstance = Subsystem->FindEditorForAsset(Asset, false);
        FAssetEditorToolkit* AssetEditorToolkit = static_cast<FAssetEditorToolkit*>(AssetEditorInstance);
        if (!AssetEditorToolkit) continue;
        TSharedPtr<SDockTab> Tab = AssetEditorToolkit->GetTabManager()->GetOwnerTab();
        if (Tab.IsValid() && Tab->IsForeground())
        {
            FBlueprintEditor* BlueprintEditor = static_cast<FBlueprintEditor*>(AssetEditorToolkit);
            if (BlueprintEditor)
            {
                FGraphPanelSelectionSet SelectedNodes = BlueprintEditor->GetSelectedNodes();
                for (UObject* Node : SelectedNodes)
                {
                    Result.Add(Node);
                }
            }
        }
    }
    return Result;
}

TArray<FMCPythonBlueprintNodeInfo> UMCPythonHelper::GetSelectedBlueprintNodeInfos()
{
    TArray<FMCPythonBlueprintNodeInfo> Result;
    if (!GEditor) return Result;
    auto* Subsystem = GEditor->GetEditorSubsystem<UAssetEditorSubsystem>();
    for (UObject* Asset : Subsystem->GetAllEditedAssets())
    {
        IAssetEditorInstance* AssetEditorInstance = Subsystem->FindEditorForAsset(Asset, false);
        FAssetEditorToolkit* AssetEditorToolkit = static_cast<FAssetEditorToolkit*>(AssetEditorInstance);
        if (!AssetEditorToolkit) continue;
        TSharedPtr<SDockTab> Tab = AssetEditorToolkit->GetTabManager()->GetOwnerTab();
        if (Tab.IsValid() && Tab->IsForeground())
        {
            FBlueprintEditor* BlueprintEditor = static_cast<FBlueprintEditor*>(AssetEditorToolkit);
            if (BlueprintEditor)
            {
                FGraphPanelSelectionSet SelectedNodes = BlueprintEditor->GetSelectedNodes();
                for (UObject* NodeObj : SelectedNodes)
                {
                    UEdGraphNode* Node = Cast<UEdGraphNode>(NodeObj);
                    if (!Node) continue;
                    FMCPythonBlueprintNodeInfo NodeInfo;
                    NodeInfo.NodeName = Node->GetName();
                    NodeInfo.NodeTitle = Node->GetNodeTitle(ENodeTitleType::FullTitle).ToString();
                    NodeInfo.NodeComment = Node->NodeComment;
                    for (UEdGraphPin* Pin : Node->Pins)
                    {
                        if (!Pin || Pin->bHidden) continue;
                        FMCPythonBlueprintPinInfo PinInfo;
                        FString Friendly = Pin->PinFriendlyName.ToString();
                        PinInfo.PinName = Pin->GetName();
                        PinInfo.FriendlyName = Friendly;
                        PinInfo.Direction = (Pin->Direction == EGPD_Input) ? TEXT("In") : TEXT("Out");
                        PinInfo.PinType = Pin->PinType.PinCategory.ToString();
                        if (Pin->PinType.PinSubCategoryObject.IsValid())
                        {
                            PinInfo.PinSubType = Pin->PinType.PinSubCategoryObject->GetName();
                        }
                        PinInfo.DefaultValue = Pin->DefaultValue;
                        for (UEdGraphPin* LinkedPin : Pin->LinkedTo)
                        {
                            if (LinkedPin && LinkedPin->GetOwningNode())
                            {
                                FMCPythonPinLinkInfo LinkInfo;
                                LinkInfo.NodeName = LinkedPin->GetOwningNode()->GetName();
                                LinkInfo.NodeTitle = LinkedPin->GetOwningNode()->GetNodeTitle(ENodeTitleType::FullTitle).ToString();
                                FString LinkedFriendly = LinkedPin->PinFriendlyName.ToString();
                                LinkInfo.PinName = LinkedFriendly.IsEmpty() ? LinkedPin->GetName() : LinkedFriendly;
                                PinInfo.LinkedTo.Add(LinkInfo);
                            }
                        }
                        NodeInfo.Pins.Add(PinInfo);
                    }
                    Result.Add(NodeInfo);
                }
            }
        }
    }
    return Result;
}
