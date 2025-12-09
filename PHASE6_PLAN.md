# Phase 6: Challenge Management System - Implementation Plan

**Status**: 🟡 Planning  
**Estimated Duration**: 2-3 days  
**Goal**: Build a comprehensive challenge library and assignment system

---

## Overview

Currently, the system has basic challenge support:
- ✅ Challenge database model exists
- ✅ Basic text area for custom challenge input
- ✅ Challenge stored with session
- ❌ No challenge service
- ❌ No challenge templates/library
- ❌ No challenge selection UI
- ❌ Basic challenge display in sidebar

Phase 6 will add a **professional challenge management system** with templates and improved UX.

---

## Current State Analysis

### Existing Components

**Database Model** (`models/models.py`):
```python
class Challenge(Base):
    - id, title, description
    - category (ChallengeCategory enum)
    - difficulty (ChallengeDifficulty enum)
    - instructions, starter_code, test_cases
    - tags (JSON), metadata (JSON)
    - is_template, estimated_duration
    - Relationships with Session
```

**Session Model** (`models/models.py`):
```python
class Session:
    - challenge_id (FK to challenges.id)
    - challenge_text (legacy text field)
```

**Session Creation** (`pages/session_create.py`):
- Simple text area for challenge input
- No template selection
- Uses `challenge_text` field only

**Candidate View** (`pages/candidate.py`):
- Shows challenge in sidebar with `.challenge-box` CSS
- Basic display, no enhanced formatting

### What's Missing

1. **Challenge Service** - CRUD operations, template management
2. **Challenge Templates** - 10-15 pre-built coding challenges with proper structure
3. **Challenge Selection UI** - Dropdown to select from templates OR custom input
4. **Enhanced Display** - Better formatting with syntax highlighting, metadata
5. **Challenge Categories** - Organize by type (algorithms, data structures, system design)

---

## Implementation Plan

### Task 1: Challenge Service (`services/challenge_service.py`)
**Duration**: 0.5 day  
**Priority**: HIGH

**Features**:
```python
class ChallengeService:
    # CRUD Operations
    def create_challenge(config: ChallengeConfig, db) -> Challenge
    def get_challenge(challenge_id: str, db) -> Challenge
    def update_challenge(challenge_id: str, updates: dict, db) -> Challenge
    def delete_challenge(challenge_id: str, db) -> bool
    
    # Template Management
    def list_templates(category: ChallengeCategory, difficulty: ChallengeDifficulty, db) -> List[Challenge]
    def get_all_templates(db) -> List[Challenge]
    def get_template_by_id(challenge_id: str, db) -> Challenge
    
    # Search & Filter
    def search_challenges(query: str, filters: dict, db) -> List[Challenge]
    def get_by_category(category: ChallengeCategory, db) -> List[Challenge]
    def get_by_difficulty(difficulty: ChallengeDifficulty, db) -> List[Challenge]
    
    # Statistics
    def get_challenge_stats(challenge_id: str, db) -> dict
    def get_popular_challenges(limit: int, db) -> List[Challenge]
```

**Key Points**:
- Use proper database queries with filters
- Implement proper error handling
- Add validation for challenge data
- Return Challenge objects, not dicts
- Handle relationships (Session linkage)

**Tests to Write**:
- Test CRUD operations
- Test template listing
- Test search/filter
- Test validation errors

---

### Task 2: Challenge Templates (Seed Data)
**Duration**: 1 day  
**Priority**: HIGH

**Create** `scripts/seed_challenges.py`:

**Template Categories**:
1. **Algorithms** (5 challenges)
   - Two Sum Problem (Easy)
   - Binary Search (Easy)
   - Merge Sorted Arrays (Medium)
   - Longest Palindromic Substring (Medium)
   - Merge K Sorted Lists (Hard)

2. **Data Structures** (5 challenges)
   - Implement Stack (Easy)
   - Implement Queue using Stacks (Easy)
   - LRU Cache (Medium)
   - Binary Search Tree Operations (Medium)
   - Trie Implementation (Hard)

3. **System Design** (3 challenges)
   - Design URL Shortener (Medium)
   - Design Rate Limiter (Medium)
   - Design Chat System (Hard)

4. **String Manipulation** (3 challenges)
   - Valid Anagram (Easy)
   - Group Anagrams (Medium)
   - Minimum Window Substring (Hard)

**Challenge Template Structure**:
```python
{
    "title": "Two Sum",
    "description": "Given an array of integers, return indices of two numbers that add up to a target.",
    "category": "ALGORITHMS",
    "difficulty": "EASY",
    "instructions": """
### Problem Statement
Given an array of integers `nums` and an integer `target`, return indices of the two numbers 
such that they add up to `target`.

### Constraints
- Each input has exactly one solution
- You may not use the same element twice
- Return answer in any order

### Examples
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: nums[0] + nums[1] = 9, so we return [0, 1]
    """,
    "starter_code": """
def two_sum(nums: List[int], target: int) -> List[int]:
    # Your code here
    pass
    """,
    "test_cases": [
        {"input": {"nums": [2,7,11,15], "target": 9}, "output": [0,1]},
        {"input": {"nums": [3,2,4], "target": 6}, "output": [1,2]},
    ],
    "tags": ["array", "hash-table", "easy"],
    "estimated_duration": 900,  # 15 minutes
    "metadata": {
        "hints": [
            "Think about using a hash map",
            "One-pass solution is possible"
        ],
        "related_concepts": ["Hash Tables", "Array Traversal"],
        "companies": ["Google", "Amazon", "Facebook"]
    }
}
```

**Seed Script Logic**:
1. Check if templates already exist (avoid duplicates)
2. Insert all challenge templates
3. Mark as `is_template=True`
4. Print summary of loaded challenges

---

### Task 3: Enhanced Session Creation UI
**Duration**: 0.5 day  
**Priority**: MEDIUM

**Update** `pages/session_create.py`:

**New UI Flow**:
```
┌─────────────────────────────────────────┐
│ Challenge Selection                     │
├─────────────────────────────────────────┤
│ ○ Select from Template Library          │
│   ├── Category: [Dropdown]              │
│   ├── Difficulty: [Dropdown]            │
│   └── Template: [Dropdown with preview] │
│                                          │
│ ○ Custom Challenge                       │
│   └── [Text Area]                        │
└─────────────────────────────────────────┘
```

**Implementation**:
```python
# In session_create.py

# Challenge selection mode
challenge_mode = st.radio(
    "Challenge Source",
    options=["📚 Template Library", "✏️ Custom Challenge"],
    horizontal=True
)

if challenge_mode == "📚 Template Library":
    # Load challenge service
    challenge_service = get_challenge_service()
    with get_db_context() as db:
        templates = challenge_service.get_all_templates(db)
    
    # Category filter
    categories = ["ALL"] + [c.value for c in ChallengeCategory]
    selected_category = st.selectbox("Category", categories)
    
    # Difficulty filter
    difficulties = ["ALL"] + [d.value for d in ChallengeDifficulty]
    selected_difficulty = st.selectbox("Difficulty", difficulties)
    
    # Filter templates
    filtered = filter_challenges(templates, selected_category, selected_difficulty)
    
    # Template selection dropdown
    if filtered:
        template_options = {f"{c.title} ({c.difficulty})": c.id for c in filtered}
        selected_template_name = st.selectbox("Select Challenge", list(template_options.keys()))
        selected_challenge_id = template_options[selected_template_name]
        
        # Show preview
        challenge = next(c for c in filtered if c.id == selected_challenge_id)
        with st.expander("📖 Challenge Preview"):
            st.markdown(f"**{challenge.title}**")
            st.markdown(challenge.description)
            st.markdown(f"*Estimated Duration: {challenge.estimated_duration // 60} minutes*")
    else:
        st.warning("No templates match your filters")
        selected_challenge_id = None

else:  # Custom Challenge
    challenge_text = st.text_area(
        "Challenge Description",
        height=200,
        placeholder="Enter your custom challenge..."
    )
    selected_challenge_id = None
```

**Save Logic**:
- If template selected: Use `challenge_id`
- If custom: Store in `challenge_text` (legacy field)
- Eventually migrate all to use Challenge records

---

### Task 4: Enhanced Challenge Display Component
**Duration**: 0.5 day  
**Priority**: MEDIUM

**Create** `components/candidate/challenge_display.py`:

```python
def render_challenge_panel(session: Session):
    """Render enhanced challenge display in sidebar."""
    
    if session.challenge_id:
        # Load full challenge from DB
        challenge = get_challenge(session.challenge_id)
        
        # Render with full structure
        st.markdown("### 📋 Challenge")
        
        # Title and metadata
        st.markdown(f"**{challenge.title}**")
        st.caption(f"{challenge.category.value} • {challenge.difficulty.value} • ~{challenge.estimated_duration // 60} min")
        
        # Collapsible sections
        with st.expander("📖 Instructions", expanded=True):
            st.markdown(challenge.instructions)
        
        if challenge.starter_code:
            with st.expander("💻 Starter Code"):
                st.code(challenge.starter_code, language="python")
        
        if challenge.metadata and "hints" in challenge.metadata:
            with st.expander("💡 Hints"):
                for i, hint in enumerate(challenge.metadata["hints"], 1):
                    st.markdown(f"{i}. {hint}")
    
    elif session.challenge_text:
        # Legacy text-only challenge
        st.markdown("### 📋 Challenge")
        st.markdown(session.challenge_text)
    
    else:
        # No challenge
        st.info("No challenge assigned for this session")
```

**Integration in** `pages/candidate.py`:
```python
# In sidebar, before resource panel
from components.candidate.challenge_display import render_challenge_panel

with st.sidebar:
    render_challenge_panel(session)
    st.markdown("---")
    # ... rest of sidebar (timer, tokens) ...
```

---

### Task 5: Database Migration & Testing
**Duration**: 0.5 day  
**Priority**: HIGH

**Database Updates**:
1. Ensure Challenge table exists (it does)
2. Run seed script to load templates
3. Verify foreign key constraints
4. Test cascading deletes

**Script**: `scripts/setup_challenges.py`
```python
#!/usr/bin/env python3
"""Setup challenge system: create tables, seed data."""

from models import get_db_context
from models.models import Challenge
from services.challenge_service import get_challenge_service
from scripts.seed_challenges import CHALLENGE_TEMPLATES

def setup_challenges():
    with get_db_context() as db:
        # Check if templates already exist
        challenge_service = get_challenge_service()
        existing = challenge_service.get_all_templates(db)
        
        if existing:
            print(f"✅ Found {len(existing)} existing templates")
            choice = input("Reload templates? This will delete existing (y/N): ")
            if choice.lower() != 'y':
                return
            
            # Delete existing templates
            for c in existing:
                challenge_service.delete_challenge(c.id, db)
            print("🗑️  Deleted existing templates")
        
        # Load new templates
        print("📚 Loading challenge templates...")
        for template_data in CHALLENGE_TEMPLATES:
            challenge = challenge_service.create_challenge(template_data, db)
            print(f"  ✅ {challenge.title} ({challenge.difficulty})")
        
        print(f"\n🎉 Successfully loaded {len(CHALLENGE_TEMPLATES)} challenge templates!")

if __name__ == "__main__":
    setup_challenges()
```

**Tests** (`tests/test_challenge_service.py`):
```python
class TestChallengeService:
    def test_create_challenge(self, db_session):
        """Test challenge creation"""
        service = get_challenge_service()
        config = {...}
        challenge = service.create_challenge(config, db_session)
        assert challenge.id is not None
        assert challenge.title == config["title"]
    
    def test_list_templates(self, db_session):
        """Test template listing"""
        # ... test code
    
    def test_filter_by_category(self, db_session):
        """Test category filtering"""
        # ... test code
    
    def test_filter_by_difficulty(self, db_session):
        """Test difficulty filtering"""
        # ... test code
```

---

## Testing Plan

### Unit Tests
- [ ] Challenge service CRUD operations
- [ ] Template listing and filtering
- [ ] Search functionality
- [ ] Validation logic

### Integration Tests
- [ ] Session creation with template
- [ ] Session creation with custom challenge
- [ ] Challenge display in candidate view
- [ ] Challenge persistence across sessions

### UI Tests (Manual)
- [ ] Select challenge from dropdown
- [ ] Preview challenge before selection
- [ ] Filter by category and difficulty
- [ ] Custom challenge input
- [ ] Challenge display in candidate sidebar
- [ ] Collapsible sections work
- [ ] Syntax highlighting for code
- [ ] Mobile responsive (sidebar challenge)

---

## Success Criteria

### Phase 6 Complete When:
- ✅ Challenge service implemented with all methods
- ✅ 10-15 challenge templates loaded in database
- ✅ Session creation has template selection dropdown
- ✅ Custom challenge option still available
- ✅ Candidate view shows enhanced challenge display
- ✅ All tests passing
- ✅ No regressions in existing functionality

---

## Migration Path

### For Existing Sessions:
- Sessions with `challenge_text` continue to work (backward compatible)
- New sessions should use `challenge_id`
- Eventually migrate old text challenges to Challenge records

### Database Changes:
- No breaking changes to Session model
- Challenge table already exists
- Just populate with seed data

---

## File Changes Summary

### New Files:
1. `services/challenge_service.py` - Challenge CRUD service
2. `components/candidate/challenge_display.py` - Enhanced display component
3. `scripts/seed_challenges.py` - Challenge template data
4. `scripts/setup_challenges.py` - Setup script
5. `tests/test_challenge_service.py` - Unit tests

### Modified Files:
1. `pages/session_create.py` - Add template selection UI
2. `pages/candidate.py` - Integrate enhanced challenge display
3. `services/__init__.py` - Export challenge service

### No Changes Required:
- `models/models.py` - Challenge model already exists
- Database schema - Already has challenges table

---

## Timeline

**Day 1**:
- Morning: Build challenge service (Task 1)
- Afternoon: Create challenge templates (Task 2)
- Evening: Write unit tests (Task 5)

**Day 2**:
- Morning: Enhanced session creation UI (Task 3)
- Afternoon: Challenge display component (Task 4)
- Evening: Integration testing (Task 5)

**Day 3**:
- Morning: Bug fixes and polish
- Afternoon: Documentation
- Evening: Phase 6 completion document

---

## Risk Mitigation

**Risk**: Templates don't match real interview scenarios  
**Mitigation**: Research common coding interview problems, validate with developers

**Risk**: UI becomes cluttered with too many options  
**Mitigation**: Use collapsible sections, clean layout, optional filters

**Risk**: Performance issues loading many templates  
**Mitigation**: Limit initial load, add caching, paginate if needed

**Risk**: Backward compatibility with existing sessions  
**Mitigation**: Keep `challenge_text` field, graceful fallback in display

---

## Dependencies

**Required**:
- Phase 1-5 complete ✅
- Database models exist ✅
- Session service functional ✅

**Optional**:
- Syntax highlighting library (already in Streamlit)
- Markdown rendering (already available)

---

## Next Steps After Phase 6

**Phase 7: Enhanced Interviewer Controls**
- Pause/Resume functionality
- Time/Token extensions (already have basics)
- Session lock/unlock
- Event timeline
- More sophisticated session management

---

**Status**: Ready for Implementation  
**Approval**: Pending user confirmation  
**Estimated Completion**: 2-3 days from start

