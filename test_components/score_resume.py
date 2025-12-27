"""
Example: Parse and score a resume file
Usage: python examples/score_resume.py [path/to/resume.pdf]
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser.resume_parser import ResumeParser
from src.scoring.ats_scorer import ATSScorer


def print_header(title, char="="):
    """Print formatted header."""
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}")


def print_score_bar(score, max_score):
    """Print visual score bar."""
    percentage = (score / max_score * 100) if max_score > 0 else 0
    filled = int(percentage / 2)  # 50 chars = 100%
    bar = "█" * filled + "░" * (50 - filled)
    print(f"  [{bar}] {percentage:.1f}%")


def main():
    """Main scoring example."""
    # Get file path
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]
    else:
        sample_dir = Path("data/sample_resumes")
        if sample_dir.exists():
            resumes = list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.pdf")) + list(sample_dir.glob("*.docx"))
            if resumes:
                resume_path = str(resumes[0])
            else:
                print(" No sample resumes found")
                print("\nUsage: python examples/score_resume.py [path/to/resume.pdf]")
                return 1
        else:
            print("❌ No resume file specified")
            print("\nUsage: python examples/score_resume.py [path/to/resume.pdf]")
            return 1
    
    print_header(" ATS RESUME SCORER - PHASE 2 DEMO")
    print(f"\n Processing: {resume_path}")
    
    try:
        # Parse resume
        print("\n Step 1/2: Parsing resume...")
        parser = ResumeParser()
        resume_data = parser.parse(resume_path)
        print(f"✓ Parsed successfully ({resume_data.metadata.parsing_time_ms:.1f}ms)")
        
        # Score resume
        print(" Step 2/2: Calculating ATS score...")
        scorer = ATSScorer()
        ats_score = scorer.score(resume_data)
        print(f"✓ Scoring complete ({ats_score.scoring_metadata['scoring_time_ms']:.1f}ms)")
        
        # Display overall score
        print_header(" OVERALL ATS SCORE")
        print(f"\n  Score: {ats_score.total_score:.1f} / {ats_score.max_score}")
        print(f"  Grade: {ats_score.grade}")
        print_score_bar(ats_score.total_score, ats_score.max_score)
        
        # Display category breakdown
        print_header(" CATEGORY BREAKDOWN")
        
        categories = [
            ('Section Completeness', ats_score.section_completeness),
            ('Content Quality', ats_score.content_quality),
            ('Contact Information', ats_score.contact_information),
            ('Structure & Organization', ats_score.structure_organization)
        ]
        
        for name, category in categories:
            if category:
                print(f"\n  {name}:")
                print(f"    Score: {category.score:.1f}/{category.max_score:.1f} ({category.percentage:.0f}%)")
                for item in category.breakdown:
                    print(f"      • {item}")
        
        # Display section scores
        print_header(" SECTION SCORES")
        for section_name, section_score in ats_score.section_scores.items():
            status = "✓" if section_score.present else "✗"
            print(f"\n  {status} {section_name.title()}")
            print(f"    Score: {section_score.score:.1f}/{section_score.max_score:.1f}")
            if section_score.present:
                print(f"    Length: {section_score.content_length} characters")
            if section_score.issues:
                print(f"    Issues: {', '.join(section_score.issues)}")
        
        # Display strengths
        if ats_score.strengths:
            print_header(" STRENGTHS")
            for i, strength in enumerate(ats_score.strengths, 1):
                print(f"  {i}. {strength}")
        
        # Display weaknesses
        if ats_score.weaknesses:
            print_header("  AREAS FOR IMPROVEMENT")
            for i, weakness in enumerate(ats_score.weaknesses, 1):
                print(f"  {i}. {weakness}")
        
        # Display suggestions
        if ats_score.suggestions:
            print_header(" RECOMMENDATIONS")
            for i, suggestion in enumerate(ats_score.suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        # Save results
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save full report
        output_file = output_dir / f"{Path(resume_path).stem}_ats_score.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ats_score.to_dict(), f, indent=2, ensure_ascii=False)
        
        print_header(" RESULTS SAVED")
        print(f"\n  Full report: {output_file}")
        print(f"  File size: {output_file.stat().st_size:,} bytes")
        
        # Final summary
        print("\n" + "=" * 70)
        if ats_score.percentage >= 80:
            print("   Excellent! Your resume is well-optimized for ATS systems.")
        elif ats_score.percentage >= 70:
            print("   Good! Address a few areas to improve ATS compatibility.")
        elif ats_score.percentage >= 60:
            print("   Fair. Implementing suggestions will boost your score.")
        else:
            print("   Needs work. Focus on section completeness first.")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())