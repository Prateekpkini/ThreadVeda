from .models import CartItem, Category


def cart_context(request):
    """Add cart count to every template context."""
    cart_count = 0
    cart_total = 0

    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if session_key:
            items = CartItem.objects.filter(session_key=session_key)
        else:
            items = CartItem.objects.none()

    for item in items:
        cart_count += item.quantity
        cart_total += item.total_price

    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
    }


def categories_context(request):
    """Add all active categories to every template context."""
    return {
        'all_categories': Category.objects.filter(is_active=True),
    }
