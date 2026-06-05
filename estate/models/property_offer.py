from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import timedelta

class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = "price desc"

    _positive_price = models.Constraint(
        'CHECK(price > 0)',
        'Offer price must be strictly positive.'
    )

    price = fields.Float(string='Price', required=True)
    status = fields.Selection(
        string='Status', 
        copy=False, 
        selection=[
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
        ]
    )
    validity = fields.Integer(string='Validity (days)', default=7)
    deadline = fields.Date(string='Deadline', compute='_compute_deadline', inverse='_inverse_deadline', store=True)
    partner_id = fields.Many2one('res.partner', string='Potential Buyer', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    property_type_id = fields.Many2one(related='property_id.type_id', string='Property Type', store=True)

    @api.depends('validity', 'create_date')
    def _compute_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.deadline = date + timedelta(days=offer.validity)

    def _inverse_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.deadline - date).days

    def accept_offer(self):
        for offer in self:
            if offer.property_id.state in ['sold', 'canceled']:
                raise UserError("You cannot accept an offer for a property that is already sold or canceled.")
            elif offer.property_id.state == 'offer_accepted':
                raise UserError("You cannot accept an offer for a property that already has an accepted offer.")
            else:
                offer.status = 'accepted'
                offer.property_id.state = 'offer_accepted'
                offer.property_id.selling_price = offer.price
                offer.property_id.buyer_id = offer.partner_id
            return True

    def refuse_offer(self):
        for offer in self:
            if offer.property_id.state in ['sold', 'canceled']:
                raise UserError("You cannot refuse an offer for a property that is already sold or canceled.")
            elif offer.property_id.state == 'offer_accepted' and offer.status == 'accepted':
                offer.property_id.state = 'offer_received'
                offer.property_id.selling_price = 0
                offer.property_id.buyer_id = False
                offer.status = 'refused'
            else:
                offer.status = 'refused'
        return True

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            prop = self.env['estate.property'].browse(vals['property_id'])
            if prop.best_offer and vals['price'] <= prop.best_offer:
                raise UserError("The offer price must be higher than the current best offer of %s." % prop.best_offer)
            if prop.state == 'new':
                prop.state = 'offer_received'
        return super().create(vals_list)
