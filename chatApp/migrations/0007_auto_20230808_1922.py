# Generated by Django 3.2.18 on 2023-08-09 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatApp', '0006_auto_20230504_1350'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(default='', max_length=255)),
                ('file', models.FileField(blank=True, upload_to='media/postsMedia')),
            ],
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='images',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='videos',
        ),
        migrations.DeleteModel(
            name='ChatImage',
        ),
        migrations.DeleteModel(
            name='ChatVideo',
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='media_files',
            field=models.ManyToManyField(blank=True, null=True, related_name='media', to='chatApp.MediaFile'),
        ),
    ]
