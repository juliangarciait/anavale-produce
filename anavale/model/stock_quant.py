# -*- coding: utf-8 -*-
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    sale_order_quantity = fields.Float(
        'Quantity in Sale Order', compute='_compute_sale_order_qty',
        help='Quantity of products in this quant in Sale Orders but not yet Reserved in a Stock Picking , in the default unit of measure of the product',
        store=True, readonly=True, groups='anavale.group_sale_lot_calculation')
        
    available_quantity = fields.Float(
        'Quantity available for Sell', compute='_compute_sale_order_qty',
        help='Quantity of products in this quant avaiable for Sell including in-transit stock, in the default unit of measure of the product',
        store=True, readonly=True, groups='anavale.group_sale_lot_calculation')
        
    def _compute_sale_order_qty(self):
        # Solo calcular si el usuario tiene permisos para ver estos campos
        if not self.env.user.has_group('anavale.group_sale_lot_calculation'):
            for quant in self:
                quant.sale_order_quantity = 0
                quant.available_quantity = quant.quantity
            return
            
        for quant in self.sudo():
            args = [quant.product_id.id]
            sql = """
                        SELECT sol.id
                            FROM sale_order_line sol
                            LEFT JOIN sale_order so
                                on sol.order_id = so.id
                            where so.state = 'sale'
                                and product_id = %s                                
                    """
            if quant.lot_id:
                sql += """ and lot_id = %s """
                args.append(quant.lot_id.id)
            self._cr.execute(sql, tuple(args))
            ids = [item.get('id') for item in self._cr.dictfetchall()]
            sale_order_quantity = 0
            for sol in self.env['sale.order.line'].browse(ids):
                sale_order_quantity += sol._compute_real_qty_to_deliver()
                # sol._compute_qty_delivered()
            # quant.available_quantity = quant.quantity - quant.sale_order_quantity
            #     sale_order_quantity += sol.product_uom_qty - sol.qty_delivered
            available_quantity = quant.quantity - sale_order_quantity
            quant.write({'sale_order_quantity': sale_order_quantity, 'available_quantity': available_quantity})

    @api.model
    def _quant_tasks(self):
        res = super(StockQuant, self)._quant_tasks()
        # Solo ejecutar cálculos pesados si hay usuarios con el grupo correspondiente
        if self.env['res.users'].search([('groups_id', 'in', self.env.ref('anavale.group_sale_lot_calculation').id)]):
            date = fields.Datetime.today() - relativedelta(months=2,day=15)
            self._cr.execute("""
                                SELECT id 
                                    FROM stock_quant
                                WHERE create_date > %s and location_id in (8, 9, 25, 26) and quantity > 0
                            """, (date, ))
            ids = [item.get('id') for item in self._cr.dictfetchall()]
            self.sudo().browse(ids)._compute_sale_order_qty()
        return res

    def call_view_sale_order(self):
        """ Method called when click button
            "View Sale Order" from stock.quant
            Tree view.
            Displays Tree view of all sale.order
            composing self.sale_order_quantity """
        # Verificar que el usuario tenga permisos
        if not self.env.user.has_group('anavale.group_sale_lot_calculation'):
            raise ValidationError('No tienes permisos para ver esta información')
            
        self.ensure_one()             
        domain = [('product_id', '=', self.product_id.id),
            ('order_id.state', '=', 'sale'),
            ('lot_id', '=', self.lot_id.id)]
            
        ids =[]
        for sol in self.env['sale.order.line'].search(domain):
            # Only sale.order.line with pending deliveries
            if sol._compute_real_qty_to_deliver() > 0:
                ids.append(sol.order_id.id)

        # raise ValidationError('{}'.format(ids))
                
        return  {
            'type': 'ir.actions.act_window',
            'name': 'Sale Orders Lot %s' % self.lot_id.name,
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', ids)],
            'context': dict(self.env.context),
            'target': 'self',
        }
        #commit

    def _compute_value(self):
        res = super(StockQuant, self)._compute_value()
        for quant in self:
            if quant.value > 0 and quant.product_id.id == 561:
                purchase = quant.lot_id.mapped('purchase_order_ids.id')
                purchase_lines = self.env['purchase.order.line'].search([('order_id','=',purchase)])
                lote_quant = quant.lot_id
                print(lote_quant.name)
                if lote_quant.name == 'FPMP3FM23-001':
                    print("paro aqui")
                movimiento_recepcion = self.env['stock.move.line'].search([('location_id','=',4), ('lot_id','=',lote_quant.id)])
                movimientos = 0
                for mov in movimiento_recepcion:
                    movimientos += mov.qty_done
                cantidad_recibida = movimientos
                for line in purchase_lines:
                    if quant.product_id == line.product_id and cantidad_recibida == line.product_qty:
                        quant.value = quant.quantity * line.price_unit

                
            # If the user didn't enter a location yet while enconding a quant.

                #quant.value = quant.quantity * quant.product_id.standard_price