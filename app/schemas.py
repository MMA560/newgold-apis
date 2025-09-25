"""
All Pydantic schemas for the admin system
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal


# ======================= Product Schemas =======================

class Section(BaseModel):
    """Represents a section within product details."""
    title: str = Field(..., min_length=1, max_length=200, description="Section title")
    items: List[str] = Field(..., min_items=1, description="List of items in the section")


class Details(BaseModel):
    """Detailed information about a product."""
    description: str = Field(..., min_length=10, description="Detailed product description")
    sections: List[Section] = Field(..., min_items=1, description="Product detail sections")


class FAQItem(BaseModel):
    """Frequently Asked Question item."""
    question: str = Field(..., min_length=5, max_length=500, description="FAQ question")
    answer: str = Field(..., min_length=10, description="FAQ answer")


class ProductVideo(BaseModel):
    """Product video information model."""
    title: Optional[str] = Field(None, description="Video section title")
    videoUrl: str = Field(..., description="Video URL")
    thumbnail: str = Field(..., description="Video thumbnail image URL")
    overlayText: Optional[str] = Field(None, description="Text overlay on video thumbnail")
    descriptionTitle: Optional[str] = Field(None, description="Video description title")
    description: Optional[str] = Field(None, description="Video description text")


class ProductVariant(BaseModel):
    """Product variant model for different colors/options."""
    id: str = Field(..., description="Variant identifier")
    color: str = Field(..., description="Variant color")
    image: str = Field(..., description="Variant image URL")
    stock: int = Field(..., ge=0, description="Available stock for this variant")
    price: Optional[str] = Field(None, description="Variant price")


class ProductUpdate(BaseModel):
    """Model for updating an existing product."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    images: Optional[List[str]] = Field(None, min_items=1)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    categories: Optional[List[str]] = Field(None, min_items=1)
    description: Optional[str] = Field(None, min_length=10)
    short_description: Optional[str] = Field(None, min_length=5, max_length=300)
    price: Optional[Decimal] = Field(None, gt=0)
    old_price: Optional[Decimal] = Field(None, gt=0)
    discount: Optional[Decimal] = Field(None, ge=0, le=100)
    usage_instructions: Optional[str] = None
    storage_instructions: Optional[str] = None
    details: Optional[Details] = None
    faq: Optional[List[FAQItem]] = None
    rating: Optional[float] = Field(None, description="Rating of the product")
    reviewCount: Optional[int] = Field(None, description="Reviews count")
    base_price: Optional[float] = Field(None, description="Original price without profit")
    variants: Optional[List[ProductVariant]] = Field(None, description="Product variants")
    videoInfo: Optional[ProductVideo] = Field(None, description="Product video information")
    sku: Optional[str] = Field(None, description="Product SKU")
    brand: Optional[str] = Field(None, description="Product brand")
    stock: Optional[int] = Field(None, ge=0, description="Available stock")


class ProductResponse(BaseModel):
    """Model for product response."""
    id: str = Field(..., description="Unique product identifier")
    title: str = Field(..., description="Product title")
    images: List[str] = Field(..., description="List of product image URLs")
    category: str = Field(..., description="Product category")
    categories: Optional[List[str]] = Field(None, description="Product categories")
    description: str = Field(..., description="Product description")
    short_description: str = Field(..., description="Short product description")
    price: float = Field(..., description="Product price")
    old_price: Optional[float] = Field(None, description="Previous price if on sale")
    discount: Optional[float] = Field(None, description="Discount percentage")
    usage_instructions: Optional[str] = None
    storage_instructions: Optional[str] = None
    details: Optional[Details] = None
    faq: Optional[List[FAQItem]] = None
    rating: Optional[float] = Field(None, description="Product rating")
    reviewCount: Optional[int] = Field(None, description="Review count")
    base_price: Optional[float] = Field(None, description="Base price")
    variants: Optional[List[ProductVariant]] = Field(None, description="Product variants")
    videoInfo: Optional[ProductVideo] = Field(None, description="Video info")
    sku: Optional[str] = Field(None, description="Product SKU")
    brand: Optional[str] = Field(None, description="Product brand")
    stock: Optional[int] = Field(None, description="Available stock")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


# ======================= Order Schemas =======================

class OrderStatus(str, Enum):
    """حالات الطلب"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class OrderItem(BaseModel):
    """عنصر الطلب"""
    product_id: Optional[str] = Field(None, description="معرف المنتج")
    title: Optional[str] = Field(None, description="عنوان المنتج")
    image: Optional[str] = Field(None, description="رابط صورة المنتج")
    quantity: Optional[int] = Field(None, description="الكمية")
    price: Optional[float] = Field(None, description="السعر")
    base_price: Optional[float] = Field(None, description="السعر الأساسي")
    total_price: Optional[float] = Field(None, description="السعر الإجمالي للعنصر")
    variant_id: Optional[str] = Field(None, description="معرف التنويع")
    variant_name: Optional[str] = Field(None, description="اسم التنويع")
    is_read: Optional[bool] = Field(None, description="حالة القراءة")


class CustomerInfo(BaseModel):
    """معلومات العميل"""
    customer_name: Optional[str] = Field(None, description="اسم العميل")
    phone_number: Optional[str] = Field(None, description="رقم الهاتف")
    full_address: Optional[str] = Field(None, description="العنوان الكامل")


class OrderResponse(BaseModel):
    """استجابة الطلب"""
    id: Optional[int] = Field(None, description="معرف الطلب")
    order_number: Optional[str] = Field(None, description="رقم الطلب")
    customer_info: Optional[CustomerInfo] = Field(None, description="معلومات العميل")
    items: Optional[List[OrderItem]] = Field(None, description="عناصر الطلب")
    subtotal: Optional[float] = Field(None, description="المجموع الفرعي")
    shipping_fee: Optional[float] = Field(None, description="رسوم الشحن")
    total: Optional[float] = Field(None, description="الإجمالي النهائي")
    status: Optional[OrderStatus] = Field(None, description="حالة الطلب")
    order_date: Optional[datetime] = Field(None, description="تاريخ الطلب")
    updated_at: Optional[datetime] = Field(None, description="تاريخ آخر تحديث")
    notes: Optional[str] = Field(None, description="ملاحظات إضافية")
    is_read: Optional[bool] = Field(None, description="حالة القراءة")


class OrderListResponse(BaseModel):
    """قائمة الطلبات"""
    orders: Optional[List[OrderResponse]] = Field(None, description="قائمة الطلبات")
    total_count: Optional[int] = Field(None, description="العدد الإجمالي")
    page: Optional[int] = Field(None, description="رقم الصفحة")
    per_page: Optional[int] = Field(None, description="عدد العناصر في الصفحة")
    total_pages: Optional[int] = Field(None, description="العدد الإجمالي للصفحات")


# ======================= Customer Schemas =======================

class CustomerResponse(BaseModel):
    """استجابة بيانات العميل"""
    customer_name: Optional[str] = Field(None, description="اسم العميل")
    phone_number: Optional[str] = Field(None, description="رقم الهاتف")
    full_address: Optional[str] = Field(None, description="العنوان الكامل")
    orders_count: Optional[int] = Field(None, description="عدد الطلبات")
    total_spent: Optional[float] = Field(None, description="إجمالي المبلغ المنفق")
    last_order_date: Optional[datetime] = Field(None, description="تاريخ آخر طلب")
    first_order_date: Optional[datetime] = Field(None, description="تاريخ أول طلب")


class CustomersListResponse(BaseModel):
    """قائمة العملاء"""
    customers: List[CustomerResponse] = Field(..., description="قائمة العملاء")
    total_count: int = Field(..., description="العدد الإجمالي للعملاء")


# ======================= API Response Schemas =======================

class APIResponse(BaseModel):
    """استجابة عامة للـ API"""
    success: bool = Field(..., description="حالة النجاح")
    message: str = Field(..., description="رسالة الاستجابة")
    data: Optional[dict] = Field(None, description="البيانات")


class ErrorResponse(BaseModel):
    """استجابة الخطأ"""
    success: bool = Field(False, description="حالة النجاح")
    message: str = Field(..., description="رسالة الخطأ")
    error_code: Optional[str] = Field(None, description="كود الخطأ")