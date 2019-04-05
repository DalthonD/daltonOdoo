# -*- coding: utf-8 -*-
from odoo import http

# class Reportesv(http.Controller):
#     @http.route('/reportesv/reportesv/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reportesv/reportesv/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reportesv.listing', {
#             'root': '/reportesv/reportesv',
#             'objects': http.request.env['reportesv.reportesv'].search([]),
#         })

#     @http.route('/reportesv/reportesv/objects/<model("reportesv.reportesv"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reportesv.object', {
#             'object': obj
#         })