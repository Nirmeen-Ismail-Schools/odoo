from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class ResUser(models.Model):
    _inherit = "res.users"

    city = fields.one2Many(
        "ashtar.city",
        "manager_id",
    )

    # add sql constaints to make sure that the user in group ashtar_group_city_manager
    _sql_constraints = [
        ("city_uniq", "unique(city)", "Each city can have only one manager")
    ]
