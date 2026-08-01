# ⚡ Skill-Based Matching - Quick Setup Guide

## Installation (5 minutes)

### Step 1: Backend Models Already Added ✓
The models, schemas, and API endpoints are ready:
- `ProviderSkill` - Links providers to skills
- `Skill` - Master skill list
- `SkillReview` - Skill-specific reviews
- `SkillLevel` enum - Expertise levels

### Step 2: Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```

Tables will auto-create on startup.

### Step 3: Seed Initial Skills

**Option A: Via Database**
```bash
psql -U urbancare -d urbancare << EOF
INSERT INTO skills (name, category_id, icon, description) VALUES
('AC gas refill', 1, '❄️', 'Refrigerant refilling'),
('Bathroom cleaning', 1, '🛁', 'Deep cleaning bathrooms'),
('Plumbing repair', 1, '🔧', 'Fixing leaks and pipes'),
('Electrical installation', 1, '⚡', 'Safe electrical work'),
('Wall painting', 1, '🎨', 'Interior & exterior painting'),
('Kitchen cleaning', 1, '🍽️', 'Professional kitchen cleaning'),
('Carpet cleaning', 1, '🧹', 'Carpet & rug cleaning'),
('Glass installation', 1, '🪟', 'Windows and mirrors');
EOF
```

**Option B: Via API**
```bash
# Login as admin first
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@urbancare.com","password":"admin123"}' \
  | jq -r '.access_token')

# Create skill
curl -X POST http://localhost:8000/api/skills \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AC gas refill",
    "category_id": 1,
    "icon": "❄️",
    "description": "Refrigerant refilling for air conditioning units"
  }'
```

### Step 4: Integrate Frontend Component
In your main app or dashboard:

```jsx
import SkillBasedMatching from './components/SkillBasedMatching';
import './styles/SkillBasedMatching.css';

// Add to your routing
<Routes>
  <Route path="/smart-match" element={<SkillBasedMatching />} />
  {/* Or show in dashboard */}
  <Route path="/dashboard" element={
    <>
      {/* existing content */}
      <SkillBasedMatching />
    </>
  } />
</Routes>
```

### Step 5: Test the Feature

**As Provider:**
```bash
# Add a skill
curl -X POST http://localhost:8000/api/skills/provider/add \
  -H "Authorization: Bearer $PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_id": 1,
    "skill_level": "expert"
  }'

# View my skills
curl -X GET http://localhost:8000/api/skills/provider/my-skills \
  -H "Authorization: Bearer $PROVIDER_TOKEN"
```

**As Customer:**
```bash
# Find providers by skills
curl -X GET "http://localhost:8000/api/skills/match?skills=1,3&limit=10" \
  -H "Authorization: Bearer $CUSTOMER_TOKEN"

# After booking completion - rate skill
curl -X POST http://localhost:8000/api/skills/reviews \
  -H "Authorization: Bearer $CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 42,
    "skill_id": 1,
    "rating": 5,
    "comment": "Excellent AC refill!",
    "would_rebook": true
  }'
```

**As Admin:**
```bash
# View top skills
curl -X GET "http://localhost:8000/api/skills/analytics/top-skills?days=30" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Verify a provider's skill
curl -X PATCH http://localhost:8000/api/skills/admin/verify/{provider_skill_id} \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 📊 Workflow Example

### Complete End-to-End Flow

```
1. ADMIN: Create Skills
   POST /api/skills
   ├── "AC gas refill"
   ├── "Bathroom cleaning"
   └── "Plumbing repair"

2. PROVIDER: Add Expertise
   POST /api/skills/provider/add
   ├── Provider 1 adds "AC gas refill" (expert)
   ├── Provider 2 adds "AC gas refill" (intermediate)
   └── Provider 3 adds "Bathroom cleaning" (expert)
   
3. BOOKINGS COMPLETED
   ├── Customer books Provider 1 for AC refill
   └── Booking completed successfully

4. CUSTOMER: Rate Skill
   POST /api/skills/reviews
   ├── Rating: 5/5
   ├── Skill: "AC gas refill"
   └── System updates Provider 1's metrics

5. PERCENTILE CALCULATED
   ├── Provider 1 has: 4.8⭐, 50+ jobs
   ├── Percentile: 95th percentile
   └── Label: "🏆 Top 5% in AC gas refill"

6. CUSTOMER: Smart Match
   GET /api/skills/match?skills=1
   ├── Finds all AC experts
   ├── Ranks by: rating × jobs × verification
   └── Returns Provider 1 #1 (87/100 score)

7. CUSTOMER: Books Expert
   ├── Sees "🏆 Top 5% in AC gas refill"
   ├── Confident choice
   └── Books with Provider 1!
```

---

## 🎯 How Percentile Ranking Works

### For "AC gas refill" across all providers:

```
Providers sorted by expertise score:
1. Provider A: 4.8⭐ × 127 jobs = 609.6 pts  → 95th percentile → "🏆 Top 5%"
2. Provider B: 4.6⭐ × 89 jobs = 409.4 pts   → 85th percentile → "⭐ Top 15%"
3. Provider C: 4.9⭐ × 45 jobs = 220.5 pts   → 60th percentile → "✨ Highly skilled"
```

**Formula:**
```
score = avg_rating × (1 + completed_jobs/100)
        × (1.2 if verified else 1.0)
```

---

## 📱 Frontend Component Features

### Skill-Based Matching Page
```
┌─────────────────────────────────┐
│  🎯 Smart Provider Matching     │
│  Find experts by specific skills │
├─────────────────────────────────┤
│                                 │
│  Step 1: Select Skill           │
│  [ ❄️ AC Repair ] [ 🛁 Cleaning ]   │
│  [ 🔧 Plumbing ] [ ⚡ Electrical ] │
│                                 │
│  [Find Matching Providers]      │
├─────────────────────────────────┤
│                                 │
│  Step 2: Choose Expert          │
│                                 │
│  ┌──────────────────────────┐   │
│  │ #1 AC Experts Ltd        │   │
│  │ 🏆 Top 5% AC Refill      │   │
│  │ ⭐ Top 10% AC Repair     │   │
│  │         [87/100]         │   │
│  │ ▶ Show Details           │   │
│  │    ├─ 4.8⭐ (127 jobs)   │   │
│  │    ├─ 95th percentile    │   │
│  │    ├─ ✓ Verified Expert  │   │
│  │    [Request] [Book Now]  │   │
│  └──────────────────────────┘   │
│                                 │
│  ┌──────────────────────────┐   │
│  │ #2 Pro Services          │   │
│  │ ✨ Highly skilled        │   │
│  │          [76/100]        │   │
│  └──────────────────────────┘   │
└─────────────────────────────────┘
```

---

## 🗂️ Files Reference

### Backend
- **Models**: `backend/app/models/models.py`
  - `Skill`, `ProviderSkill`, `SkillReview`
- **API**: `backend/app/routers/skills.py`
  - 15+ endpoints
- **Utils**: `backend/app/utils/skills.py`
  - Matching & percentile calculation
- **Schemas**: `backend/app/schemas/schemas.py`
  - `SkillOut`, `ProviderSkillOut`, etc.

### Frontend
- **Component**: `frontend/src/components/SkillBasedMatching.jsx`
- **Styles**: `frontend/src/styles/SkillBasedMatching.css`

### Documentation
- **Full Docs**: `SKILL_BASED_MATCHING.md`
- **This Guide**: `SKILL_BASED_MATCHING_SETUP.md`

---

## 🧪 Testing

### Manual Testing Checklist

```
Admin Tasks:
☐ Create 5+ skills via API
☐ Verify skills appear in list
☐ Create test provider account

Provider Tasks:
☐ Add 2-3 skills to profile
☐ Verify skills appear in /my-skills
☐ Remove a skill successfully

Customer Tasks:
☐ View available skills
☐ Select multiple skills
☐ See matched providers
☐ View expertise labels (🏆 Top 5%, etc.)
☐ Complete booking
☐ Submit skill review (1-5 rating)
☐ Verify metrics updated
☐ Check percentile rank updated

Admin Verification:
☐ Verify a provider's skill
☐ See verification badge update
☐ View analytics/top-skills
☐ Check skill trends
```

---

## 🚀 Performance Tips

### Database Indexes
```sql
-- Add these for better performance
CREATE INDEX idx_provider_skill_percentile 
  ON provider_skills(percentile_rank DESC, provider_id);

CREATE INDEX idx_skill_reviews_skill_id
  ON skill_reviews(skill_id, created_at DESC);

CREATE INDEX idx_provider_skills_provider_id
  ON provider_skills(provider_id);
```

### Caching Strategy
```python
# Cache percentile rankings (recalc daily at 2 AM)
@scheduler.add_job(update_all_percentiles, 'cron', hour=2)

# Cache provider expertise summaries (1 hour TTL)
@cache(expire=3600)
def get_provider_expertise_summary(provider_id):
    ...
```

---

## 🐛 Troubleshooting

### Issue: No providers showing in match results
**Solution:**
1. Verify skills created: `GET /api/skills`
2. Verify provider added skills: `GET /api/skills/provider/{id}`
3. Verify provider has ratings: Check skill_reviews table
4. Check min_rating filter not too high

### Issue: Percentile ranks all 50%
**Solution:** 
- Percentiles need skill reviews to calculate
- Ensure customers are rating skills after bookings
- Run `calculate_percentile_rank()` manually to recalc

### Issue: Expertise labels not showing
**Solution:**
- Ensure ProviderSkill has avg_rating > 0
- Check percentile_rank calculated correctly
- Verify get_skill_expertise_label() called

---

## 📚 Integration with Existing Features

### With Service Detail Page
```jsx
// Show provider's expertise
<ProviderCard provider={provider} />
// Now displays:
// - All skills with badges
// - Percentile rankings
// - Top expertise labels
```

### With Search/Filter
```jsx
// Add skill filter
<SkillFilter onChange={(skills) => {
  // Search providers matching skills
  matchProviders(skills);
}}/>
```

### With Booking
```jsx
// Show provider expertise during booking
<BookingConfirmation provider={provider} />
// Displays:
// - Expertise for this service
// - Reviews for this specific skill
// - "Recommended: Top 5%"
```

---

## 🎓 Next Steps

1. ✅ **Install** - Follow steps 1-5 above
2. ✅ **Test** - Run manual testing checklist
3. ✅ **Seed** - Create skills and provider profiles
4. ✅ **Deploy** - Push to production
5. ✅ **Monitor** - Watch analytics dashboard
6. 🔄 **Iterate** - Add more skills, improve matching

---

## 📖 For More Details

- **Full Documentation**: [SKILL_BASED_MATCHING.md](SKILL_BASED_MATCHING.md)
- **API Docs**: Navigate to http://localhost:8000/docs
- **Code**: Check `backend/app/routers/skills.py`
- **Tests**: See test files in `backend/`

---

**That's it! Your customers now book with confidence based on specific expertise, not generic ratings! 🚀**

Need help? Check the FAQ in [SKILL_BASED_MATCHING.md](SKILL_BASED_MATCHING.md)
