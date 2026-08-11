"""
RetailFlow Mock Supply Chain API Runner.

Usage
-----

    python -m scripts.run_mock_supply_api
"""

from __future__ import annotations

import uvicorn


def main() -> None:
    """
    Start the development Supply Chain REST API.
    """

    uvicorn.run(
        "infrastructure.mock_supply_api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()