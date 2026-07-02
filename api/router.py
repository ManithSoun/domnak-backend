from fastapi import APIRouter
from api.v1 import analysis, auth, quotes, line_items, estimator, pdf, suppliers

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(quotes.router, prefix="/quotes", tags=["Quotes"])
router.include_router(line_items.router, prefix="/line-items", tags=["Line Items"])
router.include_router(estimator.router, prefix="/estimator", tags=["Estimator"])
router.include_router(pdf.router, prefix="/pdf", tags=["PDF"])
router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
# router.include_router(chat.router, prefix="/chat", tags=["Chat"])