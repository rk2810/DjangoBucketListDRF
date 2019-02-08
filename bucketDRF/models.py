from django.db import models

# Create your models here.


class Users(models.Model):
    name = models.CharField(max_length=25)
    username = models.CharField(unique=True, max_length=10)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    flag = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'users'


class Notes(models.Model):
    title = models.CharField(max_length=50)
    details = models.CharField(max_length=500, blank=True, null=True)
    archived = models.BooleanField(default=False)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    flag = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notes'
