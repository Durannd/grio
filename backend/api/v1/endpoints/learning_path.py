from fastapi import APIRouter, Depends
from core.neo4j import get_driver
from core.deps import get_current_user
from models.user import User
from crud.learning_path import get_user_learning_path, get_full_learning_path
from core.translator import mask_id, get_friendly_name, get_friendly_code

router = APIRouter()

@router.get("/")
def read_learning_path(
    current_user: User = Depends(get_current_user),
    db_driver = Depends(get_driver)
):
    path = get_user_learning_path(db_driver, current_user.id)
    # Mascarar IDs e adicionar nomes amigáveis
    for item in path:
        original_id = item["concept_name"]
        db_name = item.get("friendly_name")
        item["display_name"] = get_friendly_name(original_id, db_name)
        item["friendly_code"] = get_friendly_code(original_id)
        item["concept_name"] = mask_id(original_id)
    return {"learning_path": path}

@router.get("/full")
def read_full_learning_path(
    current_user: User = Depends(get_current_user),
    db_driver = Depends(get_driver)
):
    path = get_full_learning_path(db_driver, current_user.id)
    # Mascarar IDs e adicionar nomes amigáveis
    for item in path:
        original_id = item["concept_name"]
        db_name = item.get("friendly_name")
        item["display_name"] = get_friendly_name(original_id, db_name)
        item["friendly_code"] = get_friendly_code(original_id)
        item["concept_name"] = mask_id(original_id)
    return {"learning_path": path}
