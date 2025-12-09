#!/usr/bin/env python3
"""
Setup challenge system: load challenge templates into database.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models import get_db_context
from services.challenge_service import get_challenge_service, ChallengeConfig
from scripts.seed_challenges import CHALLENGE_TEMPLATES
from utils.logger import logger


def setup_challenges():
    """Load challenge templates into database."""
    challenge_service = get_challenge_service()
    
    with get_db_context() as db:
        # Check if templates already exist
        existing = challenge_service.get_all_templates(db)
        
        if existing:
            print(f"✅ Found {len(existing)} existing challenge templates")
            print("\nExisting templates:")
            for c in existing:
                print(f"  - {c.title} ({c.category.value} - {c.difficulty.value})")
            
            choice = input("\nReload templates? This will delete existing templates (y/N): ")
            if choice.lower() != 'y':
                print("Keeping existing templates.")
                return
            
            # Delete existing templates
            print("\n🗑️  Deleting existing templates...")
            for c in existing:
                challenge_service.delete_challenge(c.id, db)
            print("Deleted all existing templates")
        
        # Load new templates
        print(f"\n📚 Loading {len(CHALLENGE_TEMPLATES)} challenge templates...")
        print("=" * 60)
        
        loaded_count = 0
        for template_data in CHALLENGE_TEMPLATES:
            try:
                # Create ChallengeConfig from template data
                config = ChallengeConfig(
                    title=template_data["title"],
                    description=template_data["description"],
                    category=template_data["category"],
                    difficulty=template_data["difficulty"],
                    instructions=template_data.get("instructions"),
                    starter_code=template_data.get("starter_code"),
                    test_cases=template_data.get("test_cases"),
                    tags=template_data.get("tags"),
                    metadata=template_data.get("metadata"),
                    is_template=True,
                    estimated_duration=template_data.get("estimated_duration")
                )
                
                challenge = challenge_service.create_challenge(config, db)
                loaded_count += 1
                
                # Show progress
                category_str = challenge.category.value.replace('_', ' ').title()
                difficulty_str = challenge.difficulty.value.capitalize()
                duration_str = f"{challenge.estimated_duration // 60} min" if challenge.estimated_duration else "N/A"
                
                print(f"  ✅ {challenge.title:<35} | {category_str:<20} | {difficulty_str:<8} | {duration_str}")
                
            except Exception as e:
                print(f"  ❌ Failed to load '{template_data['title']}': {e}")
                logger.error(f"Failed to load challenge template: {e}")
        
        print("=" * 60)
        print(f"\n🎉 Successfully loaded {loaded_count}/{len(CHALLENGE_TEMPLATES)} challenge templates!")
        
        # Print summary
        from collections import Counter
        categories = [c["category"] for c in CHALLENGE_TEMPLATES]
        difficulties = [c["difficulty"] for c in CHALLENGE_TEMPLATES]
        
        print("\n📊 Summary:")
        print(f"  Total challenges: {loaded_count}")
        print(f"\n  By Category:")
        for cat, count in Counter(categories).items():
            print(f"    - {cat.value.replace('_', ' ').title()}: {count}")
        print(f"\n  By Difficulty:")
        for diff, count in Counter(difficulties).items():
            print(f"    - {diff.value.capitalize()}: {count}")
        
        print("\n✅ Challenge system setup complete!")


if __name__ == "__main__":
    print("=" * 60)
    print("       INTERVIEW BUDDY - Challenge System Setup")
    print("=" * 60)
    print()
    
    try:
        setup_challenges()
    except Exception as e:
        print(f"\n❌ Error setting up challenges: {e}")
        logger.error(f"Challenge setup failed: {e}", exc_info=True)
        sys.exit(1)

