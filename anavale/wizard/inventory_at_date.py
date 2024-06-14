from odoo import models, fields, api

class ReportWizard(models.TransientModel):
    _name = 'inventoryatdate.report.wizard'
    _description = 'Asistente para Generar Reporte de Inventario a la fecha'

    report_date = fields.Date(string='Fecha de Inventario', required=True)

    def generate_report(self):
        # Obtener la fecha seleccionada
        fecha = self.report_date

        # Aquí debes agregar la lógica para generar el reporte basado en la fecha
        self.env['inventoryatdate.report'].generate_report(fecha)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inventoryatdate.report',
            'view_mode': 'pivot,tree',
            'target': 'current',
            'name': ('Reporte de inventario a: ') + fecha.strftime("%Y-%m-%d"),
        }