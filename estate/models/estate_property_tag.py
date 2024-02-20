from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Model per estate.property.tag"


    name = fields.Char(string='Etiqueta', required=True)
    color = fields.Integer(string='Index de colors')
    # Per afegir mes camps

