from rest_framework import permissions


class IsRecipeAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Проверяем, является ли текущий пользователь автором рецепта
        return obj.author == request.user
