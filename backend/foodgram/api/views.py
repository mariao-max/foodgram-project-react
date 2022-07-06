from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.aggregates import Count
from django.db.models.expressions import Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import GetObjectMixin, PermissionAndPaginationMixin
from api.pagination import LimitFieldPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from api.serializers import (CustomUserSerializer, IngredientSerializer,
                             RecipeSerializer, RecipeWriteSerializer,
                             SubscribeSerializer, SubscriptionSerializer,
                             TagSerializer, UserPasswordSerializer)

User = get_user_model()


class TagViewSet(
        PermissionAndPaginationMixin,
        viewsets.ModelViewSet):
    """Список тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для работы с пользователями.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с запросами о рецептах - просмотр списка рецептов,
    просмотр отдельного рецепта, создание, изменение и удаление рецепта.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeWriteSerializer


class IngredientViewSet(PermissionAndPaginationMixin,
                        viewsets.ModelViewSet):
    """
    Вьюсет для получения списка ингредиентов и отдельного ингредиента.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filterset_class = IngredientFilter


class AddAndDeleteSubscribe(
        generics.RetrieveDestroyAPIView,
        generics.ListCreateAPIView):
    """Подписка и отписка от пользователя."""

    permission_classes = (IsAuthenticated,)
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.follower.select_related(
            'following'
        ).prefetch_related(
            'following__recipes'
        ).annotate(
            recipes_count=Count('following__recipes'),
            is_subscribed=Value(True), )

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.id:
            return Response(
                {'errors': 'На самого себя не подписаться!'},
                status=status.HTTP_400_BAD_REQUEST)
        if request.user.follower.filter(author=instance).exists():
            return Response(
                {'errors': 'Уже подписан!'},
                status=status.HTTP_400_BAD_REQUEST)
        subs = request.user.follower.create(author=instance)
        serializer = self.get_serializer(subs)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.follower.filter(author=instance).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(ListAPIView):
    """
    Вьюсет для работы с запросом о подписках пользователя
    """
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitFieldPagination
    serializer_class = SubscriptionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        cur_user = self.request.user
        return User.objects.filter(
            following__user=cur_user
        )


class AddDeleteFavoriteRecipe(GetObjectMixin,
                              generics.RetrieveDestroyAPIView,
                              generics.ListCreateAPIView):

    """Добавление и удаление рецепта в/из избранных."""

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.favorite_recipe.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.favorite_recipe.recipe.remove(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddDeleteShoppingCart(GetObjectMixin,
                            generics.RetrieveDestroyAPIView,
                            generics.ListCreateAPIView):
    """Добавление и удаление рецепта в/из корзины."""

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.cart.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.cart.recipe.remove(instance)


class DownloadShoppingCart(viewsets.ModelViewSet):
    """
    Сохранение файла списка покупок.
    """
    permission_classes = [IsAuthenticated]

    def download_pdf(self, result):
        """
        Метод сохранения списка покупок в формате PDF.
        """
        response = HttpResponse(content_type='application/pdf')
        response[
            'Content-Disposition'
            ] = ('attachment; filename="somefilename.pdf"')
        p = canvas.Canvas(response, pagesize=A4)
        left_position = 50
        top_position = 700
        pdfmetrics.registerFont(TTFont('FreeSans',
                                       'recipes/fonts/FreeSans.ttf'))
        p.setFont('FreeSans', 25)
        p.drawString(left_position, top_position + 40, "Список покупок:")

        for number, item in enumerate(result, start=1):
            pdfmetrics.registerFont(
                TTFont('Miama Nueva', 'recipes/fonts/Miama Nueva.ttf')
                )
            p.setFont('Miama Nueva', 14)
            p.drawString(
                left_position,
                top_position,
                f'{number}.  {item["ingredient__name"]} - '
                f'{item["ingredient_total"]}'
                f'{item["ingredient__measurement_unit"]}'
            )
            top_position = top_position - 40

        p.showPage()
        p.save()
        return response

    def download(self, request):
        """
        Метод создания списка покупок.
        """
        result = RecipeIngredient.objects.filter(
            recipe__cart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').order_by(
                'ingredient__name').annotate(ingredient_total=Sum('amount'))
        return self.download_pdf(result)


@api_view(['post'])
def set_password(request):
    """Изменить пароль."""

    serializer = UserPasswordSerializer(
        data=request.data,
        context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пароль изменен!'},
            status=status.HTTP_201_CREATED)
    return Response(
        {'error': 'Введите верные данные!'},
        status=status.HTTP_400_BAD_REQUEST)
