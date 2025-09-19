import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.adapters.asg_adapter import ASGAdapter


@pytest.fixture(autouse=True)
def reset_asg_adapter_state():
    ASGAdapter.clear_token_cache()
    ASGAdapter.configure_token_persistence()
    yield
    ASGAdapter.clear_token_cache()
    ASGAdapter.configure_token_persistence()
