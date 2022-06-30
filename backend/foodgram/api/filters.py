from django_filters import rest_framework as django_filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    """Фильтрсет рецептов."""

    is_favorited = django_filters.BooleanFilter(
        method='get_is_favorited',
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )
    author = django_filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        )

    def get_is_favorited(self, queryset, name, value):
        cur_user = self.request.user
        if value:
            return Recipe.objects.filter(favorite_recipe__user=cur_user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        cur_user = self.request.user
        if value:
            return Recipe.objects.filter(cart__user=cur_user)
        return Recipe.objects.all()
