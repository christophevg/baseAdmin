#!/usr/bin/env python

import sys
import pickle
import pprint

try:
  f = sys.argv[1]
except:
  f = "config.pkl"

with open(f, "rb") as fp:
  pprint.pprint(pickle.load(fp))
