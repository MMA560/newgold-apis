# Admin Management System API

نظام إدارة شامل للمنتجات والطلبات والعملاء باستخدام FastAPI و Firebase Firestore.

## الميزات

- ✅ **4 APIs رئيسية** للإدارة الكاملة
- 🔐 **حماية API Key** لجميع المسارات
- 🔥 **Firebase Firestore** كقاعدة بيانات
- ⚡ **FastAPI** للأداء العالي
- 📊 **معالجة البيانات المتقدمة**

---

## التثبيت والإعداد

### 1. تثبيت المتطلبات

```bash
# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # على Windows: venv\Scripts\activate

# تثبيت المتطلبات
pip install -r requirements.txt
```

### 2. إعداد متغيرات البيئة

إنشئ ملف `.env` في المجلد الجذر:

```env
# Firebase Configuration
GCP_FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project",...}
GCP_PROJECT_ID=your-firebase-project-id

# API Security
ADMIN_API_KEY=your-super-secret-api-key-here

# Application Settings
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### 3. تشغيل الخادم

```bash
# الطريقة الأولى
python main.py

# الطريقة الثانية
python routes.py

# الطريقة الثالثة
uvicorn routes:app --host 0.0.0.0 --port 8000 --reload
```

الخادم سيعمل على: **http://localhost:8000**

---

## المسارات (APIs)

### 🔐 متطلبات المصادقة

**جميع المسارات تتطلب API Key في الـ Header:**

```http
X-API-Key: your-secret-api-key-here
```

---

## 1. إدارة المنتجات

### جلب جميع المنتجات

```http
GET /products
```

**المعاملات (اختيارية):**
- `limit`: عدد المنتجات (1-1000)

**مثال:**

```bash
curl -H "X-API-Key: your-secret-api-key-here" \
     "http://localhost:8000/products?limit=50"
```

**الاستجابة:**

```json
[
  {
    "id": "product_1",
    "title": "اسم المنتج",
    "images": ["url1.jpg", "url2.jpg"],
    "category": "electronics",
    "price": 299.99,
    "stock": 50,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

### تعديل منتج

```http
PUT /products/{product_id}
```

**مثال:**

```bash
curl -X PUT \
     -H "X-API-Key: your-secret-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "اسم المنتج الجديد",
       "price": 350.00,
       "stock": 25,
       "discount": 10
     }' \
     "http://localhost:8000/products/product_1"
```

**Body المطلوب:**

```json
{
  "title": "اسم المنتج الجديد",
  "price": 350.00,
  "stock": 25,
  "discount": 10,
  "category": "new_category",
  "images": ["new_image1.jpg", "new_image2.jpg"],
  "description": "وصف المنتج الجديد"
}
```

**ملاحظات:**
- جميع الحقول اختيارية
- لحذف حقل، ضع قيمته `null`
- سيتم حفظ التغييرات وإرجاع المنتج المحدث

---

## 2. إدارة الطلبات

### جلب جميع الطلبات

```http
GET /orders
```

**المعاملات (اختيارية):**
- `page`: رقم الصفحة (افتراضي: 1)
- `per_page`: عدد الطلبات في الصفحة (1-100، افتراضي: 10)
- `status`: تصفية حسب الحالة (`pending`, `confirmed`, `in_delivery`, `delivered`, `canceled`)

**مثال:**

```bash
curl -H "X-API-Key: your-secret-api-key-here" \
     "http://localhost:8000/orders?page=1&per_page=20&status=pending"
```

**الاستجابة:**

```json
{
  "orders": [
    {
      "id": 1,
      "order_number": "ORD-000001",
      "customer_info": {
        "customer_name": "أحمد محمد",
        "phone_number": "01234567890",
        "full_address": "القاهرة، مصر"
      },
      "items": [
        {
          "product_id": "product_1",
          "title": "اسم المنتج",
          "quantity": 2,
          "price": 100.00,
          "total_price": 200.00
        }
      ],
      "subtotal": 200.00,
      "shipping_fee": 25.00,
      "total": 225.00,
      "status": "pending",
      "order_date": "2024-01-01T12:00:00Z",
      "is_read": false
    }
  ],
  "total_count": 150,
  "page": 1,
  "per_page": 20,
  "total_pages": 8
}
```

---

## 3. إدارة العملاء

### جلب بيانات العملاء

```http
GET /customers
```

**مثال:**

```bash
curl -H "X-API-Key: your-secret-api-key-here" \
     "http://localhost:8000/customers"
```

**الاستجابة:**

```json
{
  "customers": [
    {
      "customer_name": "أحمد محمد",
      "phone_number": "01234567890",
      "full_address": "القاهرة، مصر",
      "orders_count": 5,
      "total_spent": 1250.00,
      "first_order_date": "2024-01-01T10:00:00Z",
      "last_order_date": "2024-01-15T14:30:00Z"
    }
  ],
  "total_count": 50
}
```

---

## 4. مسارات إضافية

### الصفحة الرئيسية

```http
GET /
```

**الاستجابة:**

```json
{
  "message": "Admin Management System API",
  "version": "1.0.0",
  "endpoints": {
    "products": "/products",
    "orders": "/orders",
    "customers": "/customers"
  }
}
```

### فحص الصحة

```http
GET /health
```

**الاستجابة:**

```json
{
  "status": "healthy",
  "service": "admin-management-system"
}
```

---

## أمثلة عملية

### مثال JavaScript (Fetch API)

```javascript
const API_KEY = 'your-secret-api-key-here';
const BASE_URL = 'http://localhost:8000';

// جلب المنتجات
async function getProducts() {
  const response = await fetch(`${BASE_URL}/products`, {
    headers: {
      'X-API-Key': API_KEY
    }
  });
  const products = await response.json();
  console.log(products);
}

// تعديل منتج
async function updateProduct(productId, data) {
  const response = await fetch(`${BASE_URL}/products/${productId}`, {
    method: 'PUT',
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  const updatedProduct = await response.json();
  console.log(updatedProduct);
}

// جلب الطلبات
async function getOrders(page = 1) {
  const response = await fetch(`${BASE_URL}/orders?page=${page}`, {
    headers: {
      'X-API-Key': API_KEY
    }
  });
  const orders = await response.json();
  console.log(orders);
}
```

### مثال Python (Requests)

```python
import requests

API_KEY = 'your-secret-api-key-here'
BASE_URL = 'http://localhost:8000'
headers = {'X-API-Key': API_KEY}

# جلب المنتجات
def get_products():
    response = requests.get(f'{BASE_URL}/products', headers=headers)
    return response.json()

# تعديل منتج
def update_product(product_id, data):
    response = requests.put(
        f'{BASE_URL}/products/{product_id}',
        headers={**headers, 'Content-Type': 'application/json'},
        json=data
    )
    return response.json()

# جلب العملاء
def get_customers():
    response = requests.get(f'{BASE_URL}/customers', headers=headers)
    return response.json()
```

---

## معالجة الأخطاء

### رموز الاستجابة

- `200` - نجح الطلب
- `401` - API Key غير صحيح
- `404` - المورد غير موجود
- `422` - بيانات غير صحيحة
- `500` - خطأ في الخادم

### أمثلة الأخطاء

```json
{
  "success": false,
  "message": "Invalid API Key",
  "error_code": "HTTP_401"
}
```

```json
{
  "success": false,
  "message": "Product with ID 'xyz' not found",
  "error_code": "HTTP_400"
}
```

---

## الأمان

### حماية API Key

1. **لا تشارك** الـ API Key في الكود العام
2. **استخدم HTTPS** في الإنتاج
3. **غير API Key** بانتظام
4. **راقب الطلبات** غير المصرح بها

### تغيير API Key

```bash
# في ملف .env
ADMIN_API_KEY=new-super-secret-key-12345

# إعادة تشغيل الخادم
python main.py
```

---

## استكشاف الأخطاء

### المشاكل الشائعة

1. **خطأ 401 - Unauthorized**
   - تأكد من وضع `X-API-Key` في الـ Header
   - تأكد من صحة قيمة API Key

2. **خطأ Firebase**
   - تأكد من صحة `GCP_FIREBASE_CREDENTIALS_JSON`
   - تأكد من وجود `GCP_PROJECT_ID`

3. **خطأ في تثبيت المتطلبات**
   - استخدم بيئة افتراضية جديدة
   - تأكد من إصدار Python (3.8+)

### تفعيل وضع Debug

```bash
# في ملف .env
DEBUG=true

# أو تشغيل مع uvicorn
uvicorn routes:app --reload --log-level debug
```

---

## هيكل المشروع

```
project/
├── main.py              # نقطة البداية
├── routes.py            # المسارات والـ APIs
├── services.py          # منطق العمليات
├── schemas.py           # نماذج البيانات
├── database.py          # إعداد Firebase
├── requirements.txt     # المتطلبات
├── .env                # متغيرات البيئة
└── README.md           # دليل الاستخدام
```

---

## الدعم

لأي مشاكل أو استفسارات، تأكد من:

1. قراءة هذا الدليل كاملاً
2. فحص ملفات الـ logs
3. التأكد من إعداد Firebase
4. التأكد من صحة API Key

---

## الترخيص

هذا المشروع للاستخدام الداخلي فقط.