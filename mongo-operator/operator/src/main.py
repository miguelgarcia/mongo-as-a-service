"""
Operator main entry point.
"""
import kopf
import logging
# Import all handlers so they get registered
import handlers

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Or INFO, WARNING, etc.
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

# Register all handlers from handlers.py

if __name__ == "__main__":
    # Run the Kopf operator loop
    kopf.run(clusterwide=True, standalone=True)