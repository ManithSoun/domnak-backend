import logging
import sys
from datetime import datetime

def setup_logging():
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s |  %(name)s | %(message)s",
    handlers=[
      logging.StreamHandler(sys.stdout),
      logging.FileHandler(f"logs/app.log")
    ]
  )
  return logging.getLogger("domnak")

logger = setup_logging()