from odoo import models, fields, api

class AshtarCity(models.Model):
    _name = "ashtar.city"
    _description = "City"
    _order = "id desc"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    lead_ids = fields.One2many("ashtar.lead", "city", string="Leads")
    manager_id = fields.Many2one("res.users", string="Manager",
                            domain=lambda self: [("groups_id", "in",
                                                  self.env.ref("ashtar-sales.ashtar_group_city_manager").id)])

    # on change name, update manager
    @api.onchange("name")
    def onchange_name(self):
        print(self.env.ref("base.group_erp_manager"))