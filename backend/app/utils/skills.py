"""
Skill-based matching and ranking utility
Enables smart provider matching based on specific expertise
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import ProviderSkill, SkillReview, Skill
from datetime import datetime, timedelta


def calculate_percentile_rank(provider_id: int, skill_id: int, db: Session) -> int:
    """
    Calculate what percentile this provider's expertise is in compared to all providers
    with the same skill.
    
    Returns: 0-100 (100 = top 1%, 50 = average, 0 = bottom)
    """
    try:
        # Get this provider's skill metrics
        provider_skill = db.query(ProviderSkill).filter(
            ProviderSkill.provider_id == provider_id,
            ProviderSkill.skill_id == skill_id
        ).first()

        if not provider_skill:
            return 50  # Default to average if no data

        # Get all providers' ratings for this skill
        all_skill_ratings = db.query(
            ProviderSkill.avg_rating,
            ProviderSkill.completed_jobs,
            ProviderSkill.verified
        ).filter(
            ProviderSkill.skill_id == skill_id,
            ProviderSkill.avg_rating > 0  # Only those with ratings
        ).all()

        if not all_skill_ratings:
            return 50

        # Sort by combined score (rating * completions + verification bonus)
        def calculate_score(rating, jobs, verified):
            score = rating * (1 + jobs / 100)  # Higher jobs = higher weight
            if verified:
                score *= 1.2  # 20% bonus for verified skills
            return score

        scores = [
            calculate_score(rating, jobs, verified)
            for rating, jobs, verified in all_skill_ratings
        ]

        provider_score = calculate_score(
            provider_skill.avg_rating,
            provider_skill.completed_jobs,
            provider_skill.verified
        )

        # Calculate percentile
        better_count = sum(1 for s in scores if s > provider_score)
        percentile = 100 - int((better_count / len(scores)) * 100) if scores else 50

        return max(1, min(100, percentile))
    except Exception as e:
        print(f"Error calculating percentile: {e}")
        return 50


def update_skill_metrics(provider_id: int, skill_id: int, db: Session):
    """
    Update skill metrics for a provider based on reviews
    Called after a new skill review is created
    """
    try:
        # Get all reviews for this provider-skill combination
        reviews = db.query(SkillReview).filter(
            SkillReview.provider_id == provider_id,
            SkillReview.skill_id == skill_id
        ).all()

        if not reviews:
            return

        # Calculate metrics
        total_rating = sum(r.rating for r in reviews)
        avg_rating = total_rating / len(reviews)

        # Update provider skill
        provider_skill = db.query(ProviderSkill).filter(
            ProviderSkill.provider_id == provider_id,
            ProviderSkill.skill_id == skill_id
        ).first()

        if provider_skill:
            provider_skill.avg_rating = round(avg_rating, 2)
            provider_skill.completed_jobs = len(reviews)
            
            # Update percentile
            percentile = calculate_percentile_rank(provider_id, skill_id, db)
            provider_skill.percentile_rank = percentile
            provider_skill.last_updated = datetime.utcnow()
            
            db.commit()
    except Exception as e:
        print(f"Error updating skill metrics: {e}")


def get_skill_expertise_label(provider_skill: ProviderSkill) -> str:
    """
    Generate a human-readable expertise label
    E.g., "Expert in AC gas refill", "Top 5% in bathroom cleaning"
    """
    skill_name = provider_skill.skill.name if provider_skill.skill else "Unknown"
    
    if provider_skill.percentile_rank >= 95:
        return f"🏆 Top 5% in {skill_name}"
    elif provider_skill.percentile_rank >= 90:
        return f"Top 10% in {skill_name}"
    elif provider_skill.percentile_rank >= 75:
        return f"Highly skilled in {skill_name}"
    elif provider_skill.skill_level == "master":
        return f"Master craftsman in {skill_name}"
    elif provider_skill.skill_level == "expert":
        return f"Expert in {skill_name}"
    elif provider_skill.skill_level == "intermediate":
        return f"Experienced in {skill_name}"
    else:
        return f"Proficient in {skill_name}"


def match_providers_by_skills(
    required_skills: list[int],
    db: Session,
    limit: int = 10,
    min_rating: float = 3.0
) -> list[dict]:
    """
    Find best providers for a specific set of skills
    
    Args:
        required_skills: List of skill IDs needed
        db: Database session
        limit: Max number of providers to return
        min_rating: Minimum average rating required
    
    Returns: List of (provider_id, match_score, expertise_labels)
    """
    try:
        # Find providers with all required skills
        from sqlalchemy import and_

        matches = []

        # Query providers that have all the required skills
        for skill_id in required_skills:
            skilled_providers = db.query(
                ProviderSkill.provider_id,
                ProviderSkill.avg_rating,
                ProviderSkill.percentile_rank,
                ProviderSkill.completed_jobs,
                ProviderSkill.verified
            ).filter(
                ProviderSkill.skill_id == skill_id,
                ProviderSkill.avg_rating >= min_rating
            ).all()

            for provider_id, rating, percentile, jobs, verified in skilled_providers:
                # Calculate match score
                base_score = rating * 20  # Convert 1-5 to 20-100
                percentile_bonus = (percentile - 50) / 50 * 10  # -10 to +10 bonus
                verified_bonus = 5 if verified else 0
                jobs_bonus = min(jobs / 100 * 5, 5)  # Max 5 bonus for jobs

                match_score = base_score + percentile_bonus + verified_bonus + jobs_bonus
                match_score = min(100, max(0, match_score))

                matches.append({
                    "provider_id": provider_id,
                    "score": match_score,
                    "skill_id": skill_id,
                    "rating": rating,
                    "percentile": percentile,
                    "verified": verified
                })

        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)

        # Group by provider and return top providers
        provider_scores = {}
        for match in matches:
            pid = match["provider_id"]
            if pid not in provider_scores:
                provider_scores[pid] = {"total_score": 0, "skills": [], "count": 0}

            provider_scores[pid]["total_score"] += match["score"]
            provider_scores[pid]["skills"].append(match)
            provider_scores[pid]["count"] += 1

        # Calculate average score per provider
        ranked_providers = [
            {
                "provider_id": pid,
                "match_score": scores["total_score"] / scores["count"],
                "skills": scores["skills"]
            }
            for pid, scores in provider_scores.items()
        ]

        ranked_providers.sort(key=lambda x: x["match_score"], reverse=True)

        return ranked_providers[:limit]

    except Exception as e:
        print(f"Error matching providers: {e}")
        return []


def get_provider_expertise_summary(provider_id: int, db: Session) -> dict:
    """
    Get a comprehensive summary of a provider's expertise
    """
    try:
        provider_skills = db.query(ProviderSkill).filter(
            ProviderSkill.provider_id == provider_id
        ).all()

        if not provider_skills:
            return {
                "total_skills": 0,
                "top_skills": [],
                "expertise_labels": [],
                "verified_skills": 0,
                "average_rating": 0,
                "total_jobs": 0
            }

        # Sort by percentile rank
        top_skills = sorted(
            provider_skills,
            key=lambda x: x.percentile_rank,
            reverse=True
        )[:5]

        expertise_labels = [get_skill_expertise_label(skill) for skill in top_skills]
        verified_count = sum(1 for s in provider_skills if s.verified)
        avg_rating = sum(s.avg_rating for s in provider_skills) / len(provider_skills) if provider_skills else 0
        total_jobs = sum(s.completed_jobs for s in provider_skills)

        return {
            "total_skills": len(provider_skills),
            "top_skills": [
                {
                    "skill_name": s.skill.name,
                    "level": s.skill_level,
                    "rating": s.avg_rating,
                    "percentile": s.percentile_rank,
                    "completed_jobs": s.completed_jobs,
                    "verified": s.verified
                }
                for s in top_skills
            ],
            "expertise_labels": expertise_labels,
            "verified_skills": verified_count,
            "average_rating": round(avg_rating, 2),
            "total_jobs": total_jobs
        }
    except Exception as e:
        print(f"Error getting expertise summary: {e}")
        return {}


def get_skill_trends(skill_id: int, db: Session, days: int = 30) -> dict:
    """
    Get trends for a specific skill (top providers, ratings, etc.)
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get recent reviews for this skill
        recent_reviews = db.query(SkillReview).filter(
            SkillReview.skill_id == skill_id,
            SkillReview.created_at >= cutoff_date
        ).all()

        if not recent_reviews:
            return {
                "skill_id": skill_id,
                "recent_reviews": 0,
                "average_rating": 0,
                "rebook_rate": 0
            }

        avg_rating = sum(r.rating for r in recent_reviews) / len(recent_reviews)
        rebook_count = sum(1 for r in recent_reviews if r.would_rebook)
        rebook_rate = (rebook_count / len(recent_reviews) * 100) if recent_reviews else 0

        # Get top providers for this skill
        top_providers = db.query(
            ProviderSkill
        ).filter(
            ProviderSkill.skill_id == skill_id
        ).order_by(
            ProviderSkill.percentile_rank.desc()
        ).limit(5).all()

        return {
            "skill_id": skill_id,
            "recent_reviews": len(recent_reviews),
            "average_rating": round(avg_rating, 2),
            "rebook_rate": round(rebook_rate, 1),
            "top_providers": [
                {
                    "provider_id": ps.provider_id,
                    "rating": ps.avg_rating,
                    "percentile": ps.percentile_rank,
                    "verified": ps.verified
                }
                for ps in top_providers
            ]
        }
    except Exception as e:
        print(f"Error getting skill trends: {e}")
        return {}
