from fastapi import APIRouter
from models.estimator import EstimatorRequest
from services.estimator import calculate_estimate
from core.logging import logger
from utils.response import success, error

router = APIRouter()

@router.post("/")
def estimate_cost(data: EstimatorRequest):
    try:
        result = calculate_estimate(
            data.floor_area,
            data.storeys,
            data.finishing,
            data.roof_type,
            data.location
        )
        logger.info(f"Estimate calculated: {data.floor_area}m² {data.finishing} in {data.location}")
        return success(data=result)
    except Exception as e:
        logger.error(f"Estimation failed: {str(e)}")
        return error(message=str(e), status_code=500)