# ecom-django-fullstack

A full-stack e-commerce web application built with Django, DaisyUI, and Tailwind CSS. The platform supports customers, managers, and riders — each with their own dashboard and workflows.

---

## Features

### Customer
- Browse products with search, category, and price filters
- Product detail page with reviews and ratings
- Cart management (authenticated + guest session cart, merged on login)
- Place orders with delivery address selection
- Order history with detail view
- Order tracking (real-time status events)
- Cancel unpaid orders
- Pay for pending orders (bKash, Nagad, SSLCommerz, COD)

### Manager
- Manage products and categories (add, edit, images)
- View and filter all orders by status and payment
- Assign riders to orders with zone/area/city/country matching algorithm
- Cancel orders (with automatic inventory restoration)
- Review rider applications (approve/reject)
- Manage rider profiles

### Rider
- Apply to become a rider
- View assigned orders
- Update order status sequentially: Assigned → Picked Up → On the Way → Delivered
- View delivery address and customer details

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.x |
| Auth | django-allauth |
| Frontend | Tailwind CSS + DaisyUI |
| Database | PostgreSQL (or SQLite for dev) |
| File Storage | Django media files |
| Payment | bKash, Nagad, SSLCommerz, COD |

---

## Apps Overview

### `core`
Handles public-facing pages — homepage, shop listing, product detail, category listing, about page.

### `product`
Models: `Category`, `Product`, `ProductImage`, `CategoryImage`, `Inventory`, `QuantityHistory`, `PriceHistory`, `Review`

Key design decisions:
- `created_by` stored as plain `IntegerField` for scalability
- `Inventory` is a separate `OneToOne` model — price and quantity decoupled from product
- `QuantityHistory` and `PriceHistory` track all stock and price changes with action types
- `order=1` convention for default images via `is_default` boolean

### `cart`
Models: `Cart`, `CartItem`

- Authenticated users: cart stored in database
- Guest users: cart stored in Django session as a list of dicts `[{product_id, quantity, selected}]`
- On login, session cart is merged into the database cart via a `user_logged_in` signal
- Context processor provides `cart_item_count` and `cart_subtotal` to all templates

### `order`
Models: `Order`, `OrderItem`, `OrderAddress`, `OrderEvent`, `Payment`

Key design decisions:
- `customer_id`, `product_id`, `rider_id` stored as plain `IntegerField` — no FK for scalability
- `OrderItem` stores product name, SKU, price as a snapshot at time of order
- `OrderEvent` is an append-only event log — each status change creates a new row
- `Order.current_status` is a denormalized fast-read field, kept in sync with `OrderEvent`
- `Payment` is a separate model supporting multiple payment attempts per order
- Inventory is decremented on order placement and restored on cancellation
- `QuantityHistory` entry created for every inventory change

### `rider`
Models: `RiderProfile`, `RiderApplication`, `RiderAddress`

- `RiderAddress` supports one active address per rider via a DB constraint
- Rider assignment uses a zone → area → city → country fallback matching algorithm
- Rider status transitions are strictly sequential and enforced in the view

---

## URL Structure

| Prefix | Includes | Description |
|---|---|---|
| `/` | `core.urls` | Public pages |
| `/my-dashboard/` | `order/customer_urls.py`, `user.urls`, `cart.urls` | Customer dashboard |
| `/manager-dashboard/` | `order/manager_urls.py`, `rider.urls`, `product.urls` | Manager dashboard |
| `/rider-dashboard/` | `order/rider_urls.py` | Rider dashboard |
| `/accounts/` | `allauth.urls` | Auth (login, signup, etc.) |

---

## Key Design Patterns

**No service layer** — all business logic lives in views for simplicity and traceability.

**Plain IntegerField over FK** — `customer_id`, `created_by`, `rider_id` are stored as integers rather than foreign keys where cross-service scalability is a concern.

**Snapshot fields on OrderItem** — product name, SKU, and price are copied at order time so historical orders are unaffected by product changes.

**Context processor for cart** — cart count and subtotal are injected into every template without repeating the query in every view.

**Event log pattern for order tracking** — `OrderEvent` is append-only. Every status change adds a row, giving a full timestamped audit trail displayed on the tracking UI.

**Atomic transactions** — order placement, cancellation, and inventory updates are wrapped in `transaction.atomic()` so partial failures never leave the database in an inconsistent state.

---

## Setup

```bash
git clone https://github.com/your-username/ecom-django-fullstack.git
cd ecom-django-fullstack

python -m venv ecom-env
source ecom-env/bin/activate  # Windows: ecom-env\Scripts\activate

pip install -r requirements.txt

cp .env.example .env  # configure your DB, secret key, etc.

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Environment Variables

```
DJANGO_SECRET=
DEBUG=
ALLOWED_HOSTS=
DATABASE_URL=

EMAIL_BACKEND=anymail.backends.resend.EmailBackend
EMAIL_PROVIDER_NAME=resend
EMAIL_API_KEY=
DEFAULT_FROM_EMAIL=

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=


```

---

## Permissions

| Permission | Used By |
|---|---|
| `order.view_order` | Manager order list and detail |
| `order.change_order` | Manager assign rider |
| `order.cancel_order` | Manager cancel order (custom permission) |
| `product.view_product` | Manager product list |
| `product.view_category` | Manager category list |
| `rider.view_riderapplication` | Manager rider applications |
| `rider.view_riderprofile` | Manager rider profiles |

---

## License

MIT
