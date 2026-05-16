from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.llm_config import LLMConfigCreate, LLMConfigOut, LLMConfigTestResult, LLMConfigUpdate
from app.services.llm_config_service import LLMConfigService

router = APIRouter(prefix="/llm-configs", tags=["llm-configs"])


@router.get("", response_model=list[LLMConfigOut])
def list_llm_configs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return LLMConfigService(db).list_for_user(current_user.id)


@router.post("", response_model=LLMConfigOut)
def create_llm_config(payload: LLMConfigCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return LLMConfigService(db).create(payload, current_user.id)


@router.patch("/{config_id}", response_model=LLMConfigOut)
def update_llm_config(
    config_id: str,
    payload: LLMConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return LLMConfigService(db).update(config_id, payload, current_user.id)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_llm_config(config_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    LLMConfigService(db).delete(config_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{config_id}/test", response_model=LLMConfigTestResult)
async def test_llm_config(config_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await LLMConfigService(db).test(config_id, current_user.id)


@router.post("/{config_id}/set-default", response_model=LLMConfigOut)
def set_default_llm_config(config_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return LLMConfigService(db).set_default(config_id, current_user.id)
