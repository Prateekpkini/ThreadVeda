from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDate
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json

from store.models import Product, Order, Category, Payment, Review


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with stats and charts."""
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    # Stats
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('total'))['total'] or 0

    total_orders = Order.objects.count()
    total_products = Product.objects.filter(is_active=True).count()
    total_users = User.objects.filter(is_staff=False).count()

    # Recent orders
    recent_orders = Order.objects.all()[:10]

    # Monthly revenue for chart
    monthly_revenue = Order.objects.filter(
        payment_status='paid',
        created_at__gte=today - timedelta(days=180)
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('total'),
        count=Count('id')
    ).order_by('month')

    # Daily orders for last 7 days
    daily_orders = Order.objects.filter(
        created_at__gte=last_7_days
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # Order status distribution
    status_dist = Order.objects.values('status').annotate(count=Count('id'))

    # Top products
    top_products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]

    # Low stock products
    low_stock = Product.objects.filter(stock__lte=5, is_active=True).order_by('stock')[:5]

    # Prepare chart data
    chart_labels = [item['month'].strftime('%b %Y') for item in monthly_revenue]
    chart_data = [float(item['revenue']) for item in monthly_revenue]

    daily_labels = [item['date'].strftime('%d %b') for item in daily_orders]
    daily_data = [item['count'] for item in daily_orders]

    status_labels = [item['status'].title() for item in status_dist]
    status_data = [item['count'] for item in status_dist]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'low_stock': low_stock,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'daily_labels': json.dumps(daily_labels),
        'daily_data': json.dumps(daily_data),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def manage_products(request):
    """Product management page."""
    products = Product.objects.all().select_related('category')
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'dashboard/manage_products.html', context)


@login_required
@user_passes_test(is_admin)
def manage_orders(request):
    """Order management page."""
    orders = Order.objects.all().select_related('user')

    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    context = {
        'orders': orders,
    }
    return render(request, 'dashboard/manage_orders.html', context)


@login_required
@user_passes_test(is_admin)
def update_order_status(request):
    """Update order status via AJAX."""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()

        return JsonResponse({'success': True, 'new_status': new_status})

    return JsonResponse({'success': False}, status=400)


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """User management page."""
    users = User.objects.filter(is_staff=False).order_by('-date_joined')

    context = {
        'users': users,
    }
    return render(request, 'dashboard/manage_users.html', context)
