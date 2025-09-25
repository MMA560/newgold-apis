"""
All Services for the admin system
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Import database function (assuming the database file is named 'database.py')
from app.database import get_firestore_client

# Configure logging
logger = logging.getLogger(__name__)

# Collection names
PRODUCTS_COLLECTION = "products"
ORDERS_COLLECTION = "orders"
COUNTERS_COLLECTION = "counters"


# ======================= Custom Exceptions =======================

class ServiceError(Exception):
    """Base service error"""
    pass


class ProductServiceError(ServiceError):
    """Product service error"""
    pass


class OrderServiceError(ServiceError):
    """Order service error"""  
    pass


class CustomerServiceError(ServiceError):
    """Customer service error"""
    pass


# ======================= Product Service =======================

class ProductService:
    """Service for managing products"""

    def __init__(self):
        """Initialize product service"""
        pass

    async def _get_client(self) -> firestore.AsyncClient:
        """Get Firestore client"""
        try:
            return await get_firestore_client()
        except Exception as e:
            if "Event loop is closed" in str(e):
                logger.warning("Event loop closed, retrying client creation")
                return await get_firestore_client()
            raise

    def _convert_firestore_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Firestore data types to Python types"""
        import json
        from datetime import datetime
        
        def convert_value(value):
            # Check if it's a timestamp-like object
            if hasattr(value, 'timestamp') and callable(getattr(value, 'timestamp')):
                try:
                    dt = datetime.utcfromtimestamp(value.timestamp())
                    return dt.isoformat() + 'Z'
                except:
                    pass
            
            # Check if it has isoformat method (datetime-like)
            if hasattr(value, 'isoformat') and callable(getattr(value, 'isoformat')):
                try:
                    return value.isoformat()
                except:
                    pass
            
            # If it's a dict, convert recursively
            if isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}
            
            # If it's a list, convert each item
            if isinstance(value, list):
                return [convert_value(item) for item in value]
            
            # Test if it's JSON serializable
            try:
                json.dumps(value)
                return value
            except (TypeError, ValueError):
                return str(value)
        
        try:
            return {key: convert_value(value) for key, value in data.items()}
        except Exception as e:
            logger.error(f"Failed to convert Firestore data: {str(e)}")
            result = {}
            for key, value in data.items():
                try:
                    json.dumps(value)
                    result[key] = value
                except:
                    result[key] = str(value)
            return result

    def _convert_decimals_to_float(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Decimal values to float for Firestore compatibility"""
        converted_data = {}
        for key, value in data.items():
            if isinstance(value, Decimal):
                converted_data[key] = float(value)
            elif isinstance(value, dict):
                converted_data[key] = self._convert_decimals_to_float(value)
            elif isinstance(value, list):
                converted_data[key] = [
                    float(item) if isinstance(item, Decimal) 
                    else self._convert_decimals_to_float(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                converted_data[key] = value
        return converted_data

    async def get_all_products(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all products"""
        try:
            client = await self._get_client()
            collection = client.collection(PRODUCTS_COLLECTION)
            
            docs = []
            async for doc in collection.stream():
                if doc.exists:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    data = self._convert_firestore_data(data)
                    docs.append(data)
            
            # Sort by created_at (newest first)
            docs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            if limit:
                docs = docs[:limit]
            
            logger.info(f"Retrieved {len(docs)} products")
            return docs
            
        except Exception as e:
            logger.error(f"Failed to get all products: {str(e)}")
            raise ProductServiceError(f"Failed to retrieve products: {str(e)}")

    async def update_product(self, product_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update product"""
        try:
            client = await self._get_client()
            doc_ref = client.collection(PRODUCTS_COLLECTION).document(product_id)
            
            # Check if product exists
            doc = await doc_ref.get()
            if not doc.exists:
                raise ProductServiceError(f"Product with ID '{product_id}' not found")
            
            if not update_data:
                # Return existing product if no updates
                data = doc.to_dict()
                data['id'] = product_id
                return self._convert_firestore_data(data)
            
            # Handle fields to delete (with None values)
            fields_to_delete = []
            update_dict = {}
            
            for key, value in update_data.items():
                if value is None:
                    fields_to_delete.append(key)
                else:
                    update_dict[key] = value
            
            # Convert Decimal values to float
            update_dict = self._convert_decimals_to_float(update_dict)
            
            # Add timestamp
            update_dict['updated_at'] = datetime.utcnow().isoformat()
            
            # Update fields
            if update_dict:
                await doc_ref.update(update_dict)
            
            # Delete fields marked for deletion
            if fields_to_delete:
                from google.cloud.firestore import DELETE_FIELD
                delete_dict = {field: DELETE_FIELD for field in fields_to_delete}
                await doc_ref.update(delete_dict)
            
            logger.info(f"Product updated successfully: {product_id}")
            
            # Return updated product
            updated_doc = await doc_ref.get()
            data = updated_doc.to_dict()
            data['id'] = product_id
            return self._convert_firestore_data(data)
            
        except ProductServiceError:
            raise
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {str(e)}")
            raise ProductServiceError(f"Failed to update product: {str(e)}")


# ======================= Order Service =======================

class OrderService:
    """Service for managing orders"""

    def __init__(self):
        """Initialize order service"""
        pass

    async def _get_client(self) -> firestore.AsyncClient:
        """Get Firestore client"""
        try:
            return await get_firestore_client()
        except Exception as e:
            if "Event loop is closed" in str(e):
                logger.warning("Event loop closed, retrying client creation")
                return await get_firestore_client()
            raise

    def _format_order_doc(self, doc, order_id: int) -> Dict[str, Any]:
        """Convert Firestore document to dictionary for detailed display"""
        data = doc.to_dict()
        data['id'] = order_id
        
        # Add missing fields with default values
        defaults = {
            'order_number': f"ORD-{order_id:06d}",
            'order_date': data.get('created_at', datetime.now()),
            'updated_at': datetime.now(),
            'is_read': False,
            'status': 'pending',
            'notes': None
        }
        
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        # Ensure customer_info exists
        if 'customer_info' not in data:
            data['customer_info'] = {}
        
        # Ensure items list exists
        if 'items' not in data:
            data['items'] = []
        
        # Calculate totals if missing
        if 'subtotal' not in data or 'total' not in data:
            subtotal = 0.0
            if isinstance(data.get('items'), list):
                for item in data['items']:
                    if isinstance(item, dict):
                        quantity = item.get('quantity', 0)
                        price = item.get('price', 0)
                        subtotal += quantity * price
                        # Add total_price to each item
                        if 'total_price' not in item:
                            item['total_price'] = quantity * price
                        # Add is_read to each item if missing
                        if 'is_read' not in item:
                            item['is_read'] = False
            
            shipping_fee = data.get('shipping_fee', 0) or data.get('shippingFee', 0)
            total = subtotal + shipping_fee
            
            data['subtotal'] = subtotal
            data['total'] = total
            data['shipping_fee'] = shipping_fee
        
        # Ensure field name consistency
        if 'shippingFee' in data and 'shipping_fee' not in data:
            data['shipping_fee'] = data['shippingFee']
        
        return data

    async def get_all_orders(
        self, 
        page: int = 1, 
        per_page: int = 10, 
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all orders with full data"""
        try:
            client = await self._get_client()
            query = client.collection(ORDERS_COLLECTION)
            
            if status:
                query = query.where(filter=FieldFilter("status", "==", status))
            
            # Order by order_id descending (newest first)
            query = query.order_by("order_id", direction=firestore.Query.DESCENDING)
            all_docs = await query.get()
            
            # Pagination
            total_count = len(all_docs)
            total_pages = (total_count + per_page - 1) // per_page
            offset = (page - 1) * per_page
            limited_docs = all_docs[offset:offset + per_page]
            
            orders = []
            for doc in limited_docs:
                doc_data = doc.to_dict()
                order_id = doc_data.get('order_id', int(doc.id))
                
                # Use formatting function to get detailed data
                full_order_data = self._format_order_doc(doc, order_id)
                orders.append(full_order_data)
            
            return {
                'orders': orders,
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
            
        except Exception as e:
            logger.error(f"Failed to get orders: {str(e)}")
            raise OrderServiceError(f"Failed to retrieve orders: {str(e)}")


# ======================= Customer Service =======================

class CustomerService:
    """Service for managing customers"""

    def __init__(self):
        """Initialize customer service"""
        pass

    async def _get_client(self) -> firestore.AsyncClient:
        """Get Firestore client"""
        try:
            return await get_firestore_client()
        except Exception as e:
            if "Event loop is closed" in str(e):
                logger.warning("Event loop closed, retrying client creation")
                return await get_firestore_client()
            raise

    async def get_all_customers(self) -> List[Dict[str, Any]]:
        """Get all customers from orders"""
        try:
            client = await self._get_client()
            orders_collection = client.collection(ORDERS_COLLECTION)
            
            # Get all orders
            all_orders = await orders_collection.get()
            
            # Group customers by phone number
            customers_dict = {}
            
            for order_doc in all_orders:
                if not order_doc.exists:
                    continue
                    
                order_data = order_doc.to_dict()
                customer_info = order_data.get('customer_info', {})
                
                if not customer_info:
                    continue
                
                phone = customer_info.get('phone_number') or customer_info.get('phoneNumber')
                name = customer_info.get('customer_name') or customer_info.get('customerName')
                address = customer_info.get('full_address') or customer_info.get('fullAddress')
                
                if not phone:
                    continue
                
                order_total = order_data.get('total', 0) or 0
                order_date = order_data.get('order_date') or order_data.get('created_at')
                
                # Convert order_date to datetime if needed
                if hasattr(order_date, 'timestamp'):
                    order_date = datetime.utcfromtimestamp(order_date.timestamp())
                elif isinstance(order_date, str):
                    try:
                        order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                    except:
                        order_date = datetime.now()
                elif order_date is None:
                    order_date = datetime.now()
                
                if phone not in customers_dict:
                    customers_dict[phone] = {
                        'customer_name': name,
                        'phone_number': phone,
                        'full_address': address,
                        'orders_count': 0,
                        'total_spent': 0.0,
                        'first_order_date': order_date,
                        'last_order_date': order_date,
                        'orders': []
                    }
                
                customer = customers_dict[phone]
                customer['orders_count'] += 1
                customer['total_spent'] += float(order_total)
                
                # Update first and last order dates
                if order_date < customer['first_order_date']:
                    customer['first_order_date'] = order_date
                if order_date > customer['last_order_date']:
                    customer['last_order_date'] = order_date
                
                # Update customer info (in case it changed)
                if name:
                    customer['customer_name'] = name
                if address:
                    customer['full_address'] = address
            
            # Convert to list and sort by total_spent
            customers_list = list(customers_dict.values())
            customers_list.sort(key=lambda x: x['total_spent'], reverse=True)
            
            logger.info(f"Retrieved {len(customers_list)} customers")
            return customers_list
            
        except Exception as e:
            logger.error(f"Failed to get customers: {str(e)}")
            raise CustomerServiceError(f"Failed to retrieve customers: {str(e)}")


# ======================= Service Instances =======================

# Create service instances
product_service = ProductService()
order_service = OrderService()
customer_service = CustomerService()