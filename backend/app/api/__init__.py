"""API package exports and provider registry."""

from . import asg, bm_parts, intercars, omega, search, uniqtrade

PROVIDER_REGISTRY = {
    "bm-parts": bm_parts.router,
    "intercars": intercars.router,
    "asg": asg.router,
    "omega": omega.router,
    "uniqtrade": uniqtrade.router,
    "search": search.router,
}

__all__ = ["PROVIDER_REGISTRY"]
