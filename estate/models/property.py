from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta

class Property(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'

    _unique_name = models.Constraint(
        'UNIQUE(name)',
        'The name of the property must be unique.'
    )
    _positive_price = models.Constraint(
        'CHECK(expected_price > 0 AND selling_price >= 0)',
        'Expected price must be strictly positive and selling price must be non-negative.'
    )

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description', help='Description of the property')
    postcode = fields.Char(string='Postcode', size=20)
    date_availability = fields.Date(string='Available From', copy=False, default=lambda self: fields.Date.today() + timedelta(days=90))
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False)
    best_offer = fields.Float(string='Best Offer', compute='_compute_best_offer')
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area (m²)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area (m²)')
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ]
    )
    total_area = fields.Integer(string='Total Area (m²)', compute='_compute_total_area')
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection(
        string='Status',
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        default='new'
    )
    type_id = fields.Many2one('estate.property.type', string='Property Type') 
    salesman_id = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer', readonly=True, copy=False)
    tag_ids = fields.Many2many('estate.property.tag', string='Property Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers', copy=False)

    @api.constrains('selling_price', 'expected_price')
    def check_price(self):
        for record in self:
            if record.state not in ['new', 'offer_received'] and record.selling_price < record.expected_price * 0.9:    
                raise ValidationError("The selling price cannot be lower than 90% of the expected price.")

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped('price'), default=0)

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'    
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError('Canceled properties cannot be sold.')
            else:
                record.state = 'sold'
            return True

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Sold properties cannot be canceled.')
            else:
                record.state = 'canceled'
            return True

    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault('name', f"{self.name} (copy)")
        return super().copy(default)