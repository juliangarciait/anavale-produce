# -*- coding: utf-8 -*-

{
    'name' : "Validación para la confirmación de Sale Orders",
    'summary' : """
    Módulo que agrega una validación al momento de confirmar las sale orders, si el partner tiene facturas vencidas y no tiene permitido el over credit, no deja confirmar la orden
    """, 
    'author' : "Quemari developers",
    'website' : "http://www.quemari.com", 
    'category' : "Sales",
    'depends' : [
        'sale', 
        'sale_management', 
        'account',
        'account_accountant',
    ], 
    'data' : [],
}