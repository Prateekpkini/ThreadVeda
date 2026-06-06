from django import forms
from .models import Review


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Full Name', 'id': 'id_full_name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'Email Address', 'id': 'id_email'
    }))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Phone Number', 'id': 'id_phone'
    }))
    address_line1 = forms.CharField(max_length=300, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Address Line 1', 'id': 'id_address1'
    }))
    address_line2 = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Address Line 2 (Optional)', 'id': 'id_address2'
    }))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'City', 'id': 'id_city'
    }))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'State', 'id': 'id_state'
    }))
    zip_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'ZIP / Postal Code', 'id': 'id_zip'
    }))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-input', 'placeholder': 'Order Notes (Optional)', 'rows': 3, 'id': 'id_notes'
    }))


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.HiddenInput(attrs={'id': 'id_rating'}),
            'title': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Review Title', 'id': 'id_review_title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-input', 'placeholder': 'Write your review...', 'rows': 4, 'id': 'id_comment'
            }),
        }


class PaymentForm(forms.Form):
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('cod', 'Cash on Delivery'),
    ]

    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, widget=forms.RadioSelect(attrs={
        'id': 'id_payment_method'
    }))
    card_number = forms.CharField(max_length=19, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': '1234 5678 9012 3456', 'id': 'id_card_number',
        'maxlength': '19', 'autocomplete': 'cc-number'
    }))
    card_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Cardholder Name', 'id': 'id_card_name'
    }))
    expiry = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'MM/YY', 'id': 'id_expiry', 'maxlength': '5'
    }))
    cvv = forms.CharField(max_length=4, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'CVV', 'id': 'id_cvv', 'maxlength': '4',
        'type': 'password'
    }))
    upi_id = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'your@upi', 'id': 'id_upi'
    }))
