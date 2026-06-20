from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Override groups and user_permissions with custom related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

      
        """ 
        In settings.py:
python
AUTH_USER_MODEL = 'accounts.User'
Key Points:
Keep username as default - No need to change USERNAME_FIELD or REQUIRED_FIELDS

Only add custom fields - email, phone, avatar, etc.

Override groups and user_permissions with unique related_name to avoid clashes

Email is unique but used for communication, not authentication

------------
✅ Uses the standard Django authentication flow with username

✅ Adds custom fields for your user model

✅ Avoids the reverse accessor clash

✅ Simpler and more maintainable

✅ Works with Django's built-in authentication views and forms

If you want to allow login with either username OR email later,
 you can create a custom authentication backend, but keeping username as 
 the primary authentication field is the most straightforward approach.
        
        """