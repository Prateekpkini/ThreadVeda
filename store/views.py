import json
import random
import uuid
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.views.decorators.http import require_POST

from .models import (
    Category, Product, ProductImage, CartItem,
    Order, OrderItem, Payment, Review, Wishlist
)
from .forms import CheckoutForm, ReviewForm, PaymentForm


def home(request):
    """Landing page with featured products, categories, and hero section."""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    new_arrivals = Product.objects.filter(is_new_arrival=True, is_active=True)[:8]
    bestsellers = Product.objects.filter(is_bestseller=True, is_active=True)[:4]
    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'bestsellers': bestsellers,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def product_list(request):
    """Product catalog with filters and search."""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Size filter
    size = request.GET.get('size')
    if size:
        products = products.filter(sizes__icontains=size)

    # Sort
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    elif sort == 'popular':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'current_sort': sort,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """Single product page with images, reviews, and related products."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = product.images.all()
    reviews = product.reviews.all()[:10]
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]

    # Check if user already reviewed
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(user=request.user, product=product).exists()

    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    review_form = ReviewForm()

    context = {
        'product': product,
        'images': images,
        'reviews': reviews,
        'related_products': related_products,
        'review_form': review_form,
        'user_has_reviewed': user_has_reviewed,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'store/product_detail.html', context)


def add_to_cart(request):
    """Add product to cart via AJAX."""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size', '')
        color = request.POST.get('color', '')

        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user, product=product, size=size, color=color,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            cart_item, created = CartItem.objects.get_or_create(
                session_key=session_key, product=product, size=size, color=color,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        # Get updated cart count
        if request.user.is_authenticated:
            cart_count = sum(i.quantity for i in CartItem.objects.filter(user=request.user))
        else:
            cart_count = sum(i.quantity for i in CartItem.objects.filter(session_key=request.session.session_key))

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_count': cart_count,
            })

        messages.success(request, f'{product.name} added to cart!')
        return redirect('store:cart')

    return JsonResponse({'success': False}, status=400)


def update_cart(request):
    """Update cart item quantity via AJAX."""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))

        try:
            if request.user.is_authenticated:
                cart_item = CartItem.objects.get(id=item_id, user=request.user)
            else:
                cart_item = CartItem.objects.get(id=item_id, session_key=request.session.session_key)

            if quantity <= 0:
                cart_item.delete()
                item_total = 0
            else:
                cart_item.quantity = quantity
                cart_item.save()
                item_total = float(cart_item.total_price)

            # Recalculate cart totals
            if request.user.is_authenticated:
                items = CartItem.objects.filter(user=request.user)
            else:
                items = CartItem.objects.filter(session_key=request.session.session_key)

            cart_total = sum(float(i.total_price) for i in items)
            cart_count = sum(i.quantity for i in items)

            return JsonResponse({
                'success': True,
                'item_total': item_total,
                'cart_total': cart_total,
                'cart_count': cart_count,
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)

    return JsonResponse({'success': False}, status=400)


def remove_from_cart(request):
    """Remove item from cart via AJAX."""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')

        try:
            if request.user.is_authenticated:
                cart_item = CartItem.objects.get(id=item_id, user=request.user)
            else:
                cart_item = CartItem.objects.get(id=item_id, session_key=request.session.session_key)

            cart_item.delete()

            # Recalculate
            if request.user.is_authenticated:
                items = CartItem.objects.filter(user=request.user)
            else:
                items = CartItem.objects.filter(session_key=request.session.session_key)

            cart_total = sum(float(i.total_price) for i in items)
            cart_count = sum(i.quantity for i in items)

            return JsonResponse({
                'success': True,
                'cart_total': cart_total,
                'cart_count': cart_count,
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)

    return JsonResponse({'success': False}, status=400)


def cart_view(request):
    """Shopping cart page."""
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    else:
        session_key = request.session.session_key
        if session_key:
            cart_items = CartItem.objects.filter(session_key=session_key).select_related('product')
        else:
            cart_items = CartItem.objects.none()

    subtotal = sum(item.total_price for item in cart_items)
    shipping = Decimal('0.00') if subtotal >= 999 else Decimal('99.00')
    tax = round(subtotal * Decimal('0.18'), 2)
    total = subtotal + shipping + tax

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
    }
    return render(request, 'store/cart.html', context)


@login_required
def checkout(request):
    """Checkout page with address form."""
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('store:product_list')

    subtotal = sum(item.total_price for item in cart_items)
    shipping = Decimal('0.00') if subtotal >= 999 else Decimal('99.00')
    tax = round(subtotal * Decimal('0.18'), 2)
    total = subtotal + shipping + tax

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address_line1=form.cleaned_data['address_line1'],
                address_line2=form.cleaned_data.get('address_line2', ''),
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                zip_code=form.cleaned_data['zip_code'],
                notes=form.cleaned_data.get('notes', ''),
                subtotal=subtotal,
                shipping_cost=shipping,
                tax=tax,
                total=total,
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.effective_price,
                    quantity=item.quantity,
                    size=item.size,
                    color=item.color,
                )

            # Store order id in session for payment
            request.session['pending_order_id'] = order.id

            return redirect('store:payment')
    else:
        # Pre-fill form if profile exists
        initial = {}
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial = {
                'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'email': request.user.email,
                'phone': profile.phone,
                'address_line1': profile.address,
                'city': profile.city,
                'state': profile.state,
                'zip_code': profile.zip_code,
            }
        form = CheckoutForm(initial=initial)

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def payment(request):
    """Mock payment gateway page."""
    order_id = request.session.get('pending_order_id')
    if not order_id:
        messages.error(request, 'No pending order found.')
        return redirect('store:cart')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        method = request.POST.get('payment_method', 'card')
        card_last_four = ''

        if method == 'card':
            card_number = request.POST.get('card_number', '').replace(' ', '')
            card_last_four = card_number[-4:] if len(card_number) >= 4 else ''

        # Simulate payment processing (90% success rate)
        is_success = random.random() < 0.9

        # Create payment record
        payment_obj = Payment.objects.create(
            order=order,
            amount=order.total,
            method=method,
            status='success' if is_success else 'failed',
            card_last_four=card_last_four,
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
        )

        if is_success:
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()

            # Clear cart
            CartItem.objects.filter(user=request.user).delete()

            # Update stock
            for item in order.items.all():
                if item.product:
                    item.product.stock = max(0, item.product.stock - item.quantity)
                    item.product.save()

            # Clear session
            if 'pending_order_id' in request.session:
                del request.session['pending_order_id']

            return redirect('store:order_success', order_number=order.order_number)
        else:
            order.payment_status = 'failed'
            order.save()
            return redirect('store:order_failure', order_number=order.order_number)

    form = PaymentForm()
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'store/payment.html', context)


@login_required
def order_success(request, order_number):
    """Order success page with confetti animation."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def order_failure(request, order_number):
    """Payment failure page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_failure.html', {'order': order})


@login_required
def order_history(request):
    """User's order history."""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    """Single order detail page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
def add_review(request, slug):
    """Submit a product review."""
    product = get_object_or_404(Product, slug=slug)

    if Review.objects.filter(user=request.user, product=product).exists():
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('store:product_detail', slug=slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Review submitted successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')

    return redirect('store:product_detail', slug=slug)


@login_required
def toggle_wishlist(request):
    """Add/remove product from wishlist via AJAX."""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, product=product
        )

        if not created:
            wishlist_item.delete()
            return JsonResponse({'success': True, 'action': 'removed'})

        return JsonResponse({'success': True, 'action': 'added'})

    return JsonResponse({'success': False}, status=400)


@login_required
def wishlist_view(request):
    """User's wishlist page."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})


def search(request):
    """Search results page."""
    query = request.GET.get('q', '')
    products = Product.objects.none()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(material__icontains=query),
            is_active=True
        )

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'store/search.html', context)
