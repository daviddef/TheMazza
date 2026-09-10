#!/usr/bin/env python3
"""The Piedimonte Etneo birth volumes, and where each one's index sits."""
import json, os
PATH = "data/pe-volumes.json"
DEFAULT = {
  "1875": {"ark": "an_ua83488"}, "1876": {"ark": "an_ua83489"},
  "1877": {"ark": "an_ua83490"}, "1878": {"ark": "an_ua83491"},
  "1879": {"ark": "an_ua83492", "container": "LDmQYGl", "images": 81, "read": True},
  "1879s": {"ark": "an_ua83493", "note": "segnatura 8957, suppl. 2"},
  "1880": {"ark": "an_ua83494"}, "1881": {"ark": "an_ua83495"},
  "1882": {"ark": "an_ua83496"}, "1883": {"ark": "an_ua83497"},
  "1884": {"ark": "an_ua83498", "guess": True}, "1885": {"ark": "an_ua83499", "guess": True},
}
if not os.path.exists(PATH):
    json.dump(DEFAULT, open(PATH, "w"), indent=1)
print(json.dumps(json.load(open(PATH)), indent=1))
