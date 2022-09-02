# -*- coding: utf-8 -*-

from odoo import http, fields, models, api, _ 
from datetime import date, datetime

import logging

_logger = logging.getLogger(__name__)


class Portal(http.Controller): 

    @http.route('/anavale/checkin', auth='public', website=True)
    def index(self, **kw): 
        return http.request.render('check_in_checkout.check_in_form')

    @http.route('/anavale/checkin/validation', type='http', methods=['POST'], auth='public', website=True, csrf=False)
    def check_in_validation(self, **kw): 
        if not {'pick_up', 'drivers_name', 'drivers_licence', 'drivers_phone', 'destination', 'carrier_name', 'trailer_plates', 'truck_plates'} <= kw.keys(): 
            _logger.info('There are some fields missing')
            return http.request.render('check_in_checkout.check_in_failed')
        else: 
            picking_id = http.request.env['stock.picking'].sudo().search([('origin', '=', kw.get('pick_up'))])
            
            if picking_id: 
                kw.update({'date' : datetime.now(), 'check_in_time': datetime.now(), 'doc_type' : 'check_in'})
                checkin_id = http.request.env['check.in.checkout'].create(kw)
                picking_id.state = 'assigned'
                picking_id.custom_state_delivery = 'assigned'

                if checkin_id and 'assigned' in (picking_id.state, picking_id.custom_state_delivery): 
                    _logger.info('The check-in has been completed successfully')
                    return http.request.render('check_in_checkout.check_in_successful')
                else: 
                    _logger.info('Something failed when creating the check-in')
                    return http.request.render('check_in_checkout.check_in_failed')

            else: 
                _logger.info('There are no transfers with that source document')
                return http.request.render('check_in_checkout.check_in_picking_not_found')
