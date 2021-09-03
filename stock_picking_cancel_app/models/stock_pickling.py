# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero

class Inventory_picking(models.Model):
	_inherit = "stock.picking"

	def set_to_draft(self) :
		self.write({'state':'draft'})
		for move in self.move_ids_without_package :
			move.write({'state':'draft'})
		return

	def action_cancel(self):
		for picking in self :
			if picking.state == 'done':
				picking.mapped('move_lines').cancel_stock_picking()
				picking.move_lines._do_unreserve()
				for moves in picking.move_lines:
					for line in moves.mapped('move_line_ids'):
						line.result_package_id.unpack()
					moves.mapped('move_line_ids').write({'qty_done': 0.0})
				picking.package_level_ids.filtered(lambda p: not p.move_ids).unlink()
				picking.write({'is_locked': True})
			else:
				picking.mapped('move_lines')._action_cancel()
				picking.write({'is_locked': True})
			account_move = self.env['account.move'].search([('ref','=',picking.name)])
			account_move.button_cancel()
			account_move.sudo().unlink()
		return True


class StockMove(models.Model):
	_inherit = "stock.move"

	def _do_unreserve(self):
		moves_to_unreserve = self.env['stock.move']        
		for move in self:
			if self.user_has_groups('stock_picking_cancel_app.group_cancel_stock_picking'):
				if move.state == 'cancel':
					# We may have cancelled move in an open picking in a "propagate_cancel" scenario.
					continue
				if move.state == 'done':
					if move.scrapped:
						# We may have done move in an open picking in a scrap scenario.
						continue
			else:
				if move.state == 'cancel':
					# We may have cancelled move in an open picking in a "propagate_cancel" scenario.
					continue
				if move.state == 'done':
					if move.scrapped:
						# We may have done move in an open picking in a scrap scenario.
						continue
					else:
						raise UserError(_('You cannot unreserve a stock move that has been set to \'Done\'.'))
			moves_to_unreserve |= move
		moves_to_unreserve.mapped('move_line_ids').unlink()
		return True


	def cancel_stock_picking(self):
		for move in self:
			move._do_unreserve()
			siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
			if move.propagate_cancel:
				# only cancel the next move if all my siblings are also cancelled
				if all(state == 'cancel' for state in siblings_states):
					move.move_dest_ids._action_cancel()
			else:
				if all(state in ('done', 'cancel') for state in siblings_states):
					move.move_dest_ids.write({'procure_method': 'make_to_stock'})
					move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
			if move.quantity_done:
				if move.picking_id.picking_type_id.code in ['outgoing','internal']:
					for move_id in move:
						for line in move_id.move_line_ids:                                  
							if move.location_dest_id.usage == 'customer':
								outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id)])
								stock_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id)])
								if outgoing_quant:
									old_qty = outgoing_quant[0].quantity
									outgoing_quant[0].quantity = old_qty - move.product_uom_qty
									abc = outgoing_quant[0].quantity
								if stock_quant:
									old_qty = stock_quant[0].quantity
									stock_quant[0].quantity = old_qty + move.product_uom_qty
							else:
								if line.product_id.tracking != 'lot':
									outgoing_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id)])
									if outgoing_customer_quant:
										old_qty = outgoing_customer_quant[0].quantity
										outgoing_customer_quant[0].quantity = old_qty - move.product_uom_qty
									outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id)])
									if outgoing_quant:
										old_qty = outgoing_quant[0].quantity									
										outgoing_quant[0].quantity = old_qty + move.product_uom_qty
									else:
										vals = { 'product_id' :move.product_id.id,
												 'location_id':move.location_id.id,
												 'quantity': move.product_uom_qty,
											   }
										test = self.env['stock.quant'].sudo().create(vals)
								else:
									outgoing_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id),('lot_id','=',line.lot_id.id)])
									if outgoing_customer_quant:
										old_qty = outgoing_customer_quant[0].quantity
										outgoing_customer_quant[0].quantity = old_qty - move.product_uom_qty
									outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id),('lot_id','=',line.lot_id.id)])
									if outgoing_quant:
										old_qty = outgoing_quant[0].quantity									
										outgoing_quant[0].quantity = old_qty + move.product_uom_qty
									else:
										vals = { 'product_id' :move.product_id.id,
												 'location_id':move.location_id.id,
												 'quantity': move.product_uom_qty,
												 'lot_id':line.lot_id.id,
											   }
										test = self.env['stock.quant'].sudo().create(vals)									
										
				if move.picking_id.picking_type_id.code == 'incoming':
					for move_id in move:
						for line in move_id.move_line_ids:
							if line.lot_id:
								if line.product_id.tracking == 'lot':
									incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id),('lot_id','=',line.lot_id.id)])
									incoming_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id),('lot_id','=',line.lot_id.id)])
									if incoming_quant:
										old_qty = incoming_quant[0].quantity
										incoming_quant[0].quantity = old_qty - move.product_uom_qty
									if incoming_customer_quant:
										old_qty = incoming_customer_quant[0].quantity
										incoming_customer_quant[0].quantity = old_qty + move.product_uom_qty
								else:
									incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id),('lot_id','=',line.lot_id.id)])
									for lot in incoming_quant:
										old_qty = lot.quantity
										lot.unlink()
										vals = { 'product_id' :move.product_id.id,
												 'location_id':move.location_dest_id.id,
												 'quantity': old_qty,
												 'lot_id':line.lot_id.id,
											   }
										test = self.env['stock.quant'].sudo().create(vals)
							else:
								incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id)])
								if incoming_quant:
									old_qty = incoming_quant[0].quantity
									incoming_quant[0].quantity = old_qty - move.product_uom_qty
								incoming_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id)])
								if incoming_customer_quant:
									old_qty = incoming_customer_quant[0].quantity
									incoming_customer_quant[0].quantity = old_qty + move.product_uom_qty

			account_move = self.env['account.move'].sudo().search([('stock_move_id','=',move.id)],order="id desc", limit=1)
			if account_move : 
				account_move.button_cancel()
			self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
		return True

class stock_quant(models.Model):
	_inherit = 'stock.quant'

	@api.model
	def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False):
		""" Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
		sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
		the *exact same characteristics* otherwise. Typically, this method is called when reserving
		a move or updating a reserved move line. When reserving a chained move, the strict flag
		should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
		anything from the stock, so we disable the flag. When editing a move line, we naturally
		enable the flag, to reflect the reservation according to the edition.

		:return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
			was done and how much the system was able to reserve on it
		"""
		self = self.sudo()
		rounding = product_id.uom_id.rounding
		quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
		reserved_quants = []

		if float_compare(quantity, 0, precision_rounding=rounding) > 0:
			# if we want to reserve
			available_quantity = self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
			if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
				raise UserError(_('It is not possible to reserve more products of %s than you have in stock.') % product_id.display_name)
		elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
			# if we want to unreserve
			available_quantity = sum(quants.mapped('reserved_quantity'))
			if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
				raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.') % product_id.display_name)
		else:
			return reserved_quants

		for quant in quants:
			if float_compare(quantity, 0, precision_rounding=rounding) > 0:
				max_quantity_on_quant = quant.quantity - quant.reserved_quantity
				if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
					continue
				max_quantity_on_quant = min(max_quantity_on_quant, quantity)
				quant.reserved_quantity += max_quantity_on_quant
				reserved_quants.append((quant, max_quantity_on_quant))
				quantity -= max_quantity_on_quant
				available_quantity -= max_quantity_on_quant
			else:
				max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
				quant.reserved_quantity -= max_quantity_on_quant
				reserved_quants.append((quant, -max_quantity_on_quant))
				quantity += max_quantity_on_quant
				available_quantity += max_quantity_on_quant

			if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity, precision_rounding=rounding):
				break
		return reserved_quants

class stock_move_line(models.Model):
	_inherit = "stock.move.line"
	
	def unlink(self):
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		for ml in self:
			if self.user_has_groups('stock_picking_cancel_app.group_cancel_stock_picking') == False and ml.state =='done':
				if ml.state in ('done', 'cancel'):
					raise UserError(_('You can not delete product moves if the picking is done. You can only correct the done quantities.'))
				# Unlinking a move line should unreserve.
				if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(ml.product_qty, precision_digits=precision):
					try:
						self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
					except UserError:
						if ml.lot_id:
							self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
						else:
							raise
			elif self.user_has_groups('stock_picking_cancel_app.group_cancel_stock_picking') == True and ml.state =='done':
				if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(ml.product_qty, precision_digits=precision):
					try:
						self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
					except UserError:
						if ml.lot_id:
							self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
						else:
							raise
		moves = self.mapped('move_id')
		for move in moves:
			if self.user_has_groups('stock_picking_cancel_app.group_cancel_stock_picking') == False and move.state != 'done':
				res = super(stock_move_line, self).unlink()
			else:
				res = True
			if self.user_has_groups('stock_picking_cancel_app.group_cancel_stock_picking') == True and move.state != 'done':
				res = super(stock_move_line, self).unlink()
			if moves:
				moves._recompute_state()
			return res


class QuantPackage(models.Model):
	""" Packages containing quants and/or other packages """
	_inherit = "stock.quant.package"

	def unpack(self):
		for package in self:
			move_line_to_modify = self.env['stock.move.line'].search([
				'|',('package_id', '=', package.id),
				('result_package_id', '=', package.id),
				('state', 'in', ('assigned', 'partially_available', 'done','cancel')),
				'|',('product_qty', '!=', 0),
				('product_qty', '=', 0),
			])
			move_line_to_modify.write({'result_package_id': False, 'package_id': False})
			package.mapped('quant_ids').sudo().write({'package_id': False})

		# Quant clean-up, mostly to avoid multiple quants of the same product. For example, unpack
		# 2 packages of 50, then reserve 100 => a quant of -50 is created at transfer validation.
		self.env['stock.quant']._merge_quants()
		self.env['stock.quant']._unlink_zero_quants()