from odoo import fields, models

class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'

    _unique_name = models.Constraint(
        'UNIQUE(name)',
        'The name of the tag must be unique.'
    )

    name = fields.Char(string='Tag', required=True)
    color = fields.Integer(string='Color')