from odoo import fields, models

class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Type'
    _order = "name asc"

    name = fields.Char(string='Type', required=True)
    property_ids = fields.One2many('estate.property', 'type_id', string='Properties')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    offer_count = fields.Integer(string='Offer Count', compute='_compute_offer_count')

    def _compute_offer_count(self):
        for property_type in self:
            property_type.offer_count = len(property_type.offer_ids)

    def action_view_offers(self):
        self.ensure_one()

        return {
            'name': 'Offers',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.property.offer',
            'view_mode': 'list',
            'context': {'property_type_view': True},
            'domain': [('property_type_id', '=', self.id)],
        }