"""
Example: Parse and score resume with role detection
Usage: python examples/score_with_role.py [resume_path] [optional_role_id]
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser.resume_parser import ResumeParser
from src.scoring.ats_scorer import ATSScorer
from src.roles.role_definitions import RoleManager
from src.roles.role_matcher import RoleMatcher


def print_header(title, char="="):
    """Print formatted header."""
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}")


def main():
    """Main scoring with role detection."""
    # Get file path
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]
    else:
        sample_dir = Path("data/sample_resumes")
        if sample_dir.exists():
            resumes = list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.pdf"))
            if resumes:
                resume_path = str(resumes[0])
            else:
                print(" No sample resumes found")
                return 1
        else:
            print(" No resume file specified")
            return 1
    
    # Get optional role override
    role_override = sys.argv[2] if len(sys.argv) > 2 else None
    
    print_header(" ROLE-AWARE ATS SCORER - PHASE 3 DEMO")
    print(f"\n Resume: {resume_path}")
    if role_override:
        print(f" Target Role: {role_override}")
    
    try:
        # Parse resume
        print("\n Step 1/3: Parsing resume...")
        parser = ResumeParser()
        resume_data = parser.parse(resume_path)
        print(f"✓ Parsed ({resume_data.metadata.parsing_time_ms:.1f}ms)")
        
        # Show available roles
        print("\n Step 2/3: Loading role definitions...")
        role_manager = RoleManager()
        available_roles = role_manager.list_roles()
        
        if available_roles:
            print(f"✓ Loaded {len(available_roles)} role definitions:")
            for role_id in available_roles:
                role_def = role_manager.get_role(role_id)
                print(f"   • {role_def.role_name} ({role_id})")
        else:
            print("  No role definitions found (using baseline scoring)")
        
        # Detect role if not specified
        if not role_override and available_roles:
            print("\n Detecting role from resume...")
            role_matcher = RoleMatcher(role_manager)
            matches = role_matcher.match_all_roles(resume_data)
            
            if matches:
                print("\n Role Match Results:")
                for i, match in enumerate(matches[:3], 1):  # Top 3
                    print(f"   {i}. {match.role_name}: {match.confidence:.1%} confidence")
                    if match.matching_skills:
                        print(f"      Matching skills: {', '.join(match.matching_skills[:5])}")
                
                best_match = matches[0]
                if best_match.confidence >= 0.3:
                    role_override = best_match.role_id
                    print(f"\n✓ Selected: {best_match.role_name}")
        
        # Score resume
        print(f"\n⏳ Step 3/3: Scoring resume...")
        scorer = ATSScorer()
        ats_score = scorer.score(resume_data, role_id=role_override)
        print(f"✓ Scoring complete ({ats_score.scoring_metadata['scoring_time_ms']:.1f}ms)")
        
        # Display role info
        if ats_score.scoring_metadata.get('role_detected'):
            print_header("🎯 ROLE ANALYSIS")
            print(f"\n  Detected Role: {ats_score.scoring_metadata['role_detected']}")
            print(f"  Confidence: {ats_score.scoring_metadata['role_confidence']:.1%}")
        
        # Display score
        print_header(" ATS SCORE")
        print(f"\n  Total Score: {ats_score.total_score:.1f}/100")
        print(f"  Grade: {ats_score.grade}")
        print(f"  Percentage: {ats_score.percentage:.1f}%")
        
        # Category breakdown
        print_header(" CATEGORY SCORES")
        categories = [
            ('Section Completeness', ats_score.section_completeness),
            ('Content Quality', ats_score.content_quality),
            ('Contact Information', ats_score.contact_information),
            ('Structure & Organization', ats_score.structure_organization)
        ]
        
        for name, category in categories:
            if category:
                print(f"\n  {name}: {category.score:.1f}/{category.max_score:.1f} ({category.percentage:.0f}%)")
        
        # Strengths
        if ats_score.strengths:
            print_header("STRENGTHS")
            for i, strength in enumerate(ats_score.strengths[:5], 1):
                print(f"  {i}. {strength}")
        
        # Weaknesses
        if ats_score.weaknesses:
            print_header("  AREAS FOR IMPROVEMENT")
            for i, weakness in enumerate(ats_score.weaknesses[:5], 1):
                print(f"  {i}. {weakness}")
        
        # Role-specific suggestions
        if ats_score.suggestions:
            print_header(" RECOMMENDATIONS")
            for i, suggestion in enumerate(ats_score.suggestions[:8], 1):
                print(f"  {i}. {suggestion}")
        
        # Save results
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{Path(resume_path).stem}_role_score.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ats_score.to_dict(), f, indent=2, ensure_ascii=False)
        
        print_header(" RESULTS SAVED")
        print(f"\n  Report saved to: {output_file}")
        
        print("\n" + "=" * 70)
        print("   Role-aware scoring complete!")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())