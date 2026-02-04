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
                    NodeInfo.NodeClass = Node->GetClass()->GetName();
                    NodeInfo.NodePath = Node->GetPathName();
                    for (UEdGraphPin* Pin : Node->Pins)
                    {
                        if (!Pin) continue;
                        FMCPythonBlueprintPinInfo PinInfo;
                        PinInfo.PinName = Pin->GetName();
                        PinInfo.Direction = (Pin->Direction == EGPD_Input) ? TEXT("Input") : TEXT("Output");
                        PinInfo.PinType = Pin->PinType.PinCategory.ToString();
                        for (UEdGraphPin* LinkedPin : Pin->LinkedTo)
                        {
                            if (LinkedPin && LinkedPin->GetOwningNode())
                            {
                                PinInfo.LinkedToNodeNames.Add(LinkedPin->GetOwningNode()->GetName());
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
