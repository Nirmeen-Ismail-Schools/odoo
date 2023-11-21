from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class ResUser(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.property", # related model
        "salesman", # field for "this" on related model
    )
