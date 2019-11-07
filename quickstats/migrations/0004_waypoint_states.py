# Generated by Django 2.2.1 on 2019-11-07 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickstats', '0003_widget_body_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waypoint',
            name='state',
            field=models.CharField(choices=[('', 'Unselected'), ('enter', 'Entered an Area'), ('leave', 'Exited an Area'), ('waypoint', 'Waypoint')], max_length=16),
        ),
    ]
