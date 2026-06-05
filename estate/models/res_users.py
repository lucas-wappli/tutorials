from odoo import fields, models

class Users(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.property', 'salesman_id', string='Properties for Sale', domain=[('state', 'not in', ['sold', 'canceled'])])