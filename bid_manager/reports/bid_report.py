# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Please note that these reports are not multi-currency !!!
#

from odoo import api, fields, models, tools


class BidReport(models.Model):
    _name = "bid.report"
    _description = "Bid Report"
    _auto = False
    #_order = 'date_order desc, price_total desc'

    bm_id = fields.Many2one('bid.manager', 'Cotizacion', readonly=True, group_operator="count")
    partner_id = fields.Many2one('res.partner', 'Proveedor', readonly=True)
    create_date = fields.Datetime('Date', readonly=True, help="Date on which this document has been created")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to approve', 'To Approve'),
        ('approved', 'Approved'),
        ('done', 'Compra'),
        ('cancel', 'Cancelled')
    ], 'Status', readonly=True)
    price_type = fields.Selection([
        ('open', 'Abierto'),
        ('closed', 'Cerrado')
    ], 'Tipo de Precio', readonly=True)
    commission = fields.Float('Commission', readonly=True)
    product_id = fields.Many2one('product.product', 'Product Variante', readonly=True)
    product_tmp_id = fields.Many2one('product.template', 'Producto', readonly=True)
    price_unit = fields.Float('costo unit', readonly=True, group_operator="avg")
    pallets = fields.Integer('Pallets', readonly=True, group_operator="sum")
    quantity = fields.Float('Cantidad', readonly=True, group_operator="sum")
    precio_venta_estimate = fields.Float('Precio est. venta', readonly=True)
    purchase_order = fields.Many2one('purchase.order', 'Order', readonly=True)
    total = fields.Float('Total venta est.', readonly=True, group_operator="sum")
    nbr_lines = fields.Integer('# of Lines', readonly=True)
    user_id = fields.Many2one('res.users', 'Usuario', readonly=True)

    
    

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

    def _select(self):
        select_str = """
                select MIN(bm.id) * 1000 + ROW_NUMBER() OVER() AS id,bm.id as bm_id, bm.partner_id, bm.create_date, bm.state, bm.price_type, bm.commission, p.id as product_id, p.product_tmpl_id as product_tmp_id, 
	            bml.price_unit, bml.pallets, bml.quantity, bml.price_sale_estimate as precio_venta_estimate, po.id as purchase_order,
	            sum(bml.price_sale_estimate::double precision * COALESCE(bml.quantity, 1.0::double precision))::numeric(16,2) AS total,
	            ru.id as user_id,
                count(*) AS nbr_lines	
            """
        return select_str

    def _from(self):
        from_str = """
            bid_manager_line as bml
	        JOIN bid_manager as bm on bml.bid_manager_id = bm.id
            left JOIN res_partner partner ON bm.partner_id = partner.id
            left join res_users ru on bm.create_uid = ru.id
            LEFT JOIN product_product p ON bml.product_variant_id = p.id
            LEFT JOIN product_template t ON p.product_tmpl_id = t.id
	        LEFT JOIN purchase_order po on bm.purchase_order = po.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
            bm.id, bm.partner_id, bml.price_unit, bm.create_date, p.product_tmpl_id, bm.state, bml.pallets,
	 		p.id, bml.quantity, bml.price_sale_estimate, bm.price_type, bm.commission, po.id, ru.id
        """
        return group_by_str
