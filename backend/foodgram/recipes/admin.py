from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscribe, Tag)

EMPTY_MSG = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        '_get_number_additions_to_favourite',

        )
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id')
    list_filter = ('name', 'measurement_unit')
    search_fields = ('name',)
    search_help_text = 'поиск по ингридиентам'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', 'id')
    search_fields = ('name',)
    prepopulated_fields = {
        'slug': ('name',),
    }


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'id')
    list_filter = ('user', 'recipe')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount', 'id')
    list_filter = ('ingredient', 'recipe', 'amount')


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'created', 'id')
    list_filter = ('user', 'author', 'created')


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'id')
    list_filter = ('user', 'id')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
