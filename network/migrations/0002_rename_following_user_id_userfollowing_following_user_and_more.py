# Generated by Django 4.1.7 on 2023-09-04 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userfollowing',
            old_name='following_user_id',
            new_name='following_user',
        ),
        migrations.RenameField(
            model_name='userfollowing',
            old_name='user_id',
            new_name='user',
        ),
    ]
