# Generated by Django 5.0 on 2023-12-24 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Horariossemanales',
            fields=[
                ('id_horarios', models.AutoField(primary_key=True, serialize=False)),
                ('hordescripcion', models.CharField(blank=True, max_length=500, null=True)),
                ('tipohorario', models.CharField(max_length=1)),
                ('nombreh', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'horariossemanales',
                'managed': False,
            },
        ),
    ]