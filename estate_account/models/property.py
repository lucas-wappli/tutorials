from odoo import models

class Property(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        print("inherited method called")
        for record in self:
            if record.state not in ['canceled']:
                invoice_vals_list = []
                for offer in record.offer_ids:
                    invoice_vals = {
                        'partner_id': offer.partner_id.id,
                        'move_type': 'out_invoice',
                        'journal_id': self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id,
                    }
                    invoice_vals_list.append(invoice_vals)
                    
                moves = self.env['account.move'].create(invoice_vals_list)

        return super().action_sold()