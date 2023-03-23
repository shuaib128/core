# Generated by Django 3.2.18 on 2023-03-20 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatApp', '0003_alter_chatroom_chatcontext'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatroom',
            name='chatContext',
        ),
        migrations.AddField(
            model_name='chatroom',
            name='chatContext',
            field=models.ManyToManyField(blank=True, null=True, related_name='ChatContent', to='chatApp.ChatMessage'),
        ),
    ]
