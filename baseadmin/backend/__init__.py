# import os
# import logging
# import bcrypt
#
# from baseadmin import config, store
#
# # provision initial users collection
#
# def init():
#   provision_users()
#
# def provision_users():
#   store.provision(
#     "users",
#     [
#       {
#         "_id"     : "admin",
#         "name"    : "Admin",
#         "password": bcrypt.hashpw(config["admin"]["pass"], bcrypt.gensalt())
#       },
#       {
#         "_id"     : config["register"]["user"],
#         "name"    : "Client Registration Account",
#         "password": bcrypt.hashpw(config["register"]["pass"], bcrypt.gensalt())
#       },
#     ],
#     force
#   )
