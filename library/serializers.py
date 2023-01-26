from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as email_validator
from rest_framework import serializers

from .models import (
    AuthorModel,
    BaseModel,
    BookModel,
    CategoryModel,
    PublisherModel,
    FavoritesModel
)


from rest_framework_jwt.serializers import JSONWebTokenSerializer

from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext as _
from rest_framework import serializers

from rest_framework_jwt.settings import api_settings


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(
            validated_data["username"], validated_data["email"], validated_data["password"]
        )

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_email(self, value):
        email_validator(value)
        return value

    def validate_username(self, value):
        # for some reason User object of the django doesn't raise a validation error
        # when the length of the username is less than 8? so raise it manually
        if len(value) >= 8:
            return value
        else:
            raise ValidationError(
                message="Username length must be greater than 7", code=400)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")

    def update(self, instance, validated_data):
        password = validated_data.get("password", instance.password)
        instance.set_password(password)
        return super(UserSerializer, self).update(instance, validated_data)


class LibraryBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseModel
        exclude = (
            "is_test_data",
            "created_at",
            "modified_at",
            "created_by",
            "modified_by",
            "deleted_at",
            "deleted_by",
        )
        depth = 1


class AuthorSerializer(LibraryBaseSerializer):
    class Meta(LibraryBaseSerializer.Meta):
        model = AuthorModel


class CategorySerializer(LibraryBaseSerializer):
    class Meta(LibraryBaseSerializer.Meta):
        model = CategoryModel


class PublisherSerializer(LibraryBaseSerializer):
    class Meta(LibraryBaseSerializer.Meta):
        model = PublisherModel


class BookSerializer(LibraryBaseSerializer):
    # adding serializers manually ensured that base serializer is being called on each request,
    # otherwise every data about the foreign keys are shown
    # this way exclude field on the base is obeyed
    author = AuthorSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    publisher = PublisherSerializer(many=False, read_only=True)

    class Meta(LibraryBaseSerializer.Meta):
        model = BookModel


class FavoriteSerializer(LibraryBaseSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta(LibraryBaseSerializer.Meta):
        model = FavoritesModel


User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class CustomJWTSerializer(JSONWebTokenSerializer):
    username_field = 'email'

    def validate(self, attrs):

        password = attrs.get("password")
        user_obj = User.objects.filter(
            email=attrs.get("email")).first()
        if user_obj is not None:
            credentials = {
                'username': user_obj.username,
                'password': password
            }
            if all(credentials.values()):
                user = authenticate(**credentials)
                if user:
                    if not user.is_active:
                        msg = _('User account is disabled.')
                        raise serializers.ValidationError(msg)

                    payload = jwt_payload_handler(user)

                    return {
                        'token': jwt_encode_handler(payload),
                        'user': user
                    }
                else:
                    msg = _('Unable to log in with provided credentials.')
                    raise serializers.ValidationError(msg)

            else:
                msg = _('Must include "{username_field}" and "password".')
                msg = msg.format(username_field=self.username_field)
                raise serializers.ValidationError(msg)

        else:
            msg = _('Account with this email does not exists')
            raise serializers.ValidationError(msg)
