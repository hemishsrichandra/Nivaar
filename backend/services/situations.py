"""Canonical localized guidance shared with the existing browser checklist."""
import json
from backend.config import ROOT
ACTIONS=json.loads((ROOT/"data/situation_guidance.json").read_text(encoding="utf-8"))
