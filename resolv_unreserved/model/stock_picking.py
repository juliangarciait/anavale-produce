from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        quants = self.env["stock.quant"].search([])
        move_line_ids = []
        warning = ""
        for quant in quants:

            move_lines = self.env["stock.move.line"].search(

                [

                    ("product_id", "=", quant.product_id.id),

                    ("location_id", "=", quant.location_id.id),

                    ("lot_id", "=", quant.lot_id.id),

                    ("package_id", "=", quant.package_id.id),

                    ("owner_id", "=", quant.owner_id.id),

                    ("product_qty", "!=", 0),

                ]

            )

            move_line_ids += move_lines.ids

            reserved_on_move_lines = sum(move_lines.mapped("product_qty"))

            move_line_str = str.join(

                ", ", [str(move_line_id) for move_line_id in move_lines.ids]

            )

            if quant.location_id.should_bypass_reservation():

                # If a quant is in a location that should bypass the reservation, its `reserved_quantity` field

                # should be 0.

                if quant.reserved_quantity != 0:
                    quant.write({"reserved_quantity": 0})

            else:

                # If a quant is in a reservable location, its `reserved_quantity` should be exactly the sum

                # of the `product_qty` of all the partially_available / assigned move lines with the same

                # characteristics.

                if quant.reserved_quantity == 0:

                    if move_lines:
                        move_lines.with_context(bypass_reservation_update=True).write(

                            {"product_uom_qty": 0}

                        )

                elif quant.reserved_quantity < 0:

                    quant.write({"reserved_quantity": 0})

                    if move_lines:
                        move_lines.with_context(bypass_reservation_update=True).write(

                            {"product_uom_qty": 0}

                        )

                else:

                    if reserved_on_move_lines != quant.reserved_quantity:

                        move_lines.with_context(bypass_reservation_update=True).write(

                            {"product_uom_qty": 0}

                        )

                        quant.write({"reserved_quantity": 0})

                    else:

                        if any(move_line.product_qty < 0 for move_line in move_lines):
                            move_lines.with_context(bypass_reservation_update=True).write(

                                {"product_uom_qty": 0}

                            )

                            quant.write({"reserved_quantity": 0})

        move_lines = self.env["stock.move.line"].search(

            [

                ("product_id.type", "=", "product"),

                ("product_qty", "!=", 0),

                ("id", "not in", move_line_ids),

            ]

        )

        move_lines_to_unreserve = []

        for move_line in move_lines:

            if not move_line.location_id.should_bypass_reservation():
                move_lines_to_unreserve.append(move_line.id)

        if len(move_lines_to_unreserve) > 1:

            self.env.cr.execute(

                """ 

                    UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id in %s ;

                """

                % (tuple(move_lines_to_unreserve),)

            )

        elif len(move_lines_to_unreserve) == 1:

            self.env.cr.execute(

                """ 

                UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id = %s ;

                """

                % (move_lines_to_unreserve[0])

            )
        return super().button_validate()

    def do_unreserve(self):
        quants = self.env["stock.quant"].search([])
        move_line_ids = []
        warning = ""
        for quant in quants:

            move_lines = self.env["stock.move.line"].search(

                [

                    ("product_id", "=", quant.product_id.id),

                    ("location_id", "=", quant.location_id.id),

                    ("lot_id", "=", quant.lot_id.id),

                    ("package_id", "=", quant.package_id.id),

                    ("owner_id", "=", quant.owner_id.id),

                    ("product_qty", "!=", 0),

                ]

            )

            move_line_ids += move_lines.ids

            reserved_on_move_lines = sum(move_lines.mapped("product_qty"))

            move_line_str = str.join(

                ", ", [str(move_line_id) for move_line_id in move_lines.ids]

            )

            if quant.location_id.should_bypass_reservation():

                # If a quant is in a location that should bypass the reservation, its `reserved_quantity` field

                # should be 0.

                if quant.reserved_quantity != 0:
                    quant.write({"reserved_quantity": 0})

            else:

                # If a quant is in a reservable location, its `reserved_quantity` should be exactly the sum

                # of the `product_qty` of all the partially_available / assigned move lines with the same

                # characteristics.

                if quant.reserved_quantity == 0:

                    if move_lines:
                        move_lines.with_context(bypass_reservation_update=True).write(

                            {"product_uom_qty": 0}

                        )

                elif quant.reserved_quantity < 0:

                    quant.write({"reserved_quantity": 0})

                    if move_lines:
                        move_lines.with_context(bypass_reservation_update=True).write(

                            {"product_uom_qty": 0}

                        )

                else:

                    if reserved_on_move_lines != quant.reserved_quantity:

                        move_lines.with_context(bypass_reservation_update=True).write(

                            {"product_uom_qty": 0}

                        )

                        quant.write({"reserved_quantity": 0})

                    else:

                        if any(move_line.product_qty < 0 for move_line in move_lines):
                            move_lines.with_context(bypass_reservation_update=True).write(

                                {"product_uom_qty": 0}

                            )

                            quant.write({"reserved_quantity": 0})

        move_lines = self.env["stock.move.line"].search(

            [

                ("product_id.type", "=", "product"),

                ("product_qty", "!=", 0),

                ("id", "not in", move_line_ids),

            ]

        )

        move_lines_to_unreserve = []

        for move_line in move_lines:

            if not move_line.location_id.should_bypass_reservation():
                move_lines_to_unreserve.append(move_line.id)

        if len(move_lines_to_unreserve) > 1:

            self.env.cr.execute(

                """ 

                    UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id in %s ;

                """

                % (tuple(move_lines_to_unreserve),)

            )

        elif len(move_lines_to_unreserve) == 1:

            self.env.cr.execute(

                """ 

                UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id = %s ;

                """

                % (move_lines_to_unreserve[0])

            )
        return super().do_unreserve()
