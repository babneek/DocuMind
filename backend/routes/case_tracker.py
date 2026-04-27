"""
Case Tracker Routes
Live case status and hearing dates from Indian courts
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from .auth import get_current_user
from backend.models.user import User
from backend.services.case_tracker_service import get_case_tracker

router = APIRouter(prefix="/api/cases", tags=["Case Tracker"])


class CNRSearchRequest(BaseModel):
    cnr_number: str  # 16-digit CNR, e.g., DLHC010123456789


class CaseNumberSearchRequest(BaseModel):
    case_type: str        # e.g., "CO", "CS", "W.P.(C)"
    case_number: str      # e.g., "448"
    year: str             # e.g., "2022"
    court: str = "delhi_hc"  # delhi_hc, bombay_hc, supreme_court, etc.


@router.post("/search-cnr")
async def search_by_cnr(
    request: CNRSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search case by CNR number (16-digit alphanumeric)
    Returns full case details including next hearing date
    
    CNR Format: STATECOURTNO + YEAR + SEQUENCE
    Example: DLHC010123456789
    """
    try:
        tracker = get_case_tracker()
        result = tracker.get_case_by_cnr(request.cnr_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search-number")
async def search_by_case_number(
    request: CaseNumberSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search case by case number (for High Courts / Supreme Court)
    
    Example: CO/448/2022 in Delhi High Court
    """
    try:
        tracker = get_case_tracker()
        result = tracker.get_case_by_number(
            case_type=request.case_type,
            case_number=request.case_number,
            year=request.year,
            court=request.court
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/upcoming/{cnr_number}")
async def get_upcoming_hearings(
    cnr_number: str,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """
    Get upcoming hearings for a case
    
    Returns:
    - Today's hearings
    - This week's hearings
    - This month's hearings
    - Full hearing history
    """
    try:
        tracker = get_case_tracker()
        result = tracker.get_upcoming_hearings(cnr_number, days_ahead=days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courts")
async def get_supported_courts(
    current_user: User = Depends(get_current_user)
):
    """Get list of supported courts"""
    return {
        "courts": [
            {"id": "delhi_hc", "name": "Delhi High Court", "url": "https://delhihighcourt.nic.in"},
            {"id": "bombay_hc", "name": "Bombay High Court", "url": "https://bombayhighcourt.nic.in"},
            {"id": "madras_hc", "name": "Madras High Court", "url": "https://hcmadras.tn.nic.in"},
            {"id": "calcutta_hc", "name": "Calcutta High Court", "url": "https://calcuttahighcourt.gov.in"},
            {"id": "karnataka_hc", "name": "Karnataka High Court", "url": "https://karnatakajudiciary.kar.nic.in"},
            {"id": "allahabad_hc", "name": "Allahabad High Court", "url": "https://allahabadhighcourt.in"},
            {"id": "gujarat_hc", "name": "Gujarat High Court", "url": "https://gujarathighcourt.nic.in"},
            {"id": "rajasthan_hc", "name": "Rajasthan High Court", "url": "https://hcraj.nic.in"},
            {"id": "supreme_court", "name": "Supreme Court of India", "url": "https://www.sci.gov.in"},
            {"id": "district_courts", "name": "District Courts (via CNR)", "url": "https://services.ecourts.gov.in"},
        ],
        "note": "For District Courts, use CNR number. For High Courts and Supreme Court, use case number."
    }
