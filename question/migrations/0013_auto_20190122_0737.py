# Generated by Django 2.1.5 on 2019-01-22 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0012_auto_20190122_0726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='likedislike',
            name='vote',
            field=models.SmallIntegerField(choices=[(-1, 'UP'), (1, 'DOWN')], default=0, verbose_name='vote'),
        ),
    ]
