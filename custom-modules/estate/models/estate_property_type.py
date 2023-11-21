from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real state property type"
    _order = "id desc"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id", string="Offers")
    offer_count = fields.Integer(compute="_compute_offer_count", string="Offers Count")
    # add property_ids to be one2Many field
    property_ids = fields.One2many(
        "estate.property", # related model
        "property_type_id", # field for "this" on related model
    )
    # name must be unique
    _sql_constraints = [
        ('name_unique', 'unique(name)', "Property type name already exists!"),
    ]

    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)