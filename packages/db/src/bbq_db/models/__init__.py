"""Tabele PostgreSQL.

| Tabela          | Używana przez                              |
|-----------------|--------------------------------------------|
| ``products``    | SQLi (wyszukiwarka), race condition (stan) |
| ``admin_secrets``| SQLi (cel ataku)                          |
| ``orders``      | N+1, wielokrotne wykonanie operacji        |
| ``order_items`` | N+1                                        |
| ``coupons``     | race condition (kupon jednorazowy)         |
"""

from bbq_db.models.coupon import Coupon
from bbq_db.models.order import Order, OrderItem
from bbq_db.models.product import Product
from bbq_db.models.secret import AdminSecret

__all__ = ["AdminSecret", "Coupon", "Order", "OrderItem", "Product"]
