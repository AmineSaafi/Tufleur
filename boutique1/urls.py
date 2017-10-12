from django.conf.urls import url
from . import views

app_name = 'boutique1'




urlpatterns = [
    #-------------------------------------------------------------------------------------------------------------------
    #Registration
    #-------------------------------------------------------------------------------------------------------------------
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    #-------------------------------------------------------------------------------------------------------------------
    #Discover
    #-------------------------------------------------------------------------------------------------------------------
    url(r'^$', views.discover, name='index'),
    url(r'^shop_products/(?P<shop_id>[0-9]+)/$', views.shopSProducts, name='shopSProducts'),
    url(r'^discover/(?P<category>[\w\-]+)/$', views.discover, name='discover_category'),
    url(r'^discover/$', views.discover, name='discover'),
    #-------------------------------------------------------------------------------------------------------------------
    #Shops
    #-------------------------------------------------------------------------------------------------------------------
    url(r'^myShops$', views.myShops, name='myShops'),
    url(r'^create_shop/$', views.create_shop, name='create_shop'),
    url(r'^edit_shop/(?P<shop_id>[0-9]+)/$', views.edit_shop, name='edit_shop'),
    url(r'^(?P<shop_id>[0-9]+)/delete_boutique/$', views.delete_shop, name='delete_shop'),
    url(r'^(?P<shop_id>[0-9]+)/$', views.shopDetails, name='shopDetails'),
    #-------------------------------------------------------------------------------------------------------------------
    #Products
    #-------------------------------------------------------------------------------------------------------------------
    url(r'^(?P<shop_id>[0-9]+)/product_detail/(?P<product_id>[0-9]+)/$', views.prodDetails, name='prodDetails'),
    url(r'^(?P<shop_id>[0-9]+)/duplicate_product/(?P<prod_id>[0-9]+)/$', views.duplicate_product, name='duplicate_product'),
    url(r'^(?P<shop_id>[0-9]+)/edit_product/(?P<prod_id>[0-9]+)/$', views.edit_product, name='edit_product'),
    url(r'^(?P<shop_id>[0-9]+)/create_product/$', views.create_product, name='create_product'),
    url(r'^(?P<shop_id>[0-9]+)/delete_product/(?P<product_id>[0-9]+)/$', views.delete_product, name='delete_product'),
    url(r'^product/(?P<id_product>[0-9]+)$', views.product, name='product'),
    url(r'^(?P<shop_id>[0-9]+)/product_status/(?P<prod_id>[0-9]+)/$', views.activate_product, name='activate_product'),
    #url(r'^(?P<shop_id>[0-9]+)/shop_products/(?P<product_id>[0-9]+)/$', views.shopSProducts, name='shopSProducts'),
    #-------------------------------------------------------------------------------------------------------------------
    #Collections
    #-------------------------------------------------------------------------------------------------------------------
    url(r'^(?P<shop_id>[0-9]+)/mycollections/$', views.myCollections, name='myCollections'),
    url(r'^(?P<shop_id>[0-9]+)/collections/details/(?P<coll_id>[0-9]+)$', views.collection_detail, name='collection_detail'),
    url(r'^(?P<shop_id>[0-9]+)/create_collection/$', views.create_collection, name='create_collection'),
    url(r'^(?P<shop_id>[0-9]+)/collections/edit/(?P<coll_id>[0-9]+)$', views.edit_collection, name='edit_collection'),
    url(r'^(?P<shop_id>[0-9]+)/collections/delete/(?P<coll_id>[0-9]+)$', views.delete_collection,
        name='delete_collection'),
    url(r'^(?P<shop_id>[0-9]+)/collection_status/(?P<coll_id>[0-9]+)/$', views.activate_collection, name='activate_collection'),
    #url(r'^collections/(?P<collection_id>[0-9]+)/$', views.detail_collection, name='collectionDetails'),
    #-------------------------------------------------------------------------------------------------------------------
    #Promotions
    #-------------------------------------------------------------------------------------------------------------------
    url(r'^(?P<shop_id>[0-9]+)/promotions/$', views.promotions, name='promotions'),
    url(r'^(?P<shop_id>[0-9]+)/promotions/new/$', views.create_promotion, name='create_promotion'),
    url(r'^(?P<shop_id>[0-9]+)/promotions/delete/(?P<promo_id>[0-9]+)$', views.delete_promotion,name='delete_promotion'),
    url(r'^(?P<shop_id>[0-9]+)/promotions/edit/(?P<promo_id>[0-9]+)$', views.edit_promotion, name='edit_promotion'),
    url(r'^(?P<shop_id>[0-9]+)/promotions/details/(?P<promo_id>[0-9]+)$', views.promotion_detail,name='promotion_detail'),
    #-------------------------------------------------------------------------------------------------------------------
    #REST API
    #-------------------------------------------------------------------------------------------------------------------  
    url(r'^create/$', views.ProductCreateAPIView.as_view(), name='create'),
    #-------------------------------------------------------------------------------------------------------------------
    #Albums
    #-------------------------------------------------------------------------------------------------------------------
    url(r'^(?P<shop_id>[0-9]+)/create_album/$', views.create_album, name='create_album'),
    url(r'^(?P<shop_id>[0-9]+)/all_albums/$', views.allAlbums, name='allAlbums'),
    url(r'^(?P<shop_id>[0-9]+)/albums/edit/(?P<album_id>[0-9]+)/$', views.edit_album, name='edit_album'),
    url(r'^(?P<shop_id>[0-9]+)/albums/delete/(?P<album_id>[0-9]+)/$', views.delete_album,name='delete_album'),
    url(r'^(?P<shop_id>[0-9]+)/album/details/(?P<album_id>[0-9]+)/$', views.albumDetails,name='albumDetails'),
    #-------------------------------------------------------------------------------------------------------------------
    #Pics
    #-------------------------------------------------------------------------------------------------------------------
    url(r'^(?P<shop_id>[0-9]+)/album/(?P<album_id>[0-9]+)/add_pic/$', views.add_pic, name='add_pic'),
    #url(r'^(?P<shop_id>[0-9]+)/all_albums/$', views.allAlbums, name='allAlbums'),
    #url(r'^(?P<shop_id>[0-9]+)/albums/edit/(?P<album_id>[0-9]+)/$', views.edit_album, name='edit_album'),
    url(r'^(?P<shop_id>[0-9]+)/album/(?P<album_id>[0-9]+)/delete_pic/(?P<pic_id>[0-9]+)/$', views.delete_pic,name='delete_pic'),
    #url(r'^(?P<shop_id>[0-9]+)/album/details/(?P<album_id>[0-9]+)$', views.albumDetails,name='albumDetails'),
    #-------------------------------------------------------------------------------------------------------------------
    #WishList
    #-------------------------------------------------------------------------------------------------------------------
    url(r'^create_wishcategory/$', views.create_wish_category, name='create_wish_category'),
    url(r'^my_categorys/$', views.my_categorys, name='my_categorys'),
    url(r'^delete_category/(?P<category_id>[0-9]+)/$', views.delete_category, name='delete_category'),
    url(r'^edit_category/(?P<category_id>[0-9]+)/$', views.edit_category, name='edit_category'),
    url(r'^category_add_product/(?P<category_id>[0-9]+)/$', views.create_wish_list, name='create_wish_list'),
    url(r'^add_product/(?P<category_id>[0-9]+)/(?P<prod_id>[0-9]+)/$', views.addprod, name='addprod'),
    url(r'^categoryProds/(?P<category_id>[0-9]+)/$', views.detailcategory, name='detailcategory'),
    url(r'^(?P<category_id>[0-9]+)/(?P<produit_id>[0-9]+)/delete_wishlist_produit/$', views.delete_category_produit,
        name='delete_category_produit'),

    url(r'^wishlist/$', views.create_wish_list, name='create_wish_list'),
]
