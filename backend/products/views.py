from rest_framework import generics, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer
from api.mixins import StaffEditorPermissionMixin, UserQuerySetMixin


class ProductListCreateAPIView(UserQuerySetMixin, generics.ListCreateAPIView, StaffEditorPermissionMixin):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        # email = serializer.validated_data.pop('email')
        # serializer.save(user=self.request.user)
        title = serializer.validated_data.get('title')
        content = serializer.validated_data.get('content') or None
        if content is None:
            content = title
        serializer.save(user=self.request.user, content=content) # like form.save() or model.dave()

    # def get_queryset(self, *args, **kwargs):
    #     qs =  super().get_queryset(*args, **kwargs)
    #     request = self.request
    #     user = request.user
    #     if not user.is_authenticated:
    #         return Product.objects.none()
    #     # print(request.user)
    #     return qs.filter(user=request.user)

class ProductDetailAPIView(UserQuerySetMixin, StaffEditorPermissionMixin, generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductUpdateAPIView(UserQuerySetMixin, StaffEditorPermissionMixin, generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        if not instance.content:
            instance.content = instance.title

class ProductDeleteAPIView(UserQuerySetMixin, StaffEditorPermissionMixin, generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def perform_delete(self, instance):
        super().perform_delete(instance)

# class ProductListAPIView(generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#handles list view and detail view
class ProductMixinView(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk' # RetrieveModelMixin

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
    
        if pk is not None:
            return self.retrieve(request, *args, **kwargs)
    
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# Same as generic above but list based views!
@api_view(['GET', 'POST'])
def product_alt_view(request, pk=None, *args, **kwargs):
    method = request.method

    if method == "GET":
        if pk is not None:
            # detail view
            obj = get_object_or_404(Product, pk=pk)
            data = ProductSerializer(obj, many=False).data
            return Response(data)

        #list view
        queryset = Product.objects.all()
        data = ProductSerializer(queryset, many=True).data
        return Response(data)

    if method == "POST":
        # Create ITEM
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            title = serializer.validated_data.get('title')
            content = serializer.validated_data.get('content') or None
            if content is None:
                content = title
            serializer.save(content=content)
            return Response(serializer.data)
        return Response({"invalid data": "not good data"}, status=400)


product_mixin_view = ProductMixinView.as_view()
product_list_create_view = ProductListCreateAPIView.as_view()
product_detail_view = ProductDetailAPIView.as_view()
product_update_view = ProductUpdateAPIView.as_view()
product_delete_view = ProductDeleteAPIView.as_view()


