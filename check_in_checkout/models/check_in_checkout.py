# -*- coding: utf-8 -*-

from odoo import models, api, fields, _ 


class CheckInCheckout(models.Model): 
    _name = 'check.in.checkout'

    date = fields.Datetime(string="Date")

    pick_up = fields.Char(string="Pick Up")

    drivers_name = fields.Char(string="Driver's name")

    drivers_licence = fields.Char(string="Driver's licence")

    drivers_phone = fields.Char(string="Driver's phone")

    destination = fields.Char(string="Destination")
    
    carrier_name = fields.Char(string="Carrier name")

    trailer_plates = fields.Char(string="Trailer plates")

    truck_plates = fields.Char(string="Truck plates")

    check_in_time = fields.Datetime(string="Check in Time")

    doc_type = fields.Selection([('check_in', 'Check In'), ('checkout', 'Checkout')], string="Type")