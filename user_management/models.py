from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
import uuid


# Create your models here.
class UserRoles(models.Model):
    """Database model for user roles in system"""

    class Meta:
        db_table = "user_roles"
        verbose_name_plural = "User Roles"

    role = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    uu_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    REQUIRED_FIELDS = ["role"]

    def __unicode__(self) -> str:
        """
        String unicode representation of UserRoles object

        Returns:
            str: Role
        """
        return self.role

    def get_user_role(self) -> str:
        """
        Retrieve full name of user

        Returns:
            str: Role
        """
        return self.role

    def __str__(self) -> str:
        """
        Return string representation of the user

        Returns:
            str: Role
        """
        return self.role


class UserProfileManager(BaseUserManager):
    """Manager for user profile"""

    def create_user(self, email, first_name, last_name, employee_id, role, dob=None, gender=None, mobile_no=None,
                    password=None):
        """
        Create a new user profile by django cli

        Args:
            email (str): Email of user
            first_name (str): Name of user
            role (int): Role primary ID
            password (str, optional): Password of user. Defaults to None.


        Raises:
            ValueError: Email required

        Returns:
            UserProfile: UserProfile object
        """
        if not email:
            raise ValueError("User email address not provided")

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, employee_id=employee_id,
                          date_of_birth=dob, gender=gender, phone_no=mobile_no)
        user.role = UserRoles.objects.get(id=role)
        user.set_password(password)
        user.is_superuser = False
        user.save(using=self._db)

        return user

    def create_superuser(self, first_name, last_name, employee_id, email, role, password):
        """
        Create a new user profile as a super user by django cli

        Args:
            email (str): Email of user
            first_name (str): Name of user
            role (int): Role of primary ID
            password (str): Password of user

        Returns:
            UserProfile: UserProfile object
        """
        user = self.create_user(email=email, first_name=first_name, last_name=last_name, employee_id=employee_id,
                                role=role, password=password)

        user.is_superuser = True
        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for users in system"""

    class Meta:
        db_table = "user_profile"
        verbose_name_plural = "User Profiles"

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255, unique=True)
    image = models.CharField(max_length=255)
    phone_no = models.BigIntegerField(null=True)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    role = models.ForeignKey("UserRoles", on_delete=models.SET_NULL, null=True)
    uu_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    pass_token = models.CharField(max_length=255, null=True)
    token_time = models.DateTimeField(null=True)
    password_updt_time = models.DateTimeField(null=True)
    objects = UserProfileManager()

    USERNAME_FIELD = "employee_id"
    REQUIRED_FIELDS = ["email", "role", "first_name", "last_name"]

    def get_full_name(self):
        """
        Retrieve full name of user

        Returns:
            str: User's Name
        """
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        """
        Retrieve short name of user

        Returns:
            str: User's Name
        """
        return self.first_name

    def get_profile_dp(self):
        """
        Retrieve user's profile image data

        Returns:
            str: User's Image data
        """
        return self.image

    def __str__(self) -> str:
        return self.email

class Group(models.Model):
    class Meta:
        db_table = 'group'
        verbose_name_plural = 'Groups'

    name = models.CharField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, default="")
    created_by = models.ForeignKey("UserProfile", related_name='group_creator', null=True, on_delete=models.SET_NULL)
    created_time = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('UserProfile', related_name='group_editor', null=True, on_delete=models.SET_NULL)
    updated_time = models.DateTimeField(null=True)
    uu_id = models.UUIDField(unique=True, default=uuid.uuid4, primary_key=True, editable=False)

    def __str__(self):
        return self.name

class UserGroup(models.Model):
    class Meta:
        db_table = 'users_group'
        verbose_name_plural = 'Groups Users'
        unique_together = (('group', 'user'), )

    group = models.ForeignKey('Group', on_delete=models.PROTECT, null=False)
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=False)
    created_by = models.ForeignKey('UserProfile', related_name='gu_creator', null=True, on_delete=models.SET_NULL)
    created_time = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('UserProfile', related_name='gu_editor', null=True, on_delete=models.SET_NULL)
    updated_time = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.user) + ":" + str(self.group)