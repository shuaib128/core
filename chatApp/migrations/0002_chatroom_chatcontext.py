# Generated by Django 3.2.18 on 2023-03-19 22:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='chatContext',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ChatContent', to='chatApp.chatmessage'),
        ),
    ]