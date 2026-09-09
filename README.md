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
| Database | PostgreSQL 17 (Docker) |
| Cache | Redis Stack (Docker) |
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

### 1. Clone and install

```bash
git clone https://github.com/achibhossengit/ecom-django-fullstack.git
cd ecom-django-fullstack

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Optional (Tailwind watch):

```bash
npm install
npm run watch:css
```

### 2. Start Docker services

```bash
docker compose up -d
```

| Service | Image | Host port | Notes |
|---|---|---|---|
| `ecom-postgres` | `postgres:17` | `5432` | User `admin`, password `password`, database `ecom-db` |
| `ecom-redis` | `redis/redis-stack:latest` | `6379` (Redis), `8001` (Redis Insight) | Persistence via `--SAVE 900 1` |
| `ecom-pgadmin` | `dpage/pgadmin4` | `5050` | Login `admin@example.com` / `password` |

Data is stored in named volumes (`ecom-post-data`, `ecom-redis-data`). Stop with `docker compose down`; add `-v` only if you also want to wipe those volumes.

### 3. Environment file

Create a `.env` in the project root (Compose credentials above match the defaults):

```
DJANGO_SECRET=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DATABASE_URL=postgres://admin:password@localhost:5432/ecom-db

REDIS_CACHE_LOCATION=redis://localhost:6379/1
REDIS_CACHE_VERSION=1

EMAIL_BACKEND=anymail.backends.resend.EmailBackend
EMAIL_PROVIDER_NAME=resend
EMAIL_API_KEY=replace-me
DEFAULT_FROM_EMAIL=noreply@example.com

GOOGLE_CLIENT_ID=replace-me
GOOGLE_CLIENT_SECRET=replace-me

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

`DATABASE_URL` and `REDIS_CACHE_LOCATION` use `localhost` because Django runs on the host and Compose publishes those ports. Point them at the service names (`ecom-postgres`, `ecom-redis`) only if you run the app inside the same Compose network.

### 4. Migrate

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Load fixtures and seed data

JSON fixtures live in `fixtures/` (`FIXTURE_DIRS` in settings). Pick **one** of the paths below — `load_all_data` already includes the address fixtures.

#### Address fixtures only

Load country → city → area → zone **in that order** (foreign keys):

```bash
python manage.py loaddata countries.json
python manage.py loaddata cities.json
python manage.py loaddata areas.json
python manage.py loaddata zones.json
```

Same thing via the wrapper command:

```bash
python manage.py create_address
```

| File | Model |
|---|---|
| `fixtures/countries.json` | `core.Country` |
| `fixtures/cities.json` | `core.City` |
| `fixtures/areas.json` | `core.Area` |
| `fixtures/zones.json` | `core.Zone` |

#### Full demo catalog

Seeds addresses, users, products, riders, carts, orders, and group permissions:

```bash
python manage.py load_all_data
```

Order of commands: `create_address` → `load_users` → `load_rider` → `load_product` → `load_cart` → `load_order` → `assign_grouppermissions`.

Continue past a failed step:

```bash
python manage.py load_all_data --ignore-error
```

Or run a subset:

```bash
python manage.py load_users
python manage.py load_product
python manage.py load_rider
python manage.py load_cart
python manage.py load_order
```

`load_product` and `load_rider` attach images from `fixtures/category_images/`, `fixtures/product_images/`, and `fixtures/profile_images/` when those folders exist and contain `.jpg` / `.png` files; otherwise image upload is skipped.

Seeded demo users use password `Test1234!` (usernames like `customer_jane_0`, `manager_…`, `rider_…`).

Homepage HTML is cached in Redis for 15 minutes. After seeding, flush cache if the home page still looks empty:

```bash
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

### 6. Run

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). pgAdmin is at [http://127.0.0.1:5050/](http://127.0.0.1:5050/); Redis Insight at [http://127.0.0.1:8001/](http://127.0.0.1:8001/).

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
