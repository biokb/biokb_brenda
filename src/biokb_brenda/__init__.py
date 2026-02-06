from importlib.metadata import PackageNotFoundError, version
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try:
    __version__ = version("biokb_brenda")
except PackageNotFoundError:
    # Package is not installed (e.g., during local development)
    __version__ = "unknown"
