from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real state property offer"
    _order = "id desc"

    price = fields.Float()
    status = fields.Selection(
        string="Status",
        selection=[("accepted", "Accepted"), ("refused", "Refused")],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate.property", string="Property")
    validity = fields.Integer(default=7, help="Offer validity in days")
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_validity", store=True)
    property_type_id = fields.Many2one(
        "estate.property.type", related="property_id.property_type_id", string="Type", store=True
    )

    @api.depends("validity")
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = (date.today() if not rec.create_date else rec.create_date.date()) + relativedelta(days=rec.validity)

    def _inverse_validity(self):
        for rec in self:
            if rec.date_deadline:
                rec.validity = (rec.date_deadline - (date.today() if not rec.create_date else rec.create_date.date())).days
    
    def action_accept_offer(self):
        for rec in self:
            rec.property_id.write({"state": "offer_accepted", "selling_price": rec.price, "buyer": rec.partner_id.id})
            rec.status = "accepted"

    def action_refuse_offer(self):
        for rec in self:
            rec.status = "refused"

    # offer price must be strictly positive
    _sql_constraints = [
        ('price_positive', 'CHECK(price > 0)', "Offer price must be strictly positive!"),
    ]