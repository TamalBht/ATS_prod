"""
ats_compatibility_check.py - FIXED VERSION

Phase 6 Example Execution - ATS Compatibility & Formatting Analysis
Handles ResumeData objects from parser.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.parser.resume_parser import ResumeParser
from src.ats.ats_compatibility_scorer import ATSCompatibilityScorer


class ATSCompatibilityDemo:
    """
    Demonstrates Phase 6 ATS compatibility analysis capabilities.
    """
    
    def __init__(self):
        """Initialize demo with all ATS analysis components."""
        self.parser = ResumeParser()
        self.ats_scorer = ATSCompatibilityScorer()
        
        print("=" * 80)
        print("PHASE 6: ATS COMPATIBILITY & FORMATTING ANALYSIS DEMO")
        print("=" * 80)
        print()
    
    def run_complete_analysis(self, resume_path: str, role_name: str = None, detailed: bool = False):
        """
        Run complete ATS compatibility analysis on a resume.
        
        Args:
            resume_path: Path to PDF/DOCX resume
            role_name: Optional role name for keyword matching
            detailed: Whether to show detailed component analysis
        """
        print(f" Analyzing Resume: {resume_path}")
        if role_name:
            print(f" Target Role: {role_name}")
        print("-" * 80)
        
        # Step 1: Parse Resume
        print("\n[Step 1/4] Parsing resume...")
        try:
            parsed_resume_obj = self.parser.parse(resume_path)
            
            # Convert ResumeData object to dictionary
            parsed_resume = self._convert_to_dict(parsed_resume_obj)
            
            raw_text = parsed_resume.get('raw_text', '')
            print(f"✓ Successfully parsed resume")
            sections = [k for k in parsed_resume.keys() if k not in ['raw_text', 'metadata']]
            print(f"  Sections found: {', '.join(sections)}")
        except Exception as e:
            print(f"✗ Failed to parse resume: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Step 2: Load Role Keywords (if role specified)
        role_keywords = None
        if role_name:
            print(f"\n[Step 2/4] Loading role keywords for {role_name}...")
            role_keywords = self._load_role_keywords(role_name)
            if role_keywords:
                print(f"✓ Loaded {len(role_keywords)} target keywords")
            else:
                print(f"⚠ No role keywords found, continuing without role-specific analysis")
        else:
            print("\n[Step 2/4] Skipping role keyword loading (no role specified)")
        
        # Step 3: Run ATS Compatibility Analysis
        print("\n[Step 3/4] Running ATS compatibility analysis...")
        try:
            ats_results = self.ats_scorer.score_resume(
                resume_path,
                parsed_resume,
                raw_text,
                role_keywords
            )
            print(f"✓ Analysis complete")
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Step 4: Display Results
        print("\n[Step 4/4] ATS Compatibility Results")
        print("=" * 80)
        
        if detailed:
            self._display_detailed_results(ats_results)
        else:
            self._display_summary_results(ats_results)
        
        # Generate and display text report
        print("\n" + "=" * 80)
        print("COMPREHENSIVE ATS REPORT")
        print("=" * 80)
        report = self.ats_scorer.generate_ats_report(ats_results)
        print(report)
        
        # Save Results
        output_path = self._save_results(resume_path, ats_results)
        print(f"\n Results saved to: {output_path}")
        
        return ats_results
    
    def _convert_to_dict(self, resume_obj) -> dict:
        """
        Convert ResumeData object to dictionary.
        
        Args:
            resume_obj: ResumeData object or dict
            
        Returns:
            Dictionary representation
        """
        # If already a dict, return as-is
        if isinstance(resume_obj, dict):
            return resume_obj
        
        # Convert object to dict
        result = {}
        
        # Check if it has __dict__ attribute
        if hasattr(resume_obj, '__dict__'):
            for key, value in resume_obj.__dict__.items():
                if not key.startswith('_'):
                    result[key] = self._convert_value(value)
        
        # Try to access as dataclass
        elif hasattr(resume_obj, '__dataclass_fields__'):
            import dataclasses
            result = dataclasses.asdict(resume_obj)
        
        # Fallback: try common attributes
        else:
            common_attrs = [
                'summary', 'skills', 'experience', 'projects', 
                'education', 'certifications', 'contact', 'raw_text'
            ]
            for attr in common_attrs:
                if hasattr(resume_obj, attr):
                    result[attr] = self._convert_value(getattr(resume_obj, attr))
        
        return result
    
    def _convert_value(self, value):
        """Convert nested objects to serializable format."""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, dict):
            return {k: self._convert_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._convert_value(item) for item in value]
        elif hasattr(value, '__dict__'):
            return self._convert_to_dict(value)
        elif hasattr(value, '__dataclass_fields__'):
            import dataclasses
            return dataclasses.asdict(value)
        else:
            return str(value)
    
    def _load_role_keywords(self, role_name: str) -> list:
        """Load keywords from role definition file."""
        role_path = Path(f"data/roles/{role_name}.yaml")
        
        if not role_path.exists():
            return None
        
        try:
            import yaml
            with open(role_path, 'r') as f:
                role_data = yaml.safe_load(f)
            
            # Extract keywords from role definition
            keywords = []
            if 'required_skills' in role_data:
                keywords.extend(role_data['required_skills'])
            if 'preferred_skills' in role_data:
                keywords.extend(role_data['preferred_skills'])
            if 'keywords' in role_data:
                keywords.extend(role_data['keywords'])
            
            return list(set(keywords))  # Remove duplicates
        except Exception as e:
            print(f"⚠ Error loading role keywords: {e}")
            return None
    
    def _display_summary_results(self, results: dict):
        """Display summary of ATS analysis results."""
        summary = results['summary']
        
        # Overall Score
        score = summary['score']
        grade = summary['grade']
        bar_length = int(score / 5)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        print(f"\n  OVERALL ATS COMPATIBILITY SCORE")
        print(f"   [{bar}] {score:.1f}/100")
        print(f"   Grade: {grade} | {summary['readiness_level']}")
        print(f"   ATS Ready: {'✓ YES' if results['is_ats_ready'] else '✗ NO'}")
        
        # Assessment
        print(f"\n Assessment:")
        print(f"   {summary['assessment']}")
        
        # Component Scores
        print(f"\n Component Scores:")
        for component, score in results['component_scores'].items():
            bar_length = int(score / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            status = "✓" if score >= 70 else "⚠" if score >= 50 else "✗"
            print(f"   {status} {component.capitalize():15} [{bar}] {score:.1f}")
        
        # Issues Summary
        issues = results['issues_by_severity']
        print(f"\n  Issues Detected: {issues['total_count']}")
        if issues['critical_count'] > 0:
            print(f"   🔴 Critical: {issues['critical_count']}")
        if issues['high_count'] > 0:
            print(f"   🟠 High:     {issues['high_count']}")
        if issues['medium_count'] > 0:
            print(f"   🟡 Medium:   {issues['medium_count']}")
        if issues['low_count'] > 0:
            print(f"   🟢 Low:      {issues['low_count']}")
        
        # Top Recommendations
        print(f"\n TOP RECOMMENDATIONS:")
        recommendations = results['recommendations'][:5]  # Top 5
        
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(rec['priority'], '•')
            
            print(f"\n   {priority_icon} {i}. {rec['issue']}")
            print(f"      → {rec['action']}")
    
    def _display_detailed_results(self, results: dict):
        """Display detailed component-by-component results."""
        self._display_summary_results(results)
        
        print("\n\n" + "=" * 80)
        print("DETAILED COMPONENT ANALYSIS")
        print("=" * 80)
        
        detailed = results['detailed_analysis']
        
        # Format Analysis
        print("\n FORMAT ANALYSIS")
        print("-" * 80)
        format_data = detailed['format']
        print(f"File Format: {format_data['file_format']}")
        print(f"Score: {format_data['format_score']:.1f}/100")
        print(f"ATS Friendly: {'Yes' if format_data['is_ats_friendly'] else 'No'}")
        if format_data.get('structure_details'):
            print(f"\nStructure Details:")
            for key, value in format_data['structure_details'].items():
                print(f"  • {key}: {value}")
        if format_data['issues']:
            print(f"\nIssues ({len(format_data['issues'])}):")
            for issue in format_data['issues']:
                print(f"  [{issue['severity'].upper()}] {issue['issue']}")
        
        # Structure Analysis
        print("\n\n STRUCTURE ANALYSIS")
        print("-" * 80)
        structure_data = detailed['structure']
        print(f"Score: {structure_data['structure_score']:.1f}/100")
        print(f"Well Structured: {'Yes' if structure_data['is_well_structured'] else 'No'}")
        print(f"\nRequired Sections:")
        print(f"  ✓ Present: {', '.join(structure_data['required_sections']['present']) or 'None'}")
        print(f"  ✗ Missing: {', '.join(structure_data['required_sections']['missing']) or 'None'}")
        print(f"\nRecommended Sections:")
        print(f"  ✓ Present: {', '.join(structure_data['recommended_sections']['present']) or 'None'}")
        print(f"  • Missing: {', '.join(structure_data['recommended_sections']['missing']) or 'None'}")
        
        # Contact Analysis
        print("\n\n CONTACT INFORMATION ANALYSIS")
        print("-" * 80)
        contact_data = detailed['contact']
        print(f"Score: {contact_data['contact_score']:.1f}/100")
        print(f"Complete Contact: {'Yes' if contact_data['has_complete_contact'] else 'No'}")
        print(f"\nContact Details:")
        for key, value in contact_data['contact_details'].items():
            status = "✓" if value else "✗"
            display_value = value if value else "Not found"
            print(f"  {status} {key.capitalize()}: {display_value}")
        
        # Keyword Analysis
        print("\n\n KEYWORD OPTIMIZATION ANALYSIS")
        print("-" * 80)
        keyword_data = detailed['keywords']
        print(f"Score: {keyword_data['keyword_score']:.1f}/100")
        print(f"Optimized: {'Yes' if keyword_data['is_optimized'] else 'No'}")
        print(f"\nMetrics:")
        for key, value in keyword_data['metrics'].items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        if keyword_data.get('role_keyword_analysis') and keyword_data['role_keyword_analysis'].get('found_keywords'):
            role_analysis = keyword_data['role_keyword_analysis']
            print(f"\nRole Keyword Match: {role_analysis['match_rate']*100:.0f}%")
            print(f"  Found: {role_analysis['found_count']} keywords")
            print(f"  Missing: {role_analysis['missing_count']} keywords")
            if role_analysis['missing_keywords']:
                print(f"  Missing Keywords: {', '.join(role_analysis['missing_keywords'][:10])}")
        
        # Extractability
        print("\n\n TEXT EXTRACTABILITY ANALYSIS")
        print("-" * 80)
        extract_data = detailed['extractability']
        print(f"Score: {extract_data['extractability_score']:.1f}/100")
        print(f"Extractable: {'Yes' if extract_data['is_extractable'] else 'No'}")
        print(f"Text Length: {extract_data.get('text_length', 0)} characters")
    
    def _save_results(self, resume_path: str, results: dict) -> str:
        """Save analysis results to JSON file."""
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        resume_name = Path(resume_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{resume_name}_ats_compatibility_{timestamp}.json"
        output_path = output_dir / output_filename
        
        # Add metadata
        results['metadata'] = {
            'resume_file': str(resume_path),
            'analysis_date': datetime.now().isoformat(),
            'phase': 'Phase 6 - ATS Compatibility & Formatting Analysis'
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return str(output_path)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Phase 6: ATS Compatibility & Formatting Analysis Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ats_compatibility_check.py
  python ats_compatibility_check.py --resume data/sample_resume/resume.pdf
  python ats_compatibility_check.py --resume my_resume.pdf --role backend_engineer
  python ats_compatibility_check.py --resume my_resume.pdf --detailed
        """
    )
    
    parser.add_argument(
        '--resume',
        type=str,
        help='Path to resume PDF/DOCX file'
    )
    
    parser.add_argument(
        '--role',
        type=str,
        help='Role name for keyword matching (e.g., backend_engineer, data_scientist)'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed component analysis'
    )
    
    args = parser.parse_args()
    
    # Initialize demo
    demo = ATSCompatibilityDemo()
    
    # Determine resume path
    if args.resume:
        resume_path = args.resume
    else:
        # Try to find sample resume
        possible_paths = [
            'data/sample_resume/TamalBhattacharjee.pdf',
            'data/sample_resumes/TamalBhattacharjee.pdf',
            'data/sample_resume/sample_resume.pdf',
            'data/sample_resumes/sample_resume.pdf',
            'sample_resume.pdf'
        ]
        
        resume_path = None
        for path in possible_paths:
            if os.path.exists(path):
                resume_path = path
                break
        
        if not resume_path:
            print(" Error: No resume file specified and no sample resume found.")
            print("\nUsage:")
            print("  python ats_compatibility_check.py --resume path/to/resume.pdf")
            print("\nOr place a sample resume at:")
            print("  data/sample_resume/")
            sys.exit(1)
    
    # Validate file exists
    if not os.path.exists(resume_path):
        print(f" Error: Resume file not found: {resume_path}")
        sys.exit(1)
    
    # Run analysis
    try:
        results = demo.run_complete_analysis(resume_path, args.role, args.detailed)
        
        if results:
            print("\n" + "=" * 80)
            print(" ANALYSIS COMPLETE")
            print("=" * 80)
            
            score = results['overall_ats_score']
            grade = results['summary']['grade']
            
            print(f"\n Final ATS Compatibility Score: {score:.2f}/100 (Grade: {grade})")
            print(f"   Readiness: {results['readiness_level']}")
            
            # Quick action items
            print("\n Next Steps:")
            critical_count = results['issues_by_severity']['critical_count']
            high_count = results['issues_by_severity']['high_count']
            
            if critical_count > 0:
                print(f"   1. FIX IMMEDIATELY: {critical_count} critical issue(s)")
            if high_count > 0:
                print(f"   2. Address {high_count} high-priority issue(s)")
            if results['is_ats_ready']:
                print("   3. Resume is ATS-ready - consider keyword optimization per job")
            else:
                print("   3. Review all recommendations before submitting")
            
            print("\n   Run with --detailed flag for comprehensive component analysis.")
    
    except Exception as e:
        print(f"\n Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()