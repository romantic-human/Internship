"""用户模块序列化器 — 参考《组织架构模块设计方案.md》第 5.2 节"""
from rest_framework import serializers
from .models import User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
        }


class UserListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.dept_name", read_only=True)
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "nickname", "real_name", "email", "telephone",
            "gender", "department_id", "department_name", "role_name",
            "status", "last_login", "create_time",
        ]

    def get_role_name(self, obj):
        """通过 prefetch 的用户角色关联获取角色名列表"""
        relations = obj.userrolerelation_set.all()
        names = [r.role.role_name for r in relations if r.role.status == 1]
        return "、".join(names) if names else ""


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)


class RefreshTokenSerializer(serializers.Serializer):
    """刷新 Token — 校验 refresh_token 是否存在"""
    refresh = serializers.CharField(required=True)


class UserCreateSerializer(serializers.ModelSerializer):
    """创建用户（注册 / 后台新增通用）"""
    password = serializers.CharField(write_only=True, required=False, default="123456")
    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=User._meta.get_field("department").related_model.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = [
            "id", "username", "password", "nickname", "real_name",
            "email", "telephone", "gender", "department_id", "status",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password", "123456")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """个人资料 — GET 返回详情，PUT 部分更新"""

    class Meta:
        model = User
        fields = [
            "id", "username", "nickname", "real_name", "email",
            "telephone", "gender", "avatar", "department_id",
        ]
        read_only_fields = ["id", "username"]