import json
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime
from Mesero.models import *

@method_decorator(csrf_exempt, name='dispatch')
class ListaPedidos(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtén la lista de pedidos con información del cliente y detalle del pedido
            pedidos = Pedidos.objects.filter(estado_del_pedido='O')

            # Formatea los datos
            data = []
            for pedido in pedidos:
                detalle_pedido_data = []
                for detalle_pedido in pedido.detallepedidos_set.all():
                    producto_data = {
                        'id_producto': detalle_pedido.id_producto.id_producto,
                        'nombreproducto': detalle_pedido.id_producto.nombreproducto,
                        'cantidad': detalle_pedido.cantidad,
                        'precio_unitario': detalle_pedido.precio_unitario,
                        'impuesto': detalle_pedido.impuesto,
                        'descuento': detalle_pedido.descuento,
                    }
                    detalle_pedido_data.append(producto_data)

                pedido_data = {
                    'id_pedido': pedido.id_pedido,
                    'cliente': {
                        'id_cliente': pedido.id_cliente.id_cliente,
                        'crazon_social': pedido.id_cliente.crazon_social,
                        'ctelefono': pedido.id_cliente.ctelefono,
                        'snombre': pedido.id_cliente.snombre,
                        'capellido': pedido.id_cliente.capellido,
                        'ccorreo_electronico': pedido.id_cliente.ccorreo_electronico,
                    },
                    'precio': pedido.precio,
                    'tipo_de_pedido': pedido.tipo_de_pedido,
                    'metodo_de_pago': pedido.metodo_de_pago,
                    'puntos': pedido.puntos,
                    'fecha_pedido': pedido.fecha_pedido,
                    'fecha_entrega': pedido.fecha_entrega,
                    'estado_del_pedido': pedido.estado_del_pedido,
                    'observacion_del_cliente': pedido.observacion_del_cliente,
                    'detalle_pedido': detalle_pedido_data,
                }

                data.append(pedido_data)

            return JsonResponse({'pedidos': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
@method_decorator(csrf_exempt, name='dispatch')
class TodosLosPedidos(View):
    def get(self, request, *args, **kwargs):
        try:
            pedidos = Pedidos.objects.all().values()
            pedidos_list = list(pedidos)
            return JsonResponse({'todos_los_pedidos': pedidos_list})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class TomarPedido(View):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():  
                id_mesero = request.POST.get('id_mesero', 1)
                id_mesa = request.POST.get('id_mesa')
                id_cliente_id = request.POST.get('id_cliente')
                fecha_pedido = datetime.now()
                tipo_de_pedido = request.POST.get('tipo_de_pedido')
                metodo_de_pago = request.POST.get('metodo_de_pago')
                puntos = request.POST.get('puntos')
                fecha_entrega = request.POST.get('fecha_entrega', None)
                estado_del_pedido = request.POST.get('estado_del_pedido')
                observacion_del_cliente = request.POST.get('observacion_del_cliente')
                
                cliente_instance = get_object_or_404(Clientes, id_cliente=id_cliente_id)

                nuevo_pedido = Pedidos.objects.create(
                    id_cliente=cliente_instance,
                    precio=0,
                    tipo_de_pedido=tipo_de_pedido,
                    metodo_de_pago=metodo_de_pago,
                    puntos=puntos,
                    fecha_pedido=fecha_pedido,
                    fecha_entrega=fecha_entrega,
                    estado_del_pedido=estado_del_pedido,
                    observacion_del_cliente=observacion_del_cliente,
                )

                mesero_instance = get_object_or_404(Meseros, id_mesero=id_mesero)
                mesa_instance = get_object_or_404(Mesas, id_mesa=id_mesa)
                Pedidosmesa.objects.create(
                    id_mesero=mesero_instance,
                    id_mesa=mesa_instance,
                    id_pedido=nuevo_pedido,
                )

                detalles_pedido_raw = request.POST.get('detalles_pedido', '{}')
                detalles_pedido = json.loads(detalles_pedido_raw)

                total_precio_pedido = 0
                for detalle_pedido_data in detalles_pedido['detalles_pedido']:
                    id_producto_id = detalle_pedido_data.get('id_producto')
                    id_combo_id = detalle_pedido_data.get('id_combo')
                    precio_unitario = float(detalle_pedido_data['precio_unitario'])
                    impuesto = float(detalle_pedido_data['impuesto'])
                    cantidad = float(detalle_pedido_data['cantidad'])
                    descuento = float(detalle_pedido_data.get('descuento', 0))
                    
                    precio_total_detalle = (precio_unitario * cantidad) + impuesto
                    precio_total_detalle -= descuento
                    total_precio_pedido += precio_total_detalle

                    if id_producto_id and not id_combo_id:  # Es un producto individual
                        producto_instance = get_object_or_404(Producto, id_producto=id_producto_id)
                        Detallepedidos.objects.create(
                            id_pedido=nuevo_pedido,
                            id_producto=producto_instance,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            impuesto=impuesto,
                            descuento=descuento,
                        )
                    elif id_combo_id and not id_producto_id:  # Es un combo
                        combo_instance = get_object_or_404(Combo, id_combo=id_combo_id)
                        Detallepedidos.objects.create(
                            id_pedido=nuevo_pedido,
                            id_combo=combo_instance,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            impuesto=impuesto,
                            descuento=descuento,
                        )

                nuevo_pedido.precio = total_precio_pedido
                nuevo_pedido.save()

                # Crear la factura asociada al pedido
                nueva_factura = Factura.objects.create(
                    id_pedido=nuevo_pedido,  # Utiliza el objeto de pedido en lugar del id
                    id_cliente=cliente_instance,
                    id_mesero=mesero_instance,
                    total=total_precio_pedido,
                )

                # Crear los detalles de la factura
                for detalle_pedido_data in detalles_pedido['detalles_pedido']:
                    id_producto_id = detalle_pedido_data.get('id_producto')
                    id_combo_id = detalle_pedido_data.get('id_combo')
                    cantidad = float(detalle_pedido_data['cantidad'])
                    precio_unitario = float(detalle_pedido_data['precio_unitario'])
                    descuento = float(detalle_pedido_data.get('descuento', 0))
                    valor = (precio_unitario * cantidad) - descuento

                    if id_producto_id and not id_combo_id:  # Es un producto individual
                        id_producto_instance = get_object_or_404(Producto, id_producto=id_producto_id)
                        DetalleFactura.objects.create(
                            id_factura=nueva_factura,
                            id_producto=id_producto_instance,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            descuento=descuento,
                            valor=valor,
                        )
                    elif id_combo_id and not id_producto_id:  # Es un combo
                        id_combo_instance = get_object_or_404(Combo, id_combo=id_combo_id)
                        DetalleFactura.objects.create(
                            id_factura=nueva_factura,
                            id_combo=id_combo_instance,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            descuento=descuento,
                            valor=valor,
                        )

                return JsonResponse({'mensaje': 'Pedido y factura creados con éxito'})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)

def ver_factura(request, id_pedido):
    print("ID de pedido recibido:", id_pedido)
    try:
        factura = Factura.objects.get(id_pedido_id=id_pedido)
        detalles_factura = DetalleFactura.objects.filter(id_factura_id=factura.id_factura).values()

        detalles_factura_list = list(detalles_factura)
        id_cliente = factura.id_cliente_id

        # Obtener información del pedido
        pedido = Pedidos.objects.get(pk=id_pedido)
        tipo_de_pedido = pedido.tipo_de_pedido
        metodo_de_pago = pedido.metodo_de_pago

        factura_data = {
            'id_factura': factura.id_factura,
            'id_cliente': id_cliente,
            'fecha_emision': factura.fecha_emision,
            'total': factura.total,
            'tipo_de_pedido': tipo_de_pedido,
            'metodo_de_pago': metodo_de_pago,  
            'detalles_factura': detalles_factura_list,
        }

        return JsonResponse(factura_data)
    except Factura.DoesNotExist:
        return JsonResponse({'error': 'La factura no existe'}, status=404)


def pedidos_del_mesero(request, id_mesa):
    try:
        
        id_mesero = request.POST.get('id_mesero', 1)

        # Obtener todos los pedidos asociados al mesero y a la mesa
        pedidos_del_mesero = Pedidosmesa.objects.filter(id_mesero=id_mesero, id_mesa=id_mesa)

        # Inicializar una lista para almacenar la información de los pedidos
        pedidos_info = []

        # Iterar sobre cada pedido asociado al mesero y a la mesa
        for pedido_mesa in pedidos_del_mesero:
            # Obtener la información del pedido
            pedido_info = {
                'id_pedido': pedido_mesa.id_pedido.id_pedido,
                'id_mesa': pedido_mesa.id_mesa.id_mesa,
                'fecha_pedido': pedido_mesa.id_pedido.fecha_pedido,
                # Otros campos del pedido que quieras mostrar
            }
            pedidos_info.append(pedido_info)

        return JsonResponse({'pedidos_del_mesero': pedidos_info})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)