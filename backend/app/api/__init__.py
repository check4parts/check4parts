"""API package exports and provider registry."""

from . import asg, bm_parts, intercars, omega, uniqtrade

PROVIDER_REGISTRY = {
    "bm-parts": bm_parts.router,
    "intercars": intercars.router,
    "asg": asg.router,
    "omega": omega.router,
    "uniqtrade": uniqtrade.router,
}

__all__ = ["PROVIDER_REGISTRY"]
