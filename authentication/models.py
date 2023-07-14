from django.db import models
from user_management.models import UserProfile

class UserLoginHistory(models.Model):
    class Meta:
        db_table = "user_login_history"
        verbose_name_plural = "User Login Histories"

    user = models.ForeignKey(
        UserProfile, related_name="login_user", on_delete=models.CASCADE
    )
    logintime = models.DateTimeField(auto_now=True)
    logouttime = models.DateTimeField(null=True)
    IP = models.CharField(max_length=255)
    activity = models.JSONField(null=True)


    def __str__(self) -> str:
        return self.user.email + " " + str(self.logintime)
