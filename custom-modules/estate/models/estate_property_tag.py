from odoo import models, fields
from random import randint

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real state property tag"
    _order = "id desc"

    def _default_color(self):
        return randint(1, 11)
        
    name = fields.Char(required=True, translate=True)
    color = fields.Integer(
        default=lambda self: self._default_color())
    # name must be unique
    _sql_constraints = [
        ('name_unique', 'unique(name)', "Property tag name already exists!"),
    ]