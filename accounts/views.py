from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegistrationForm, LoginForm, ProfileForm
from .models import UserProfile


def register_view(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile
            UserProfile.objects.create(user=user)
            # Auto login
            login(request, user)
            messages.success(request, f'Welcome to ThreadVeda, {user.first_name}!')
            return redirect('store:home')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'store:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Log out user."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('store:home')


@login_required
def profile_view(request):
    """User profile page."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    orders = request.user.orders.all()[:5]

    context = {
        'profile': profile,
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()
            # Update User model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    return render(request, 'accounts/edit_profile.html', {'form': form})
