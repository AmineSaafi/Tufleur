from rest_framework.serializers import ModelSerializer
from .models import Product

class ProductCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'is_active', 'en_promotion', 'quantity', 'principal_picture', 'category', 'shop']