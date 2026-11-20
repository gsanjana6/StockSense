
from fastapi import APIRouter, HTTPException

from app.services.technical_analysis import (
    calculate_technical_analysis,
)

router = APIRouter(tags=["Technical Analysis"])


@router.get("/stocks/{ticker}/technical-analysis")
def get_technical_analysis(ticker: str):
    try:
        return calculate_technical_analysis(ticker)

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except Exception:
        # Log the full exception on the backend during debugging.
        import logging

        logging.exception(
            "Technical analysis failed for ticker %s", ticker
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Technical analysis is temporarily unavailable. "
                "Check the ticker and market-data service."
            ),
        )
