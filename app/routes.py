"""
API Routes - All endpoints for the admin system
"""

import os
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query, Path, Body, status, Depends

# Import services and schemas
from app.services import product_service, order_service, customer_service
from app.services import ProductServiceError, OrderServiceError, CustomerServiceError
from app.schemas import (
    ProductResponse, 
    ProductUpdate, 
    OrderListResponse, 
    CustomersListResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# API Key from environment variable
API_KEY = os.getenv("ADMIN_API_KEY", "sk_admin_2024_abc123")

# Create main router
router = APIRouter()


# ======================= API Key Protection =======================

async def verify_api_key(x_api_key: str = Header(..., description="API Key required for access")):
    """Verify API Key in request headers"""
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return x_api_key


# ======================= API Routes =======================

# Root endpoint
@router.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Admin Management System API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/products",
            "orders": "/orders", 
            "customers": "/customers"
        }
    }


# Health check
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "admin-management-system"
    }


# ======================= Products API =======================

@router.get(
    "/products",
    response_model=List[ProductResponse],
    tags=["Products"],
    summary="Get all products",
    description="جلب جميع المنتجات مع إمكانية التحكم في العدد",
    dependencies=[Depends(verify_api_key)]
)
async def get_all_products(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="عدد المنتجات المطلوب جلبها")
):
    """
    API 1: جلب جميع المنتجات
    """
    try:
        logger.info(f"Getting all products with limit: {limit}")
        products = await product_service.get_all_products(limit=limit)
        logger.info(f"Successfully retrieved {len(products)} products")
        return products
        
    except ProductServiceError as e:
        logger.error(f"Product service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.put(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Update product",
    description="تعديل منتج موجود",
    dependencies=[Depends(verify_api_key)]
)
async def update_product(
    product_id: str = Path(..., description="معرف المنتج"),
    update_data: ProductUpdate = Body(..., description="بيانات التحديث")
):
    """
    API 2: تعديل المنتج
    """
    try:
        logger.info(f"Updating product: {product_id}")
        update_dict = update_data.dict(exclude_unset=True)
        updated_product = await product_service.update_product(product_id, update_dict)
        logger.info(f"Successfully updated product: {product_id}")
        return updated_product
        
    except ProductServiceError as e:
        logger.error(f"Product service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


# ======================= Orders API =======================

@router.get(
    "/orders",
    tags=["Orders"],
    summary="Get all orders",
    description="جلب جميع الطلبات مع التقسيم إلى صفحات",
    dependencies=[Depends(verify_api_key)]
)
async def get_all_orders(
    page: int = Query(1, ge=1, description="رقم الصفحة"),
    per_page: int = Query(10, ge=1, le=100, description="عدد الطلبات في الصفحة"),
    status: Optional[str] = Query(None, description="تصفية حسب الحالة")
):
    """
    API 3: جلب جميع الطلبات
    """
    try:
        logger.info(f"Getting orders - Page: {page}, Per page: {per_page}, Status: {status}")
        orders_data = await order_service.get_all_orders(
            page=page,
            per_page=per_page,
            status=status
        )
        logger.info(f"Successfully retrieved {len(orders_data.get('orders', []))} orders")
        return orders_data
        
    except OrderServiceError as e:
        logger.error(f"Order service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


# ======================= Customers API =======================

@router.get(
    "/customers",
    response_model=CustomersListResponse,
    tags=["Customers"],
    summary="Get all customers",
    description="جلب بيانات جميع العملاء من الطلبات",
    dependencies=[Depends(verify_api_key)]
)
async def get_all_customers():
    """
    API 4: جلب بيانات العملاء من الطلبات
    يجمع بيانات العملاء من جميع الطلبات ويعرض إحصائيات كل عميل
    """
    try:
        logger.info("Getting all customers from orders")
        customers = await customer_service.get_all_customers()
        
        response_data = {
            "customers": customers,
            "total_count": len(customers)
        }
        
        logger.info(f"Successfully retrieved {len(customers)} unique customers from orders")
        return response_data
        
    except CustomerServiceError as e:
        logger.error(f"Customer service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting customers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )