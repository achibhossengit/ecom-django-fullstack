# ecom-django-fullstack

A full-stack e-commerce web application built with Django, DaisyUI, and Tailwind CSS. The platform supports customers, managers, and riders — each with their own dashboard and workflows.

---

## Features

### Customer

- Browse products with search, category, and price filters
- Product detail page with reviews and ratings
- Cart management (authenticated + guest session cart, merged on login)
- Place orders with delivery address selection (payment gateways are not wired; orders remain unpaid)
- Order history with detail view
- Order tracking (real-time status events)
- Cancel unpaid orders



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

## Groups and permissions

Created by seed commands (`create_groups`, `assign_grouppermissions`), not JSON fixtures. New signups are added to `customer` automatically.

| Group | Permissions (short) |
| --- | --- |
| `customer` | Cart; place / view / cancel orders; view catalog; reviews; apply to be a rider |
| `manager` | Manager dashboard; product & category CRUD; view / assign / cancel orders; review rider applications and profiles |
| `rider` | Rider dashboard; view assigned orders; add order events (status updates); manage own profile and addresses |

---

## Tech Stack


| Layer        | Technology                                                           |
| ------------ | -------------------------------------------------------------------- |
| Backend      | Django 6.x                                                           |
| Auth         | django-allauth (email + Google)                                      |
| Frontend     | Tailwind CSS 4 + DaisyUI 5                                           |
| Database     | PostgreSQL (`DATABASE_URL`)                                          |
| Cache        | LocMem when `DEBUG=True`; Redis when `DEBUG=False`. Homepage catalog only — not sessions, cart, or rate limiting |
| Static files | WhiteNoise. Source in `assets/` (including compiled `css/output.css`); `collectstatic` writes gitignored `staticfiles/` |
| Media        | Local `mediafiles/` when `DEBUG=True`; Cloudinary when `DEBUG=False` |
| Email        | Console backend in debug; Anymail / Resend in production             |
| Payment      | Not integrated. `Payment.Method` lists COD, bKash, Nagad, and SSLCommerz, but checkout does not call any gateway. Seed data uses COD only; new orders stay unpaid. |


---



## Apps Overview



### `core`

Public pages — homepage, shop listing, product detail, category listing, about — plus country/city/area/zone address helpers.

The homepage caches category and product query results for 15 minutes (`homepage_catalog`). The HTML is always rendered fresh so login toasts and the auth navbar are not frozen. That catalog cache is dropped when a `Product`, `Category`, `Inventory`, `ProductImage`, or `CategoryImage` is saved or deleted.

### `users`

Profile and saved addresses. Login, signup, and email verification are handled by django-allauth.

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
- Cart page is not cached — items and the active shipping address are read live on each request
- Context processor provides `cart_item_count` and `cart_subtotal` to all templates



### `order`

Models: `Order`, `OrderItem`, `OrderAddress`, `OrderEvent`, `Payment`

Key design decisions:

- `customer_id`, `product_id`, `rider_id` stored as plain `IntegerField` — no FK for scalability
- `OrderItem` stores product name, SKU, price as a snapshot at time of order
- `OrderEvent` is an append-only event log — each status change creates a new row
- `Order.current_status` is a denormalized fast-read field, kept in sync with `OrderEvent`
- `Payment` is a placeholder for multiple attempts (COD / bKash / Nagad / SSLCommerz). There is no pay view or provider SDK; checkout does not create a `Payment` row
- Inventory is decremented on order placement and restored on cancellation
- `QuantityHistory` entry created for every inventory change



### `rider`

Models: `RiderProfile`, `RiderApplication`, `RiderAddress`

- `RiderAddress` supports one active address per rider via a DB constraint
- Rider assignment uses a zone → area → city → country fallback matching algorithm
- Rider status transitions are strictly sequential and enforced in the view

---



## URL Structure


| Prefix                                   | Includes                   | Description                                     |
| ---------------------------------------- | -------------------------- | ----------------------------------------------- |
| `/`                                      | `core.urls`                | Homepage, shop, categories, about, address AJAX |
| `/admin/`                                | Django admin               | Admin site                                      |
| `/accounts/`                             | `allauth.urls`             | Login, signup, email, Google OAuth              |
| `/cart/`                                 | `cart.urls`                | Cart                                            |
| `/my-dashboard/`                         | `users.urls`               | Profile and addresses                           |
| `/my-dashboard/orders/`                  | `order.urls`               | Customer orders                                 |
| `/my-dashboard/be-a-rider/`              | `rider.urls`               | Rider applications                              |
| `/manager-dashboard/`                    | `product.urls`             | Manager products and categories                 |
| `/manager-dashboard/orders/`             | `order.urls`               | Manager orders                                  |
| `/manager-dashboard/rider-applications/` | `rider.urls`               | Manager rider applications                      |
| `/manager-dashboard/rider-profiles/`     | `rider.urls`               | Manager rider profiles                          |
| `/rider-dashboard/`                      | `order.urls`, `rider.urls` | Rider orders, profile, addresses                |


---



## Key Design Patterns

**No service layer** — all business logic lives in views for simplicity and traceability.

**Plain IntegerField over FK** — `customer_id`, `created_by`, `rider_id` are stored as integers rather than foreign keys where cross-service scalability is a concern.

**Snapshot fields on OrderItem** — product name, SKU, and price are copied at order time so historical orders are unaffected by product changes.

**Context processor for cart** — cart count and subtotal are injected into every template without repeating the query in every view.

**Homepage catalog cache** — only the homepage product/category lists are cached (15 minutes). Cart, sessions, and authentication do not use the cache. Redis is the production backend for that catalog cache; there is no rate limiter.

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

Optional (rebuild Tailwind CSS after template or `assets/input.css` changes):

```bash
npm install
npm run watch:css          # development
# npm run build:css        # one-off build → assets/css/output.css
```

Commit `assets/css/output.css` so clones work without Node. Then collect into gitignored `staticfiles/` (WhiteNoise):

```bash
python manage.py collectstatic
```

Do not commit `static/` or `staticfiles/`. JS, images, and compiled CSS live in `assets/`. `collectstatic` copies them to `staticfiles/`.



### 2. Database (optional local Postgres)

Compose only starts PostgreSQL. Skip this step if `DATABASE_URL` already points at a hosted database.

```bash
docker compose up -d
```


| Service         | Image         | Host port | Notes                                                 |
| --------------- | ------------- | --------- | ----------------------------------------------------- |
| `ecom-postgres` | `postgres:17` | `5432`    | User `admin`, password `password`, database `ecom-db` |


Data is stored in the `ecom-post-data` volume. Stop with `docker compose down`; add `-v` only if you also want to wipe that volume.

### 3. Environment file

Create a `.env` in the project root. Do not commit it (it is gitignored).

```
DJANGO_SECRET=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Local Compose Postgres (use your hosted URL instead if not using Docker)
DATABASE_URL=postgres://admin:password@localhost:5432/ecom-db

# Used only when DEBUG=False (homepage catalog cache backend — not sessions or rate limiting)
REDIS_CACHE_LOCATION=redis://localhost:6379/1
REDIS_CACHE_VERSION=1

EMAIL_BACKEND=anymail.backends.resend.EmailBackend
EMAIL_PROVIDER_NAME=resend
EMAIL_API_KEY=replace-me
DEFAULT_FROM_EMAIL=noreply@example.com

GOOGLE_CLIENT_ID=replace-me
GOOGLE_CLIENT_SECRET=replace-me

# Required when DEBUG=False
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

With `DEBUG=True`, Django uses in-process LocMem cache, local media files, and the console email backend. Redis, Cloudinary, and the Resend API key are required in production (`DEBUG=False`). Redis is only the Django cache backend for the homepage catalog; login still uses database sessions.

### 4. Migrate

```bash
python manage.py migrate
python manage.py createsuperuser
```



### 5. Load fixtures and seed data

JSON fixtures live in `fixtures/` (`FIXTURE_DIRS` in settings). Pick **one** of the paths below — `load_all_data` already includes the address fixtures.

An empty catalog is valid: the homepage, shop, and category pages show “No products found.” / “No categories found.” until you seed or add data in admin.

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


| File                      | Model          |
| ------------------------- | -------------- |
| `fixtures/countries.json` | `core.Country` |
| `fixtures/cities.json`    | `core.City`    |
| `fixtures/areas.json`     | `core.Area`    |
| `fixtures/zones.json`     | `core.Zone`    |




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

The homepage catalog is cached for 15 minutes and is cleared when products or categories change. After seeding, flush cache if the homepage still looks empty:

```bash
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

In debug, restarting `runserver` also clears the LocMem cache.

### 6. Run

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
