# your_app/templatetags/engagement_tags.py

from django import template

register = template.Library()

@register.filter
def liked_by_user(product_id, admin_id):
    # Replace this logic with your actual implementation
    # For example, check if a Like object exists for the given product and user
    from jruapp.models import Product  # Adjust the import based on your project structure
    return Product.objects.filter(product_id=product_id, user_id=admin_id).exists()
