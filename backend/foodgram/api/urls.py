from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (AddAndDeleteSubscribe, AddDeleteFavoriteRecipe,
                       AddDeleteShoppingCart, CustomUserViewSet,
                       DownloadShoppingCart, IngredientViewSet, RecipeViewSet,
                       SubscriptionsView, TagViewSet, set_password)

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)


urlpatterns = [
     path(
          'users/set_password/',
          set_password,
          name='set_password'),
     path(
          'users/<int:user_id>/subscribe/',
          AddAndDeleteSubscribe.as_view(),
          name='subscribe'),
     path(
        'users/subscriptions/',
        SubscriptionsView.as_view(),
        name='subscriptions'),
     path(
          'recipes/<int:recipe_id>/favorite/',
          AddDeleteFavoriteRecipe.as_view(),
          name='favorite_recipe'),
     path(
          'recipes/<int:recipe_id>/shopping_cart/',
          AddDeleteShoppingCart.as_view(),
          name='shopping_cart'),
     path('recipes/download_shopping_cart/',
          DownloadShoppingCart.as_view({'get': 'download'}), name='download'),
     path('', include(router.urls)),
     path('auth/', include('djoser.urls.authtoken')),
     path('', include('djoser.urls')),
]
