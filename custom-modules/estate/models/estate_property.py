# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, exceptions, tools
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real state app"
    _order = "id desc"
    active = fields.Boolean(default=True)
    title = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    available_from = fields.Date(copy=False, default=fields.Date.today(3) + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    property_type_id = fields.Many2one("estate.property.type", string="Type")
    # set default value = current user
    salesman = fields.Many2one("res.users", default=lambda self: self.env.user)
    buyer = fields.Many2one("res.partner", string="Buyer", copy=False)
    tags = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Integer(compute="_compute_total_area")
    best_offer = fields.Float(compute="_compute_best_offer")
    state = fields.Selection(
        string=False,
        selection=[("new", "New"), ("offer_recieved", "Offer Received"), ("offer_accepted", "Offer Accepted"), ("sold", "Sold"), ("canceled", "Canceled")],
        default="new",
        copy=False,
        required=True
    )
    garden_orientation = fields.Selection(
        string="Direction",
        selection=[("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        help="Garden orientation",
    )

    # make onchange function that sets state = offer_recieved when offer_ids is not empty and offer state = new
    @api.onchange("offer_ids")
    def _onchange_offer_ids(self):
        print ("onchange offer_ids")
        for rec in self:
            if rec.offer_ids and rec.offer_ids[0].status == False:
                rec.state = "offer_recieved"
            else:
                rec.state = "new"

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    def _compute_best_offer(self):
        for rec in self:
            rec.best_offer = self.offer_ids.sorted(key=lambda r: r.price, reverse=True)[0].price if self.offer_ids else 0

    @api.onchange("garden")
    # make a method that sets garden area value to 10 and orientation to north when garden is checked
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"

    def action_sold(self):
        for rec in self:
            if rec.state == "canceled" or rec.state == "sold":
                print ("Property is already sold or canceled")
                raise exceptions.ValidationError("Property is already sold or canceled")
                return False
            rec.state = "sold"
            rec.selling_price = rec.best_offer
            rec.buyer = rec.offer_ids.sorted(key=lambda r: r.price, reverse=True)[0].partner_id.id
            return True

    def action_cancel(self):
        for rec in self:
            rec.state = "canceled"
            rec.selling_price = 0
            rec.buyer = False
        return True

    # use sql constraints to let expected price must be strictly positive
    _sql_constraints = [
        ('expected_price_positive', 'CHECK(expected_price > 0)', 'Expected price must be strictly positive'),
        # selling price must be positive
        ('selling_price_positive', 'CHECK(selling_price >= 0)', 'Selling price must be positive')
    ]

    # use python constraints to let selling price can't be lower than 90% of the expected price
    @api.constrains("selling_price")
    @api.constrains("expected_price")
    def _check_selling_price(self):
        for rec in self:
            if rec.state != "offer_accepted" and rec.state != "sold":
                continue
            # use float_utils.float_compare() from to compare float numbers
            if tools.float_utils.float_compare(rec.selling_price, rec.expected_price * 0.9, precision_digits=2) < 0:
                raise exceptions.ValidationError("Selling price can't be lower than 90% of the expected price")