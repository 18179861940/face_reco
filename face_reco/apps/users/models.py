from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone


class User(models.Model):
    name = models.CharField(max_length=20)
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="上班时间")    # 上班时间
    end_time = models.DateTimeField(auto_now=True, verbose_name="下班班时间")    # 下班班时间
    is_delete = models.BooleanField(default=0)  # 是否删除
