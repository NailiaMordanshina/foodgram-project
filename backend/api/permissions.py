from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешить только GET-запросы для неавторизованных пользователей
        return request.method == 'GET' or request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Разрешить доступ для всех к просмотру (GET-запросам)
        return request.method == 'GET'


# class IsRecipeAuthor(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # Проверяем, является ли текущий пользователь автором рецепта
#         return obj.author == request.user


# class IsOwnerOrReadOnly(permissions.BasePermission):
#     """
#     Пользователи могут редактировать свои собственные объекты, но не могут редактировать чужие.
#     """
    # def has_object_permission(self, request, view, obj):
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #     return obj.author == request.user


