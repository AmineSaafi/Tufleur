from django import forms
from django.contrib.auth.models import User
from .models import Shop, Product, Trader, Picture, Collection, Promotion, Album, Pic, wish_category, wish_list


class ShopForm(forms.ModelForm):

    class Meta:
        model = Shop
        fields = ['name', 'logo', 'description', 'address']


class CollectionForm(forms.ModelForm):

    class Meta:
        model = Collection
        fields = ['title', 'description', 'product', 'image_collection', 'is_active']


#class PromotionForm(forms.ModelForm):
    # product = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Product.objects.all())

#    class Meta:
#        model = Promotion
#        fields = ['product','collection','discount_value', 'promotion_type', 'promotion_for', 'start_time', 'end_time', 'status']

class PromotionForm(forms.ModelForm):
    # product = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Product.objects.all())

    class Meta:
        model = Promotion
        fields = ['title','promotion_type', 'promotion_for','product','collection','discount_value','start_time', 'end_time']


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'description', 'product_type', 'price', 'principal_picture', 'category', 'quantity', 'is_active']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class TraderForm(forms.ModelForm):

    class Meta:
        model = Trader
        fields = ['picture', 'commercant_type', 'description', 'fb_link', 'instagram_link', 'location']


class PictureForm(forms.ModelForm):

    class Meta:
        model = Picture
        fields = ['name']

class AlbumForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = ['title', 'description', 'album_image']


class PicForm(forms.ModelForm):

    class Meta:
        model = Pic
        fields = ['name', 'image', 'details']

class CategoryForm(forms.ModelForm):

    class Meta:
        model = wish_category
        fields = ['title', 'image_category','description','is_active']

class WishlistForm(forms.ModelForm):
    produit = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True)

    class Meta:
        model = wish_list
        fields = ['wish_category','produit']


class WishlistForm1(forms.ModelForm):

    class Meta:
        model = wish_list
        fields = ['wish_category']
