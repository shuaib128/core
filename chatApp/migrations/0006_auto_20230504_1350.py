# Generated by Django 3.2.18 on 2023-05-04 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatApp', '0005_auto_20230327_1014'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Video Name', max_length=10000)),
                ('video', models.FileField(blank=True, null=True, upload_to='media/chatVideos')),
            ],
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='videos',
            field=models.ManyToManyField(blank=True, null=True, related_name='videos', to='chatApp.ChatVideo'),
        ),
    ]