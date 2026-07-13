from fastapi import APIRouter
from api.v1 import auth, quotes, line_items, estimator, suppliers, analysis, chat, floor_plan, messages, pdf

router = APIRouter() 

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(quotes.router, prefix="/quotes", tags=["Quotes"])
router.include_router(line_items.router, prefix="/line-items", tags=["Line Items"])
router.include_router(estimator.router, prefix="/estimator", tags=["Estimator"])
router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(floor_plan.router, prefix="/floor-plan", tags=["Floor Plan"])
router.include_router(messages.router, prefix="/messages", tags=["Messages"])
router.include_router(pdf.router, prefix="/pdf", tags=["PDF"])

