import os
import json
import re
from functools import wraps
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import recommender


# =====================================================
# KONFIGURASI DASAR
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "secret_stuffsus_key_123"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:@localhost/retail_recommendation_system"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =====================================================
# PAYMENT METHOD
# =====================================================

PAYMENT_METHODS = [
    ("credit_card", "Credit Card", "fa-credit-card"),
    ("mobile_payment", "Mobile Payment", "fa-mobile-screen-button"),
    ("debit_card", "Debit Card", "fa-credit-card"),
    ("cash", "Cash", "fa-money-bill-wave"),
]

PAYMENT_LABELS = {k: v for k, v, _ in PAYMENT_METHODS}


# =====================================================
# DATABASE MODELS
# =====================================================

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")
    full_name = db.Column(db.String(150), default="")
    phone = db.Column(db.String(30), default="")
    address = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_url = db.Column(
        db.String(500),
        default="/images/default_avatar.jpg"
    )

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Kategori(db.Model):
    __tablename__ = "kategori"

    id = db.Column(db.Integer, primary_key=True)
    nama_kategori = db.Column(db.String(100), unique=True, nullable=False)

    subkategoris = db.relationship(
        "Subkategori",
        backref="kategori",
        cascade="all, delete-orphan"
    )

    @property
    def product_count(self):
        return sum(len(s.products) for s in self.subkategoris)


class Subkategori(db.Model):
    __tablename__ = "subkategori"

    id = db.Column(db.Integer, primary_key=True)
    nama_subkategori = db.Column(db.String(100), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey("kategori.id"), nullable=False)

    products = db.relationship(
        "Product",
        backref="subkategori",
        cascade="all, delete-orphan"
    )


class Product(db.Model):
    __tablename__ = "produk"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=50)
    description = db.Column(db.Text, default="")
    image_url = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, default=4.8)
    reviews = db.Column(db.Integer, default=100)
    sold = db.Column(db.Integer, default=0)
    is_new_arrival = db.Column(db.Boolean, default=False)
    is_best_seller = db.Column(db.Boolean, default=False)
    discount_percent = db.Column(db.Integer, default=0)

    subkategori_id = db.Column(
        db.Integer,
        db.ForeignKey("subkategori.id"),
        nullable=True
    )

    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    seller = db.relationship("User", backref="products")

    @property
    def final_price(self):
        if self.discount_percent > 0:
            return self.price * (100 - self.discount_percent) / 100.0
        return self.price

    @property
    def category(self):
        if self.subkategori and self.subkategori.kategori:
            return self.subkategori.kategori.nama_kategori
        return "-"

    @property
    def subcategory(self):
        return self.subkategori.nama_subkategori if self.subkategori else "-"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="orders")

    total = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(30), default="Diproses")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "OrderItem",
        backref="order",
        cascade="all, delete-orphan"
    )

    @property
    def payment_label(self):
        return PAYMENT_LABELS.get(self.payment_method, self.payment_method)


class OrderItem(db.Model):
    __tablename__ = "order_item"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("produk.id"), nullable=True)

    product_name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


# =====================================================
# HELPER
# =====================================================

def current_user():
    uid = session.get("user_id")
    if uid:
        return User.query.get(uid)
    return None


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Silakan login terlebih dahulu.", "error")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = current_user()

            if not user:
                flash("Silakan login terlebih dahulu.", "error")
                return redirect(url_for("login", next=request.path))

            if user.role not in roles:
                flash("Anda tidak memiliki akses ke halaman tersebut.", "error")
                return redirect(url_for("index"))

            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.context_processor
def inject_globals():
    cart = session.get("cart", {})

    return dict(
        cart_count=sum(cart.values()),
        current_user=current_user(),
        all_kategori=Kategori.query.order_by(Kategori.nama_kategori).all(),
        all_subkategori=Subkategori.query.order_by(Subkategori.nama_subkategori).all(),
    )


def slugify(name):
    return name.strip().lower().replace(" ", "_")


def get_products_by_slug_order(rec_slugs):
    """
    Mengambil produk dari database sesuai urutan rekomendasi model.
    Ini penting karena Product.slug.in_(rec_slugs).all() urutannya bisa acak dari MySQL.
    """
    if not rec_slugs:
        return []

    rec_products = Product.query.filter(Product.slug.in_(rec_slugs)).all()
    product_map = {p.slug: p for p in rec_products}

    ordered_products = [
        product_map[slug]
        for slug in rec_slugs
        if slug in product_map
    ]

    return ordered_products


# =====================================================
# SEED DATABASE
# =====================================================

def seed_initial_data():
    if User.query.count() == 0:
        admin = User(
            username="admin",
            email="admin@stuffsus.com",
            role="admin",
            full_name="Administrator Stuffsus"
        )
        admin.set_password("admin123")

        seller = User(
            username="seller",
            email="seller@stuffsus.com",
            role="seller",
            full_name="Toko Stuffsus Official"
        )
        seller.set_password("seller123")

        user = User(
            username="user",
            email="user@stuffsus.com",
            role="user",
            full_name="Pelanggan Setia"
        )
        user.set_password("user123")

        db.session.add_all([admin, seller, user])
        db.session.commit()

    if Product.query.count() == 0:
        seed_path = os.path.join(BASE_DIR, "data", "seed_products.json")

        if not os.path.exists(seed_path):
            print("[seed] data/seed_products.json tidak ditemukan.")
            return

        with open(seed_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        sub_objects = {}

        for kat_name, sub_names in data["kategori_map"].items():
            kat = Kategori.query.filter_by(nama_kategori=kat_name).first()

            if not kat:
                kat = Kategori(nama_kategori=kat_name)
                db.session.add(kat)
                db.session.flush()

            for s in sub_names:
                sub = Subkategori(
                    nama_subkategori=s.replace("_", " ").title(),
                    kategori_id=kat.id
                )
                db.session.add(sub)
                db.session.flush()
                sub_objects[s] = sub

        seller = User.query.filter_by(role="seller").first()
        sid = seller.id if seller else None

        for p in data["products"]:
            sub = sub_objects.get(p["subkategori"])

            db.session.add(Product(
                slug=p["slug"],
                name=p["name"],
                price=p["price"],
                stock=p["stock"],
                sold=p["sold"],
                description=p["description"],
                image_url=p["image_url"],
                rating=round(4.0 + (p["sold"] % 10) / 10.0, 1),
                reviews=max(10, p["sold"]),
                is_new_arrival=p["is_new_arrival"],
                is_best_seller=p["is_best_seller"],
                discount_percent=p["discount_percent"],
                subkategori_id=sub.id if sub else None,
                seller_id=sid,
            ))

        db.session.commit()
        print(f"[seed] {len(data['products'])} produk berhasil dimuat.")


# =====================================================
# AUTH ROUTES
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "user")

        if role not in ("user", "seller"):
            role = "user"

        if not username or not email or not password:
            flash("Semua kolom wajib diisi.", "error")
            return redirect(url_for("register"))

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username atau email sudah terdaftar.", "error")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            email=email,
            role=role,
            full_name=request.form.get("full_name", "")
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Pendaftaran berhasil! Silakan login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["role"] = user.role

            flash(f"Selamat datang kembali, {user.full_name or user.username}!", "success")

            next_url = request.args.get("next")

            if user.role == "admin":
                return redirect(next_url or url_for("admin_dashboard"))

            if user.role == "seller":
                return redirect(next_url or url_for("seller_dashboard"))

            return redirect(next_url or url_for("index"))

        flash("Username atau password salah.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("role", None)

    flash("Anda telah logout.", "success")
    return redirect(url_for("index"))


# =====================================================
# PROFILE
# =====================================================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()

    if request.method == "POST":
        user.full_name = request.form.get("full_name", user.full_name)
        user.email = request.form.get("email", user.email)
        # No. Telepon hanya boleh berisi angka (sanitasi sisi server)
        phone_input = request.form.get("phone", user.phone) or ""
        user.phone = re.sub(r"\D", "", phone_input)
        user.address = request.form.get("address", user.address)

        avatar = request.form.get("avatar_url", "").strip()
        if avatar:
            user.avatar_url = avatar

        new_pw = request.form.get("new_password", "")
        if new_pw:
            user.set_password(new_pw)

        db.session.commit()

        flash("Data pribadi berhasil diperbarui!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


# =====================================================
# BERANDA
# =====================================================

@app.route("/")
def index():
    new_arrivals = Product.query.filter_by(is_new_arrival=True).limit(4).all()

    best_sellers = Product.query.filter_by(
        is_best_seller=True
    ).order_by(Product.sold.desc()).limit(4).all()

    on_discount = Product.query.filter(
        Product.discount_percent > 0
    ).order_by(Product.discount_percent.desc()).limit(4).all()

    recommendations = []
    cart = session.get("cart", {})

    if cart and recommender.is_available():
        product_ids = [int(i) for i in cart.keys()]
        cart_products = Product.query.filter(Product.id.in_(product_ids)).all()
        slugs = [p.slug for p in cart_products if p.slug]

        rec_slugs = recommender.recommend_for_many(slugs, n=5)
        recommendations = get_products_by_slug_order(rec_slugs)

    return render_template(
        "index.html",
        new_arrivals=new_arrivals,
        best_sellers=best_sellers,
        on_discount=on_discount,
        recommendations=recommendations
    )


# =====================================================
# SHOP
# =====================================================

@app.route("/shop")
def shop():
    kategori_id = request.args.get("kategori", type=int)
    search_query = request.args.get("search")
    special = request.args.get("filter")
    page = request.args.get("page", 1, type=int)
    per_page = 12

    query = Product.query
    active_kategori = None

    if kategori_id:
        active_kategori = Kategori.query.get(kategori_id)

        if active_kategori:
            sub_ids = [s.id for s in active_kategori.subkategoris]
            query = query.filter(Product.subkategori_id.in_(sub_ids))

    if search_query:
        query = query.filter(Product.name.like(f"%{search_query}%"))

    if special == "new_arrival":
        query = query.filter_by(is_new_arrival=True)

    elif special == "best_seller":
        query = query.filter_by(is_best_seller=True)

    elif special == "on_discount":
        query = query.filter(Product.discount_percent > 0)

    pagination = query.order_by(Product.name).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    products = pagination.items
    total_products = Product.query.count()

    recommendations = []

    if search_query and recommender.is_available():
        search_slug = slugify(search_query)
        rec_slugs = recommender.recommend(search_slug, n=10)

        print("SEARCH SLUG:", search_slug)
        print("REC SLUGS SHOP:", rec_slugs)

        recommendations = get_products_by_slug_order(rec_slugs)

        print("REKOMENDASI SHOP:", [p.slug for p in recommendations])

    current_args = request.args.to_dict()
    current_args.pop("page", None)
    current_args.pop("kategori", None)
    current_args.pop("filter", None)

    return render_template(
        "shop.html",
        products=products,
        pagination=pagination,
        total_products=total_products,
        active_kategori=active_kategori,
        active_filter=special,
        search_query=search_query or "",
        current_args=current_args,
        recommendations=recommendations
    )


# =====================================================
# CART & CHECKOUT
# =====================================================

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    cart = session.get("cart", {})
    p_id_str = str(product_id)
    current_qty = cart.get(p_id_str, 0)

    if current_qty + 1 > product.stock:
        flash(f"Maaf, stok '{product.name}' hanya tersisa {product.stock} pcs.", "error")
        return redirect(request.referrer or url_for("shop"))

    cart[p_id_str] = current_qty + 1
    session["cart"] = cart

    flash(f"Berhasil menambahkan '{product.name}' ke keranjang belanja!", "success")
    return redirect(request.referrer or url_for("shop"))


@app.route("/buy_now/<int:product_id>", methods=["POST"])
def buy_now(product_id):
    product = Product.query.get_or_404(product_id)

    cart = session.get("cart", {})
    p_id_str = str(product_id)
    current_qty = cart.get(p_id_str, 0)

    if current_qty + 1 > product.stock:
        flash(f"Maaf, stok '{product.name}' hanya tersisa {product.stock} pcs.", "error")
        return redirect(request.referrer or url_for("shop"))

    cart[p_id_str] = current_qty + 1
    session["cart"] = cart

    return redirect(url_for("checkout"))


@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})

    cart_items = []
    total_price = 0.0
    slugs = []

    for p_id_str, qty in cart.items():
        product = Product.query.get(int(p_id_str))

        if product:
            subtotal = product.final_price * qty
            total_price += subtotal

            if product.slug:
                slugs.append(product.slug)

            cart_items.append({
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.final_price,
                "original_price": product.price,
                "discount": product.discount_percent,
                "image_url": product.image_url,
                "quantity": qty,
                "subtotal": subtotal,
            })

    recommendations = []

    if slugs and recommender.is_available():
        rec_slugs = recommender.recommend_for_many(slugs, n=10)

        print("CART SLUGS:", slugs)
        print("REC SLUGS CART:", rec_slugs)

        recommendations = get_products_by_slug_order(rec_slugs)

        print("REKOMENDASI CART:", [p.slug for p in recommendations])

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_price=total_price,
        recommendations=recommendations
    )


@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    p_id_str = str(product_id)

    if p_id_str in cart:
        del cart[p_id_str]
        session["cart"] = cart
        flash("Produk telah dihapus dari keranjang.", "success")

    return redirect(url_for("view_cart"))


@app.route("/update_cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    product = Product.query.get_or_404(product_id)

    cart = session.get("cart", {})
    p_id_str = str(product_id)

    try:
        new_qty = int(request.form.get("quantity", 1))
    except ValueError:
        new_qty = 1

    if new_qty < 1:
        new_qty = 1

    if new_qty > product.stock:
        flash(f"Stok '{product.name}' hanya tersisa {product.stock} pcs.", "error")
        new_qty = product.stock

    cart[p_id_str] = new_qty
    session["cart"] = cart

    return redirect(url_for("view_cart"))


@app.route("/checkout", methods=["GET"])
@login_required
def checkout():
    cart = session.get("cart", {})

    if not cart:
        flash("Keranjang Anda kosong.", "error")
        return redirect(url_for("shop"))

    cart_items = []
    total_price = 0.0

    for p_id_str, qty in cart.items():
        product = Product.query.get(int(p_id_str))

        if product:
            subtotal = product.final_price * qty
            total_price += subtotal

            cart_items.append({
                "name": product.name,
                "price": product.final_price,
                "quantity": qty,
                "subtotal": subtotal,
                "image_url": product.image_url
            })

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total_price=total_price,
        payment_methods=PAYMENT_METHODS,
        user=current_user()
    )


@app.route("/checkout/process", methods=["POST"])
@login_required
def checkout_process():
    cart = session.get("cart", {})

    if not cart:
        flash("Keranjang Anda kosong.", "error")
        return redirect(url_for("shop"))

    payment_method = request.form.get("payment_method")

    if payment_method not in PAYMENT_LABELS:
        flash("Silakan pilih metode pembayaran terlebih dahulu.", "error")
        return redirect(url_for("checkout"))

    user = current_user()

    order = Order(
        user_id=user.id,
        total=0.0,
        payment_method=payment_method
    )

    db.session.add(order)

    total = 0.0

    for p_id_str, qty in cart.items():
        product = Product.query.get(int(p_id_str))

        if product:
            total += product.final_price * qty

            product.sold = (product.sold or 0) + qty
            product.stock = max(0, (product.stock or 0) - qty)

            order.items.append(OrderItem(
                product_id=product.id,
                product_name=product.name,
                price=product.final_price,
                quantity=qty
            ))

    order.total = total
    db.session.commit()

    session["cart"] = {}

    flash(
        f"Transaksi berhasil! Pembayaran via {PAYMENT_LABELS[payment_method]} "
        f"sebesar ${total:.2f}. Terima kasih telah berbelanja di Stuffsus.",
        "success"
    )

    return redirect(url_for("my_orders"))


@app.route("/orders")
@login_required
def my_orders():
    user = current_user()

    orders = Order.query.filter_by(
        user_id=user.id
    ).order_by(Order.created_at.desc()).all()

    return render_template("orders.html", orders=orders)


# =====================================================
# SELLER DASHBOARD
# =====================================================

@app.route("/seller")
@role_required("seller", "admin")
def seller_dashboard():
    user = current_user()

    if user.role == "admin":
        my_products = Product.query.all()
    else:
        my_products = Product.query.filter_by(seller_id=user.id).all()

    # Data untuk bar chart "Penjualan Terlaris".
    # Difilter & diurutkan di sisi browser agar filter kategori responsif.
    chart_products = [
        {
            "name": p.name,
            "sold": p.sold or 0,
            "category": p.category,
        }
        for p in my_products
    ]

    # Daftar kategori unik (untuk opsi filter pada bar chart)
    chart_categories = sorted(
        {p["category"] for p in chart_products if p["category"] and p["category"] != "-"}
    )

    return render_template(
        "seller.html",
        my_products=my_products,
        chart_products=chart_products,
        chart_categories=chart_categories,
    )


def _product_from_form(product, form, seller_id=None):
    product.name = form.get("name")
    product.slug = product.slug or slugify(form.get("name", ""))
    product.price = float(form.get("price", 0))
    product.stock = int(form.get("stock", 50) or 50)
    product.description = form.get("description", "")
    product.image_url = form.get("image_url") or "/images/default.jpg"
    product.is_new_arrival = bool(form.get("is_new_arrival"))
    product.is_best_seller = bool(form.get("is_best_seller"))
    product.discount_percent = int(form.get("discount_percent", 0) or 0)

    if form.get("subkategori_id"):
        product.subkategori_id = int(form.get("subkategori_id"))
    else:
        product.subkategori_id = None

    if seller_id:
        product.seller_id = seller_id

    return product


@app.route("/seller/add", methods=["POST"])
@role_required("seller", "admin")
def seller_add_product():
    user = current_user()

    product = _product_from_form(Product(), request.form, seller_id=user.id)

    base_slug = product.slug
    i = 2

    while Product.query.filter_by(slug=product.slug).first():
        product.slug = f"{base_slug}_{i}"
        i += 1

    db.session.add(product)
    db.session.commit()

    flash(f"Produk '{product.name}' berhasil ditambahkan!", "success")
    return redirect(url_for("seller_dashboard"))


@app.route("/seller/edit/<int:product_id>", methods=["GET", "POST"])
@role_required("seller", "admin")
def seller_edit_product(product_id):
    user = current_user()
    product = Product.query.get_or_404(product_id)

    if user.role != "admin" and product.seller_id != user.id:
        flash("Anda hanya dapat mengubah produk milik Anda sendiri.", "error")
        return redirect(url_for("seller_dashboard"))

    if request.method == "POST":
        _product_from_form(product, request.form)
        db.session.commit()

        flash("Produk berhasil diperbarui!", "success")
        return redirect(url_for("seller_dashboard"))

    return render_template("edit_product.html", product=product)


@app.route("/seller/delete/<int:product_id>")
@role_required("seller", "admin")
def seller_delete_product(product_id):
    user = current_user()
    product = Product.query.get_or_404(product_id)

    if user.role != "admin" and product.seller_id != user.id:
        flash("Anda hanya dapat menghapus produk milik Anda sendiri.", "error")
        return redirect(url_for("seller_dashboard"))

    db.session.delete(product)
    db.session.commit()

    flash("Produk berhasil dihapus.", "success")
    return redirect(url_for("seller_dashboard"))


# =====================================================
# ADMIN DASHBOARD
# =====================================================

@app.route("/admin")
@role_required("admin")
def admin_dashboard():
    stats = {
        "total_users": User.query.count(),
        "total_sellers": User.query.filter_by(role="seller").count(),
        "total_products": Product.query.count(),
        "total_orders": Order.query.count(),
        "total_revenue": sum(o.total for o in Order.query.all()),
    }

    all_users = User.query.all()
    all_products = Product.query.all()
    all_orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template(
        "admin.html",
        stats=stats,
        all_users=all_users,
        all_products=all_products,
        all_orders=all_orders
    )


@app.route("/admin/user/role/<int:user_id>", methods=["POST"])
@role_required("admin")
def admin_change_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role")

    if new_role in ("user", "seller", "admin"):
        user.role = new_role
        db.session.commit()
        flash(f"Role {user.username} diubah menjadi {new_role}.", "success")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/user/delete/<int:user_id>")
@role_required("admin")
def admin_delete_user(user_id):
    me = current_user()

    if me.id == user_id:
        flash("Anda tidak dapat menghapus akun sendiri.", "error")
        return redirect(url_for("admin_dashboard"))

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash(f"Akun '{user.username}' telah dihapus.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/order/status/<int:order_id>", methods=["POST"])
@role_required("admin")
def admin_update_order(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get("status")

    if status in ("Diproses", "Dikirim", "Selesai", "Dibatalkan"):
        order.status = status
        db.session.commit()
        flash(f"Status pesanan #{order.id} diubah menjadi {status}.", "success")

    return redirect(url_for("admin_dashboard"))


# =====================================================
# JALANKAN APP
# =====================================================

with app.app_context():
    db.create_all()
    seed_initial_data()

if __name__ == "__main__":
    app.run(debug=True)