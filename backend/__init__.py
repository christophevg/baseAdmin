import os

APP_NAME = os.environ.get("APP_NAME")
if not APP_NAME:
  APP_NAME = "baseAdmin"

import backend.logging

import backend.data

import backend.web
import backend.rest

import backend.resources
import backend.interface
