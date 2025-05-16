# editor_actions.py

import unreal
import json

def ue_get_selected_assets() -> str:
    """Gets the set of currently selected assets."""
    try:
        selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
        
        # Object 객체를 시리얼라이즈할 수 있는 형태로 변환
        serialized_assets = []
        for asset in selected_assets:
            serialized_assets.append({
                "asset_name": asset.get_name(),  # 에셋 이름
                "asset_path": asset.get_path_name(),  # 에셋 경로
                "asset_class": asset.get_class().get_name(),  # 에셋 클래스 이름
                # 필요한 다른 속성 추가 가능
            })
        
        return json.dumps({"success": True, "selected_assets": serialized_assets})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e)})