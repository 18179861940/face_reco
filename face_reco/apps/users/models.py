from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone


class AttendCard(models.Model):
    userName = models.CharField(max_length=20)
    userCode = models.CharField(max_length=20)
    attendType = models.CharField(max_length=10, verbose_name='打卡类型', choices=(('1', '上班打卡'), ('2', '下班打卡')),
                                  default='1')
    attendState = models.CharField(max_length=10, verbose_name='打卡状态',
                                   choices=(('1', '正常 '), ('2', '迟到'), ('3', '早退'), ('4', '缺卡')), default='1')
    pushTime = models.DateTimeField(auto_now_add=True, verbose_name="打卡时间")
    is_delete = models.BooleanField(default=False)  # 是否删除
    face_image = models.ImageField(upload_to="attendFace", blank=True, null=True, verbose_name='打卡证据图片')

    @property
    def face_image_url(self):
        if self.face_image and hasattr(self.face_image, 'url'):
            return self.face_image.url
    class Meta:
        db_table = 'card_table'


class UserTable(models.Model):
    userName = models.CharField(max_length=20)
    userCode = models.CharField(max_length=20)
    sex = models.CharField(max_length=10, verbose_name='性别',
                                   choices=(('1', '男 '), ('2', '女')), default='1')
    state = models.CharField(max_length=10, verbose_name='在职状态',
                                   choices=(('1', '在职'), ('2', '离职')), default='1')
    insertTime = models.DateTimeField(auto_now_add=True, verbose_name="录入时间")
    is_delete = models.BooleanField(default=False)  # 是否删除

    class Meta:
        db_table = 'user_table'
