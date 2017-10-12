from django.contrib.auth.models import Permission, User
from django.db import models
import datetime

def user_directory_path(instance, filename):
    return 'user_{0}/{1}/{2}/{3}/{4}'.format(instance.shop.owner.user.username,'Shops', instance.shop.name,instance.name,str(filename))
def user_directory_path_four(instance, filename):
    return 'user_{0}/{1}/{2}/{3}'.format(instance.owner.user.username,'Shops', instance.name,str(filename))
def user_directory_path_two(instance, filename):
    return 'user_{0}/{1}/{2}/{3}/{4}'.format(instance.product.shop.owner.user.username,'Shops', instance.product.shop.name,instance.product.name,str(filename))
def user_directory_path_three(instance, filename):
    return 'user_{0}/{1}/{2}'.format(instance.user.username, 'Profile' ,str(filename))
def user_directory_path_five(instance, filename):
    return 'user_{0}/{1}/{2}/{3}/'.format(instance.owner.user.username, 'Collections', instance.title, str(filename))
def user_directory_path_six(instance, filename):
    return 'user_{0}/{1}/{2}/{3}/'.format(instance.owner.user.username, 'Album', instance.title, str(filename))
def user_directory_path_seven(instance, filename):
    return 'user_{0}/{1}/{2}/{3}/'.format(instance.owner.user.username, 'Album_pics', instance.name, str(filename))
def user_directory_path_eight(instance, filename):
    return 'user_{0}/{1}/{2}/{3}'.format(instance.user.username, 'wish_category' ,instance.title,str(filename))
#-----------------------------------------------------------------------------------------------------------------------
class Trader(models.Model):
    PARTICULAR = 'PA'
    SOCIETY = 'SO'

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    description = models.CharField(max_length=2500, null=True)
    picture = models.ImageField(null=True, blank=True, upload_to=user_directory_path_three)
    fb_link = models.CharField(max_length=100)
    instagram_link = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    commercant_type = models.CharField(
        max_length=20,
        blank=True,
        choices=(
            (PARTICULAR, 'Particular'),
            (SOCIETY, 'Society')
        )
    )

    def __str__(self):
        return self.user.username + ' - ' + str(self.commercant_type)
#-----------------------------------------------------------------------------------------------------------------------
class Shop(models.Model):
    owner = models.ForeignKey(Trader)
    name = models.CharField(max_length=250)
    logo = models.ImageField(blank=True,null=True, upload_to=user_directory_path_four)
    description = models.CharField(max_length=1000)
    address = models.CharField(max_length=250)
    processing_time = models.FloatField(default=0)
    create_date = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.name + ' - ' + str(self.owner)
#-----------------------------------------------------------------------------------------------------------------------
class Category(models.Model):
   label = models.CharField(max_length=100)

   def __str__(self):
       return self.label
#-----------------------------------------------------------------------------------------------------------------------
class Product(models.Model):
    HAND_MADE = 'HM'
    VINTAGE = 'VTG'

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE,default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,default=1)
    name = models.CharField(max_length=250)
    principal_picture = models.ImageField(blank=True, null=True,upload_to=user_directory_path)
    price = models.FloatField()
    description = models.CharField(max_length=1000)
    is_active = models.BooleanField(default=False)
    en_promotion = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    product_type = models.CharField(
        max_length=20,
        blank=True,
        choices=(
            (HAND_MADE, 'Hand Made'),
            (VINTAGE, 'Vintage')
        )
    )

    def __str__(self):
        return self.name + ' - ' + str(self.price)
#-----------------------------------------------------------------------------------------------------------------------
class Picture(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,default=1)
    name = models.ImageField(blank=True,null=True,upload_to=user_directory_path_two)
#-----------------------------------------------------------------------------------------------------------------------
class Collection(models.Model):
    owner = models.ForeignKey(Trader, on_delete=models.CASCADE,default=1)
    product = models.ManyToManyField(Product, default=1)
    title = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000)
    image_collection = models.ImageField(blank=True, null=True,upload_to=user_directory_path_five)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.datetime.now())


    def __str__(self):
        return self.title

# -----------------------------------------------------------------------------------------------------------------------
class Promotion(models.Model):

    REGULAR = 'REGULAR'
    FLASH = 'FLASH'

    PRODUCT ='PR'
    COLLECTION = 'CO'

    title = models.CharField(max_length=20, default='')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, default=1)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    status = models.BooleanField(default=False)
    start_time = models.DateTimeField(default=datetime.datetime.now())
    end_time = models.DateTimeField(default=datetime.datetime.now())
    discount_value = models.IntegerField(default=10)
    is_active = models.BooleanField(default=False)

    promotion_type = models.CharField(
        max_length=20,
        blank=True,
        choices=(
            (REGULAR, 'Regular'),
            (FLASH, 'Flash')
        )
    )

    promotion_for = models.CharField(
        max_length=20,
        blank=True,
        choices=(
            (PRODUCT, 'Product'),
            (COLLECTION, 'Collection')
        )
    )


    def __str__(self):
        return self.title + ' - ' + str(self.discount_value)
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
class Album(models.Model):
    title = models.CharField(max_length=30, default='')
    description = models.CharField(max_length=3000, null=True)
    owner = models.ForeignKey(Trader, on_delete=models.CASCADE, default=1)
    album_image = models.ImageField(null=True, upload_to=user_directory_path_six)
    create_date = models.DateTimeField(default=datetime.datetime.now())


    def __str__(self):
        return self.title
#-----------------------------------------------------------------------------------------------------------------------
class Pic(models.Model):
    album = models.ForeignKey(Album)
    image = models.ImageField(blank=True,null=True,upload_to=user_directory_path_seven)
    name = models.CharField(max_length=10)
    details = models.CharField(max_length=1000, default='')
    create_date = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.name
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
class wish_category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    title = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000)
    image_category = models.ImageField(blank=True, null=True, upload_to=user_directory_path_five)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    def __str__(self):
        return self.title

class wish_list(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    wish_category=models.ForeignKey(wish_category,on_delete=models.CASCADE,default=0)
    produit=models.ForeignKey(Product,on_delete=models.CASCADE,default=0)

    class Meta:
        unique_together = ('user', 'wish_category', 'produit')