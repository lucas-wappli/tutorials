from odoo import fields, models, api
from datetime import timedelta

class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'

    price = fields.Float(string='Offer Price', required=True)
    status = fields.Selection(
        string='Status', 
        copy=False, 
        selection=[
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
        ]
    )
    validity = fields.Integer(string='Validity (days)', default=7)
    deadline = fields.Date(string='Deadline', compute='_compute_deadline')
    partner_id = fields.Many2one('res.partner', string='Potential Buyer', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)

    @api.depends('validity', 'create_date')
    def _compute_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.deadline = date + timedelta(days=offer.validity)