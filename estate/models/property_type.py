from odoo import fields, models

class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Type'
    _order = "name asc"

    name = fields.Char(string='Type', required=True)
    property_ids = fields.One2many('estate.property', 'type_id', string='Properties')