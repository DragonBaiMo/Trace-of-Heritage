"""积分商城服务。"""
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models.product import Order, Product, UserPoint
from app.utils.exceptions import BusinessException


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, *, page: int, page_size: int) -> Tuple[list[Product], int]:
        q = self.db.query(Product).filter(Product.status == "active")
        total = q.count()
        items = (
            q.order_by(Product.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    # ----- Admin operations -----
    def admin_list_products(
        self,
        *,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Tuple[list[Product], int]:
        q = self.db.query(Product)
        if status:
            q = q.filter(Product.status == status)
        if keyword:
            like = f"%{keyword}%"
            q = q.filter(Product.title.like(like))
        total = q.count()
        items = (
            q.order_by(Product.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create_product(
        self,
        *,
        title: str,
        cover: Optional[str],
        price: Optional[float],
        points_price: int,
        stock: int,
        status: str = "active",
    ) -> Product:
        p = Product(
            title=title,
            cover=cover,
            price=price,
            points_price=points_price,
            stock=stock,
            status=status,
        )
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def update_product(
        self,
        *,
        product: Product,
        title: Optional[str] = None,
        cover: Optional[str] = None,
        price: Optional[float] = None,
        points_price: Optional[int] = None,
        stock: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Product:
        if title is not None:
            product.title = title
        if cover is not None:
            product.cover = cover
        if price is not None:
            product.price = price
        if points_price is not None:
            product.points_price = int(points_price)
        if stock is not None:
            product.stock = int(stock)
        if status is not None:
            product.status = status
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def ensure_points_row(self, user_id: int) -> UserPoint:
        pts = self.db.query(UserPoint).filter(UserPoint.user_id == user_id).first()
        if not pts:
            pts = UserPoint(user_id=user_id, balance=0)
            self.db.add(pts)
            self.db.commit()
            self.db.refresh(pts)
        return pts

    def get_points(self, user_id: int) -> UserPoint:
        return self.ensure_points_row(user_id)

    def create_order(self, *, user_id: int, product_id: int, quantity: int) -> Order:
        product = self.db.query(Product).filter(Product.id == product_id, Product.status == "active").first()
        if not product:
            raise BusinessException("商品不存在或已下架")
        if product.stock < quantity:
            raise BusinessException("库存不足")
        total_points = int(product.points_price) * int(quantity)
        points = self.ensure_points_row(user_id)
        if points.balance < total_points:
            raise BusinessException("积分不足")
        # 扣减库存与积分
        product.stock -= quantity
        points.balance -= total_points
        order = Order(
            user_id=user_id,
            product_id=product.id,
            quantity=quantity,
            points_cost=total_points,
            status="pending",
        )
        self.db.add_all([product, points, order])
        self.db.commit()
        self.db.refresh(order)
        return order

    def list_orders(self, *, user_id: int, page: int, page_size: int) -> Tuple[list[Order], int]:
        q = self.db.query(Order).filter(Order.user_id == user_id)
        total = q.count()
        items = (
            q.order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def admin_list_orders(
        self,
        *,
        page: int,
        page_size: int,
        status: Optional[str] = None,
    ) -> Tuple[list[Order], int]:
        q = self.db.query(Order)
        if status:
            q = q.filter(Order.status == status)
        total = q.count()
        items = (
            q.order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def ship_order(self, *, order: Order, remark: Optional[str] = None) -> Order:
        if order.status != "pending":
            raise BusinessException("仅待发货订单可发货")
        order.status = "shipped"
        order.shipping_remark = remark
        order.shipped_at = datetime.utcnow()
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def confirm_order(self, *, order: Order, user_id: int) -> Order:
        if order.user_id != user_id:
            raise BusinessException("无法操作他人订单")
        if order.status not in {"pending", "shipped"}:
            raise BusinessException("当前状态不可确认收货")
        order.status = "completed"
        order.confirmed_at = datetime.utcnow()
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
