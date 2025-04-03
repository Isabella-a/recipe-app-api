from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from rest_framework.parsers import MultiPartParser, FormParser
from core.models import Recipe, Tag, Ingredient
from .serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer, IngredientSerializer, \
    RecipeImageSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='tags',
                type=OpenApiTypes.STR,
                description='Comma separated list of tags IDs to filter,'
            ),
            OpenApiParameter(
                name='ingredients',
                type=OpenApiTypes.STR,
                description='Comma separated list of ingredients IDs to filter'
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recipes.
    Supports filtering by tags and ingredients.
    Only authenticated users have access.
    """
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """" Convert a list of string IDs to a list of integers """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """" Retrive recipes for authenticated users """
        tags = self.request.query_params.get('tags', None)
        ingredients = self.request.query_params.get('ingredients', None)
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """" Return the serializer class to use for the request"""
        if self.action == 'list':
            return RecipeSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(request=RecipeImageSerializer)
    @action(
        detail=True,
        methods=['post'],
        url_path='upload-image',
        parser_classes = [MultiPartParser, FormParser]
    )
    def upload_image(self, request, pk=None):
        """" Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='assign_only',
                type=OpenApiTypes.INT, enum=[0,1],
                description='Filter by items assigned to recipes',
            )
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """" Base viewset for recipe attributes. """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """" Filter queryset to authenticated users"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user).order_by('-name').distinct()



class TagViewSet(BaseRecipeAttrViewSet):
    """" Manage tags in the database"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
