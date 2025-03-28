from odoo import fields, models, api
from odoo import tools
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


Precios = [
    ('fijo', 'Precio Fijo'),
    ('variable', 'Precio Variable'),
]

porcentajes = [
    ('8', '8% comision'),
    ('9', '9% comision'),
    ('10', '10% comision'),
    ('11', '11% comision'),
    ('12', '12% comision'),

]

SiNo = [
    ('si','SI'),
    ('no','NO'),
]

Flete_opciones = [
    ('si','Se paga y se descuenta'),
    ('no','Se paga, NO se descuenta'),
    ('nono','No se paga')
]

InOut_opciones = [
    ('si','SI se descuenta'),
    ('no','NO se descuenta'),
]

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tipo_precio = fields.Selection(Precios, string="Tipo de Precio")

    porcentaje_comision = fields.Selection(porcentajes, string="% de Comision")

    Flete_entrada = fields.Selection(Flete_opciones, string='Flete de entrada?')

    Aduana_MX = fields.Selection(Flete_opciones, string='Aduana MX?')

    Aduana_US = fields.Selection(Flete_opciones, string='Aduana US?')

    In_out = fields.Selection(InOut_opciones, string='In and Out?')

    caja = fields.Selection(InOut_opciones, string='caja?')

    Desc_fijo = fields.Text(string="Descuentos Fijos(especificar)")
    
    referencia = fields.Text('Referencia')

    purchase_analytics = fields.Float('Purchase Contab')
    
    @api.onchange('partner_id')
    def onchange_partner(self): 
        for record in self: 
            record.tipo_precio = record.partner_id.price_type
            record.porcentaje_comision = record.partner_id.commission_percentage
            record.Flete_entrada = record.partner_id.freight_in
            record.Aduana_MX = record.partner_id.mx_customs
            record.Aduana_US = record.partner_id.us_customs
            record.In_out = record.partner_id.in_and_out
            record.caja = record.partner_id.box
            record.referencia = record.partner_id.reference

    lot = fields.Text(compute="_get_lot")

    @api.depends('order_line')
    def _get_lot(self):
        for order in self:
            order.lot = ''
            try:
                #purchase = self.env['purchase.order'].search([('invoice_ids', 'in', [order.id])])  
                picking = self.env['stock.picking'].search([('purchase_id', '=', order.id), ('state', '=', 'done')], order='create_date desc', limit=1)
                move = self.env['stock.move.line'].search([('picking_id', '=', picking.id)], limit=1)
                reference = move.lot_id.name
                if reference and picking.date_done: 
                    reference = reference.split('-')
                    if len(reference) > 1: 
                        year = picking.date_done.strftime('%y')
                        ref = reference[1]

                        order.lot = "{}{}-{}".format(order.partner_id.lot_code_prefix, year, ref[:4]) 
            except:
                order.lot = ''

    def _update_stock_valuation_layer(self, move, product_id, price_unit):
        for layer in move.stock_valuation_layer_ids:
            if layer.product_id == product_id:
                layer.sudo().write({
                    'remaining_value': layer.remaining_qty * price_unit,
                    'value': layer.quantity * price_unit,
                    'unit_cost': price_unit
                })

    def payments_reconcile(self, move):
        pay_term_line_ids = move.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        domain = [('account_id', 'in', pay_term_line_ids.mapped('account_id').ids),
                  '|', ('move_id.state', '=', 'posted'), '&', ('move_id.state', '=', 'draft'),
                  ('journal_id.post_at', '=', 'bank_rec'),
                  ('partner_id', '=', move.commercial_partner_id.id),
                  ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                  ('amount_residual_currency', '!=', 0.0)]
        if move.is_inbound():
            domain.extend([('credit', '>', 0), ('debit', '=', 0)])
        else:
            domain.extend([('credit', '=', 0), ('debit', '>', 0)])
        lines = self.env['account.move.line'].search(domain)
        if len(lines) != 0:
            return lines

    def _update_work_flow_invoice(self, move):
        if move.state == 'posted':
            payment_state = move.invoice_payment_state
            move.button_draft()
            move.action_post()
            if payment_state in ('paid', 'in_payment'):
                # Refund Payment
                if move.invoice_has_outstanding:
                    lines = self.payments_reconcile(move)
                    for line in lines:
                        lines = self.env['account.move.line'].browse(line.id)
                        lines += move.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()

    @staticmethod
    def _get_list_lot_ids(lot_id):
        _logger.info(lot_id.name)
        result = [lot_id.id]
        for child_lot in lot_id.child_lot_ids:
            result.append(child_lot.id)
        return result
    
    @staticmethod
    def _get_list_variant_ids(template_id):
        result = []
        result = template_id.product_variant_ids.ids
            
        return result

    def _update_account_move_from_sale(self, move_sale, product_id, price_unit):

        domain = [('lot_id', 'in', tuple(self._get_list_lot_ids(move_sale.lot_id))),
                  ('product_id', 'in', self._get_list_variant_ids(product_id.product_tmpl_id))]
        lines = self.env['sale.order.line'].search(domain)
        _logger.info("$"*900)
        _logger.info(domain)
        _logger.info(lines.read())
        
        for line in lines:
            # Update Purchase Move
            for move in line.move_ids:
                _logger.info("Move Update SALE")
                self._update_account_move(move, product_id, price_unit)
                self.update_invoice_valuation(move, product_id, price_unit, move_sale.lot_id)
                self._update_stock_valuation_layer(move, product_id, price_unit)
            # Update Invoice Lines
            # for ivl in line.invoice_lines:
            #     if ivl.move_id:
            #         self._update_work_flow_invoice(ivl.move_id)

    def update_invoice_valuation(self, move, product_id, price_unit, lot_id):
        _logger.info("&"*900)
        product_ids = self._get_list_variant_ids(product_id.product_tmpl_id)
        order_id = move.sale_line_id and move.sale_line_id.order_id
        accounts = product_id.product_tmpl_id.get_product_accounts()
        _logger.info(accounts)
        domain = [("product_id", "=", product_id.id), ("account_id", "in", [accounts.get("expense").id, accounts.get("stock_output").id])]
        if order_id:
            domain.append(("move_id.invoice_origin", "=", order_id.name))
        move_ids = self.env["account.move.line"].search(domain)
        tag = lot_id.analytic_tag_ids.ids
        if len(tag) == 0:
            raise ValidationError('lote {} no tiene tags'.format(str(lot_id.name)))
        tag.sort()
        tag = tag[-1]
        
        for x in range(len(move_ids)):
            if move_ids[x].account_id.id == 24:
                if tag in move_ids[x].analytic_tag_ids.ids:
                    sql_str = ""
                    total = price_unit * move_ids[x].quantity
                    for acc in move_ids[x-1:x+1]:
                        if acc.credit != 0:
                            sql_str = "UPDATE account_move_line set credit=%f,balance=%f,price_subtotal=%f,price_total=%f,price_unit=%f where id=%s" % (
                            price_unit * abs(acc.quantity), abs(total) * -1, total, total, price_unit, acc.id)
                        else:
                            sql_str = "UPDATE account_move_line set debit=%f, balance=%f,price_subtotal=%f,price_total=%f,price_unit=%f where id=%s" % (
                            price_unit * abs(acc.quantity), abs(total), total, total, price_unit, acc.id)
                        if sql_str:
                            _logger.info(sql_str)
                            self.env.cr.execute(sql_str)


        # for line in move_ids:
        #     sql_str = ""
        #     total = price_unit * line.quantity
        #     if line.credit != 0:
        #         sql_str = "UPDATE account_move_line set credit=%f,balance=%f,price_subtotal=%f,price_total=%f,price_unit=%f where id=%s" % (
        #             price_unit * abs(line.quantity), abs(total) * -1, total, total, price_unit, line.id)
        #     else:
        #         sql_str = "UPDATE account_move_line set debit=%f, balance=%f,price_subtotal=%f,price_total=%f,price_unit=%f where id=%s" % (
        #             price_unit * abs(line.quantity), abs(total), total, total, price_unit, line.id)
        #     if sql_str:
        #         _logger.info(sql_str)
        #         self.env.cr.execute(sql_str)



    def _update_account_move(self, stock_move, product_id, price_unit):
        product_ids = self._get_list_variant_ids(product_id.product_tmpl_id)
        lot_ids = self.env["stock.production.lot"].browse(self._get_list_lot_ids(stock_move.lot_id))
        tag_ids = self.env["account.analytic.tag"]
        for lot in lot_ids:
            tag_ids += lot.analytic_tag_ids
        sol_id = stock_move.sale_line_id

        for rec in self.env['account.move'].search([('stock_move_id', '=', stock_move.id)]):
            if rec.state == 'posted':
                rec.button_draft()
                prepare_ids = []  # (1, ID, { values })
                line_ids = rec.line_ids
                if sol_id:
                    _logger.info("_"*900)
                    _logger.info(tag_ids)
                    for line in rec.line_ids:
                        _logger.info("%"*900)
                        _logger.info(line.analytic_tag_ids)
                    line_ids = rec.invoice_line_ids.filtered(lambda line: line.analytic_tag_ids in tag_ids)                    
                for line_ac in line_ids:
                    if line_ac.product_id.id in product_ids:
                        if line_ac.credit != 0:
                            prepare_ids.append((1, line_ac.id, {'credit': price_unit * abs(line_ac.quantity)}))
                        else:
                            prepare_ids.append((1, line_ac.id, {'debit': price_unit * abs(line_ac.quantity)}))
                if prepare_ids:
                    rec.sudo().invoice_line_ids = prepare_ids
                rec.action_post()
        print("termina _update_account_move")
    
    def _update_stock_valuation_by_lot(self, move, product_id, price_unit):
        for line in move.move_line_ids:
            lot = line.lot_id
            if lot:
                lot_ids = [lot.id] + self.env['stock.production.lot'].search([('parent_lod_id', '=', lot.id)]).ids
                mline_ids = self.env['stock.move.line'].search([('lot_id', 'in', lot_ids)])                
                for mline in mline_ids:
                    for accmove in mline.move_id.account_move_ids:
                        if accmove.state == 'posted':
                            accmove.button_draft()
                    # if len(mline.move_id.account_move_ids.line_ids.filtered('reconciled')) == 0:
                            for aline in accmove.line_ids:
                                if aline.credit != 0:
                                    aline.sudo().with_context({'check_move_validity': False}).write({'credit': price_unit * abs(aline.quantity)})
                                else:
                                    aline.sudo().with_context({'check_move_validity': False}).write({'debit': price_unit * abs(aline.quantity)})
                            print(accmove)
                            print(line)
                            accmove.action_post()
        print("termina update_stock_valuation_by_lot") 
                    #mline.move_id.account_move_ids.action_post()

    def action_update_valuation(self):
        _logger.info('update valuation')
        for record in self:
            for line in record.order_line:
                if line.product_id and line.price_total:
                    # Update Purchase Move
                    line._compute_total_invoiced()
                    for move in line.move_ids.filtered(lambda move: move.state == "done"):
                        self._update_account_move(move, line.product_id, line.price_unit)
                        self._update_stock_valuation_by_lot(move, line.product_id, line.price_unit)
                        self._update_stock_valuation_layer(move, line.product_id, line.price_unit)
                        for move_sale in move.move_line_nosuggest_ids:
                            
                            if move_sale.lot_id:
                                self._update_account_move_from_sale(move_sale, line.product_id, line.price_unit)
            record.calc_purchase_analytics()
        print("termina uaction_update_valuation") 

    @api.model
    def create(self, vals):
        purchaseperson = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))], limit=1).purchaseperson_id.id
        if purchaseperson:
            vals['user_id'] = purchaseperson
        return super(PurchaseOrder, self).create(vals)

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if 'order_line' in vals:
            order_lines = vals.get('order_line')
            for line in order_lines:
                for record in line:
                    if type(record).__name__ == 'dict':
                        if 'price_unit' in record.keys():
                            self.action_update_valuation()
                            break

        return res

    def update_total_invoiced(self): 
        active_ids = self.env.context.get('active_ids', [])
        purchases = self.search([('id', 'in', active_ids)])
        for purchase in purchases: 
            for line_purchase in purchase.order_line: 
                line_purchase._compute_total_invoiced()

    def update_purchase_lot(self):
        active_ids = self.env.context.get('active_ids', [])
        purchases = self.search([('id', 'in', active_ids)])
        for purchase in purchases:
            for line in purchase.order_line:
                purchase_lot1 = line.move_ids.move_line_ids.lot_id
                line.write({'purchase_lot': purchase_lot1.id})

                #purchase_lot1 = line.move_id.purchase_line_id
                #purchase_lot1.write({'purchase_lot': lot.id})

    def calc_purchase_analytics(self):
        active_ids = self.env.context.get('active_ids', [])
        purchases = self.search([('id', 'in', active_ids)])
        for purchase_rec in purchases: 
            po_product_ids = [line.product_id for line in purchase_rec.order_line]
            fecha = purchase_rec.date_order
            picking_ids = purchase_rec.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
            lot_ids = self.env["stock.production.lot"]
            for sml in picking_ids.move_line_ids:
                lot_ids += sml.lot_id
            analytic_tag_ids = self.env['account.analytic.tag']
            for lot in lot_ids:
                tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
                if not tag in analytic_tag_ids:
                    analytic_tag_ids += tag
            move_line_ids= self.env['account.move.line']
            tag_name = ''
            move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
            for tag_id in analytic_tag_ids:
                tag_name += tag_id.name + ' '
            tag_name = tag_name.split("-")
            if len(tag_name) < 2:
                tag_name.append("")
            purcha = move_line_ids.filtered(lambda line: line.account_id.id == 24 and line.move_id.state == 'posted')
            spoilage = move_line_ids.filtered(lambda line: line.account_id.id == 1396 and line.move_id.state == 'posted')
            inventory_variation = move_line_ids.filtered(lambda line: line.account_id.id == 1398 and line.move_id.state == 'posted')
            purcha_Sum = sum([line.balance for line in purcha])
            spoilage_Sum = sum([line.balance for line in spoilage])
            inventory_variation_Sum = sum([line.balance for line in inventory_variation])
            suma = purcha_Sum + spoilage_Sum + inventory_variation_Sum
            purchase_rec.write({'purchase_analytics': abs(suma)})
            purchase_rec.purchase_analytics = abs(suma)




class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    total_invoiced = fields.Float(compute='_compute_total_invoiced', string="Billed Total", store=True)
    purchase_lot = fields.Many2one('stock.production.lot', 'Lote')
    pallets = fields.Integer(string='Pallets', help="Número de pallets asociados a esta línea de pedido.")

    @api.constrains('pallets')
    def _check_pallets_positive(self):
        for record in self:
            if record.pallets <= 0:
                raise ValidationError("El número de pallets debe ser mayor que cero.")

    @api.model
    def create(self, vals):
        if vals['price_unit'] == 0:
            raise ValidationError('el precio no puede ser 0')
        return super(PurchaseOrderLine, self).create(vals)


    @api.depends('invoice_lines.price_unit', 'invoice_lines.quantity')
    def _compute_total_invoiced(self):
        for line in self:
            total = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.move_id.state not in ['cancel']:
                    if inv_line.move_id.type == 'in_invoice':
                        total += inv_line.price_total
                    elif inv_line.move_id.type == 'in_refund':
                        total -= inv_line.price_total
            line.total_invoiced = total


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    total_invoiced = fields.Float('Total Billed', readonly=False, )

    purchase_lot = fields.Many2one('stock.production.lot', 'Lote', readonly=True)

    pallets = fields.Integer(string='Pallets', readonly=True)


    def _select(self):
        return super(PurchaseReport, self)._select() + ", sum(l.pallets) as pallets ,sum(l.total_invoiced) as total_invoiced, l.purchase_lot as purchase_lot"

    def _group_by(self):
        return super(PurchaseReport,self)._group_by() + ", l.pallets , l.purchase_lot"
