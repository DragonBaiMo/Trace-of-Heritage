"""积分商城接口。"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.schemas.common import PaginationMeta, ResponseModel
from app.schemas.product import (
    OrderCreate,
    OrderRead,
    OrderShipRequest,
    PointsRead,
    ProductRead,
    ProductCreate,
    ProductUpdate,
)
from app.services.product_service import ProductService
from app.utils.request import extract_client_ip
from app.localization.messages import MESSAGES
from app.utils.exceptions import BusinessException
from app.models.product import Order

router = APIRouter(prefix="/shop", tags=["积分商城"])


@router.get("/products", response_model=ResponseModel[list[ProductRead]])
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[ProductRead]]:
    items, total = ProductService(db).list_products(page=page, page_size=page_size)
    return ResponseModel(code=0, message="ok", data=[ProductRead.from_orm(x) for x in items], meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.get("/points/me", response_model=ResponseModel[PointsRead])
def get_my_points(current_user=Depends(get_current_user), db: Session = Depends(get_db_session)) -> ResponseModel[PointsRead]:
    pts = ProductService(db).get_points(current_user.id)
    return ResponseModel(code=0, message="ok", data=PointsRead(balance=int(pts.balance)))


@router.post("/orders", response_model=ResponseModel[OrderRead])
def create_order(payload: OrderCreate, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db_session)) -> ResponseModel[OrderRead]:
    svc = ProductService(db)
    try:
        order = svc.create_order(user_id=current_user.id, product_id=payload.product_id, quantity=payload.quantity)
    except BusinessException as exc:  # BusinessException 等
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ResponseModel(code=0, message=MESSAGES["order_created"], data=OrderRead.from_orm(order))


@router.get("/orders", response_model=ResponseModel[list[OrderRead]])
def list_my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[OrderRead]]:
    """用户查看自己的订单。"""

    svc = ProductService(db)
    items, total = svc.list_orders(user_id=current_user.id, page=page, page_size=page_size)
    return ResponseModel(
        code=0,
        message="ok",
        data=[OrderRead.from_orm(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/orders/{order_id}/confirm", response_model=ResponseModel[OrderRead])
def confirm_order(order_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db_session)) -> ResponseModel[OrderRead]:
    """用户确认收货。"""

    svc = ProductService(db)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    try:
        updated = svc.confirm_order(order=order, user_id=current_user.id)
    except BusinessException as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ResponseModel(code=0, message=MESSAGES["order_confirmed"], data=OrderRead.from_orm(updated))


@router.get("/admin/orders", dependencies=[Depends(require_roles("admin"))], response_model=ResponseModel[list[OrderRead]])
def admin_list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[OrderRead]]:
    """管理员查看订单列表。"""

    svc = ProductService(db)
    items, total = svc.admin_list_orders(page=page, page_size=page_size, status=status)
    return ResponseModel(
        code=0,
        message="ok",
        data=[OrderRead.from_orm(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/admin/orders/{order_id}/ship", dependencies=[Depends(require_roles("admin"))], response_model=ResponseModel[OrderRead])
def ship_order(order_id: int, payload: OrderShipRequest, db: Session = Depends(get_db_session)) -> ResponseModel[OrderRead]:
    """管理员发货。"""

    svc = ProductService(db)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    try:
        updated = svc.ship_order(order=order, remark=payload.remark)
    except BusinessException as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ResponseModel(code=0, message=MESSAGES["order_shipped"], data=OrderRead.from_orm(updated))


# ----- Admin management -----
@router.get("/admin/products", dependencies=[Depends(require_roles("admin"))], response_model=ResponseModel[list[ProductRead]])
def admin_list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[ProductRead]]:
    items, total = ProductService(db).admin_list_products(page=page, page_size=page_size, status=status, keyword=keyword)
    return ResponseModel(code=0, message="ok", data=[ProductRead.from_orm(x) for x in items], meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/admin/products", dependencies=[Depends(require_roles("admin"))], response_model=ResponseModel[ProductRead])
def admin_create_product(payload: ProductCreate, db: Session = Depends(get_db_session)) -> ResponseModel[ProductRead]:
    svc = ProductService(db)
    p = svc.create_product(
        title=payload.title,
        cover=payload.cover,
        price=payload.price,
        points_price=payload.points_price,
        stock=payload.stock,
        status=payload.status,
    )
    return ResponseModel(code=0, message="ok", data=ProductRead.from_orm(p))


@router.patch("/admin/products/{product_id}", dependencies=[Depends(require_roles("admin"))], response_model=ResponseModel[ProductRead])
def admin_update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db_session)) -> ResponseModel[ProductRead]:
    svc = ProductService(db)
    from app.models.product import Product

    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="商品不存在")
    updated = svc.update_product(
        product=p,
        title=payload.title,
        cover=payload.cover,
        price=payload.price,
        points_price=payload.points_price,
        stock=payload.stock,
        status=payload.status,
    )
    return ResponseModel(code=0, message="ok", data=ProductRead.from_orm(updated))
