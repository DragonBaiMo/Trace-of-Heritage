"""数据导出接口。"""
from datetime import datetime
from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_roles
from app.localization.messages import MESSAGES
from app.models.resource import Resource
from app.models.user import User

router = APIRouter(prefix="/admin/export", tags=["导出"])


@router.get("/")
def export_data(
    data_type: str = Query(..., regex="^(users|resources)$", description="导出类型 users/resources"),
    db: Session = Depends(get_db_session),
    _=Depends(require_roles("admin")),
):
    """导出用户或资源数据为 Excel。"""

    now = datetime.now().strftime("%Y%m%d%H%M%S")
    if data_type == "users":
        rows = db.query(User).all()
        payload = [
            {
                "用户ID": item.id,
                "用户名": item.username,
                "昵称": item.nickname,
                "角色": item.role,
                "状态": item.status,
                "创建时间": item.created_at,
            }
            for item in rows
        ]
    elif data_type == "resources":
        rows = db.query(Resource).all()
        payload = [
            {
                "资源ID": item.id,
                "标题": item.title,
                "类型": item.resource_type,
                "流派": item.genre,
                "标签": ",".join(item.tags or []),
                "状态": item.status,
                "提交人": item.submitter_id,
                "更新时间": item.updated_at,
            }
            for item in rows
        ]
    else:
        raise HTTPException(status_code=400, detail="不支持的导出类型")

    df = pd.DataFrame(payload)
    stream = BytesIO()
    df.to_excel(stream, index=False)
    stream.seek(0)
    filename = f"{data_type}_{now}.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
        background=None,
    )
