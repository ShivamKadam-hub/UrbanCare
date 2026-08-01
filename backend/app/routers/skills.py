"""
Skills & Expertise API Router
Endpoints for skill-based provider matching and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.models.models import (
    ProviderSkill, Skill, SkillReview, ServiceProvider, User, Booking, BookingStatus
)
from app.schemas.schemas import (
    SkillCreate, SkillOut, ProviderSkillCreate, ProviderSkillOut,
    ProviderSkillDetail, SkillReviewCreate, SkillReviewOut
)
from app.utils.auth import get_current_user, require_role
from app.utils.skills import (
    calculate_percentile_rank, update_skill_metrics, get_skill_expertise_label,
    match_providers_by_skills, get_provider_expertise_summary, get_skill_trends
)

router = APIRouter(prefix="/api/skills", tags=["Skills & Expertise"])


# ────────────────────────────────────────────────────────────────────────────
# SKILLS MANAGEMENT (Admin only)
# ────────────────────────────────────────────────────────────────────────────

@router.post("", response_model=SkillOut, status_code=201)
def create_skill(
    payload: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Create a new skill (admin only)"""
    # Check if skill already exists
    existing = db.query(Skill).filter(Skill.name.ilike(payload.name)).first()
    if existing:
        raise HTTPException(400, f"Skill '{payload.name}' already exists")

    skill = Skill(**payload.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("", response_model=list[SkillOut])
def list_skills(
    category_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all available skills"""
    q = db.query(Skill)
    
    if category_id:
        q = q.filter(Skill.category_id == category_id)
    
    return q.order_by(Skill.name).offset(skip).limit(limit).all()


@router.get("/{skill_id}", response_model=SkillOut)
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """Get skill details"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(404, "Skill not found")
    return skill


# ────────────────────────────────────────────────────────────────────────────
# PROVIDER SKILLS MANAGEMENT
# ────────────────────────────────────────────────────────────────────────────

@router.post("/provider/add", response_model=ProviderSkillOut, status_code=201)
def add_provider_skill(
    payload: ProviderSkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("provider")),
):
    """Provider adds a skill they're experienced in"""
    # Get provider profile
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.user_id == current_user.id
    ).first()

    if not provider:
        raise HTTPException(404, "Provider profile not found")

    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if not skill:
        raise HTTPException(404, "Skill not found")

    # Check if already added
    existing = db.query(ProviderSkill).filter(
        ProviderSkill.provider_id == provider.id,
        ProviderSkill.skill_id == payload.skill_id
    ).first()

    if existing:
        raise HTTPException(400, "This skill is already in your profile")

    provider_skill = ProviderSkill(
        provider_id=provider.id,
        skill_id=payload.skill_id,
        skill_level=payload.skill_level
    )
    db.add(provider_skill)
    db.commit()
    db.refresh(provider_skill)
    return provider_skill


@router.get("/provider/my-skills", response_model=list[ProviderSkillDetail])
def get_my_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("provider")),
):
    """Get current provider's skills"""
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.user_id == current_user.id
    ).first()

    if not provider:
        raise HTTPException(404, "Provider profile not found")

    return db.query(ProviderSkill).filter(
        ProviderSkill.provider_id == provider.id
    ).order_by(ProviderSkill.percentile_rank.desc()).all()


@router.get("/provider/{provider_id}", response_model=list[ProviderSkillDetail])
def get_provider_skills(
    provider_id: int,
    db: Session = Depends(get_db),
):
    """Get a provider's skills"""
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.id == provider_id
    ).first()

    if not provider:
        raise HTTPException(404, "Provider not found")

    return db.query(ProviderSkill).filter(
        ProviderSkill.provider_id == provider.id
    ).order_by(ProviderSkill.percentile_rank.desc()).all()


@router.delete("/provider/remove/{skill_id}")
def remove_provider_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("provider")),
):
    """Provider removes a skill from their profile"""
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.user_id == current_user.id
    ).first()

    if not provider:
        raise HTTPException(404, "Provider profile not found")

    provider_skill = db.query(ProviderSkill).filter(
        ProviderSkill.provider_id == provider.id,
        ProviderSkill.skill_id == skill_id
    ).first()

    if not provider_skill:
        raise HTTPException(404, "Skill not found in profile")

    db.delete(provider_skill)
    db.commit()
    return {"message": "Skill removed"}


# ────────────────────────────────────────────────────────────────────────────
# SKILL REVIEWS
# ────────────────────────────────────────────────────────────────────────────

@router.post("/reviews", response_model=SkillReviewOut, status_code=201)
def create_skill_review(
    payload: SkillReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer")),
):
    """Customer rates a provider's specific skill after booking"""
    # Verify booking exists and is completed and belongs to customer
    booking = db.query(Booking).filter(
        Booking.id == payload.booking_id,
        Booking.customer_id == current_user.id,
        Booking.status == BookingStatus.COMPLETED
    ).first()

    if not booking:
        raise HTTPException(404, "Completed booking not found")

    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if not skill:
        raise HTTPException(404, "Skill not found")

    # Check if already reviewed this skill for this booking
    existing = db.query(SkillReview).filter(
        SkillReview.booking_id == payload.booking_id,
        SkillReview.skill_id == payload.skill_id
    ).first()

    if existing:
        raise HTTPException(400, "This skill has already been reviewed for this booking")

    # Create review
    review = SkillReview(
        booking_id=payload.booking_id,
        provider_id=booking.service.provider_id,
        skill_id=payload.skill_id,
        rating=payload.rating,
        comment=payload.comment,
        would_rebook=payload.would_rebook
    )
    db.add(review)
    db.commit()

    # Update skill metrics
    update_skill_metrics(booking.service.provider_id, payload.skill_id, db)

    db.refresh(review)
    return review


@router.get("/reviews/provider/{provider_id}", response_model=list[SkillReviewOut])
def get_provider_skill_reviews(
    provider_id: int,
    skill_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get reviews for a provider's skills"""
    q = db.query(SkillReview).filter(SkillReview.provider_id == provider_id)

    if skill_id:
        q = q.filter(SkillReview.skill_id == skill_id)

    return q.order_by(SkillReview.created_at.desc()).offset(skip).limit(limit).all()


# ────────────────────────────────────────────────────────────────────────────
# SMART MATCHING & EXPERTISE
# ────────────────────────────────────────────────────────────────────────────

@router.post("/match", response_model=list[dict])
def match_providers(
    skills: list[int] = Query(...),
    limit: int = Query(10, ge=1, le=20),
    min_rating: float = Query(3.0, ge=1.0, le=5.0),
    db: Session = Depends(get_db),
):
    """
    Find best providers for specific skills
    Returns ranked list by expertise level
    """
    if not skills:
        raise HTTPException(400, "At least one skill ID is required")

    matches = match_providers_by_skills(skills, db, limit=limit, min_rating=min_rating)

    # Enrich with provider details
    result = []
    for match in matches:
        provider = db.query(ServiceProvider).filter(
            ServiceProvider.id == match["provider_id"]
        ).first()

        if provider and provider.user:
            result.append({
                "provider_id": match["provider_id"],
                "provider_name": provider.business_name,
                "match_score": round(match["match_score"], 2),
                "expertise_labels": [
                    get_skill_expertise_label(
                        db.query(ProviderSkill).filter(
                            ProviderSkill.provider_id == match["provider_id"],
                            ProviderSkill.skill_id == s["skill_id"]
                        ).first()
                    )
                    for s in match["skills"]
                ],
                "skills": match["skills"]
            })

    return result


@router.get("/expertise/{provider_id}", response_model=dict)
def get_expertise_summary(
    provider_id: int,
    db: Session = Depends(get_db),
):
    """Get comprehensive expertise summary for a provider"""
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.id == provider_id
    ).first()

    if not provider:
        raise HTTPException(404, "Provider not found")

    return get_provider_expertise_summary(provider_id, db)


@router.get("/trends/{skill_id}", response_model=dict)
def get_skill_trends_endpoint(
    skill_id: int,
    days: int = Query(30, ge=1, le=360),
    db: Session = Depends(get_db),
):
    """Get trends and statistics for a specific skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(404, "Skill not found")

    return get_skill_trends(skill_id, db, days=days)


@router.get("/analytics/top-skills")
def get_top_skills(
    limit: int = Query(20, ge=1, le=50),
    period_days: int = Query(30, ge=1, le=180),
    db: Session = Depends(get_db),
):
    """Admin endpoint: Get most demanded and highest-rated skills"""
    from sqlalchemy import func
    from datetime import datetime, timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    # Get skills with highest demand and ratings
    top_skills = db.query(
        Skill.id,
        Skill.name,
        func.count(SkillReview.id).label("review_count"),
        func.avg(SkillReview.rating).label("avg_rating"),
        func.sum(SkillReview.would_rebook).label("rebook_count")
    ).join(
        SkillReview, Skill.id == SkillReview.skill_id
    ).filter(
        SkillReview.created_at >= cutoff_date
    ).group_by(
        Skill.id, Skill.name
    ).order_by(
        func.count(SkillReview.id).desc()
    ).limit(limit).all()

    result = []
    for skill in top_skills:
        review_count = skill[2] or 0
        rebook_count = skill[4] or 0
        rebook_rate = (rebook_count / review_count * 100) if review_count > 0 else 0
        
        result.append({
            "skill_id": skill[0],
            "skill_name": skill[1],
            "review_count": review_count,
            "average_rating": round(float(skill[3]) if skill[3] else 0, 2),
            "rebook_rate": round(rebook_rate, 1)
        })
    
    return result


@router.patch("/admin/verify/{provider_skill_id}")
def verify_provider_skill(
    provider_skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Admin verifies a provider's skill expertise"""
    provider_skill = db.query(ProviderSkill).filter(
        ProviderSkill.id == provider_skill_id
    ).first()

    if not provider_skill:
        raise HTTPException(404, "Provider skill not found")

    provider_skill.verified = True
    db.commit()
    db.refresh(provider_skill)

    return {"message": "Skill verified", "verified": provider_skill.verified}
