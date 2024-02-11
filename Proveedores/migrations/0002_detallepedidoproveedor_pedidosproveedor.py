# Generated by Django 5.0.1 on 2024-01-31 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proveedores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Detallepedidoproveedor',
            fields=[
                ('id_detallepedidoproveedor', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=9)),
                ('costounitario', models.DecimalField(decimal_places=2, max_digits=9)),
            ],
            options={
                'db_table': 'detallepedidoproveedor',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Pedidosproveedor',
            fields=[
                ('id_pedidoproveedor', models.AutoField(primary_key=True, serialize=False)),
                ('fechapedido', models.DateTimeField()),
                ('fechaentregaesperada', models.DateTimeField(blank=True, null=True)),
                ('estado', models.CharField(max_length=1)),
                ('observacion', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'db_table': 'pedidosproveedor',
                'managed': False,
            },
        ),
    ]