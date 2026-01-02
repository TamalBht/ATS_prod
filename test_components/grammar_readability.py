"""
grammar_readability.py

Phase 5 Example Execution - Grammar & Readability Intelligence
Demonstrates complete language quality analysis on a sample PDF resume.

Usage:
    python grammar_readability.py
    python grammar_readability.py --resume path/to/resume.pdf
    python grammar_readability.py --detailed
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
from src.language.language_scorer import LanguageScorer
from src.language.grammar_checker import GrammarChecker
from src.language.readability_analyzer import ReadabilityAnalyzer
from src.language.clarity_scorer import ClarityScorer


class GrammarReadabilityDemo:
    """
    Demonstrates Phase 5 language quality analysis capabilities.
    """
    
    def __init__(self, use_language_tool: bool = False):
        """
        Initialize demo with all language analysis components.
        
        Args:
            use_language_tool: Whether to use LanguageTool (requires Java)
        """
        self.parser = ResumeParser()
        self.language_scorer = LanguageScorer(use_language_tool=use_language_tool)
        self.grammar_checker = GrammarChecker(use_language_tool=use_language_tool)
        self.readability_analyzer = ReadabilityAnalyzer()
        self.clarity_scorer = ClarityScorer()
        
        print("=" * 80)
        print("PHASE 5: GRAMMAR & READABILITY INTELLIGENCE DEMO")
        print("=" * 80)
        print(f"Language Tool: {'Enabled' if use_language_tool else 'Disabled (using basic rules)'}")
        print()
    
    def run_complete_analysis(self, resume_path: str, detailed: bool = False):
        """
        Run complete language quality analysis on a resume.
        
        Args:
            resume_path: Path to PDF/DOCX resume
            detailed: Whether to show detailed component analysis
        """
        print(f"📄 Analyzing Resume: {resume_path}")
        print("-" * 80)
        
        # Step 1: Parse Resume
        print("\n[Step 1/5] Parsing resume...")
        try:
            parsed_resume = self.parser.parse(resume_path)
            print(f"✓ Successfully parsed resume")
            print(f"  Sections found: {', '.join(parsed_resume.sections.keys())}")

        except Exception as e:
            print(f"✗ Failed to parse resume: {e}")
            return None
        
        # Step 2: Run Complete Language Analysis
        print("\n[Step 2/5] Running language quality analysis...")
        try:
            language_results = self.language_scorer.score_resume_sections(parsed_resume)
            print(f"✓ Analysis complete")
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
            return None
        
        # Step 3: Display Results
        print("\n[Step 3/5] Language Quality Results")
        print("=" * 80)
        self._display_overall_results(language_results)
        
        if detailed:
            print("\n[Step 4/5] Detailed Section Analysis")
            print("=" * 80)
            self._display_section_analysis(language_results)
            
            print("\n[Step 5/5] Component Deep Dive")
            print("=" * 80)
            self._display_component_details(language_results)
        else:
            print("\n[Step 4/5] Section Scores")
            print("=" * 80)
            self._display_section_summary(language_results)
            
            print("\n[Step 5/5] Recommendations")
            print("=" * 80)
            self._display_recommendations(language_results)
        
        # Save Results
        output_path = self._save_results(resume_path, language_results)
        print(f"\n💾 Results saved to: {output_path}")
        
        return language_results
    
    def _display_overall_results(self, results: dict):
        """Display overall language quality score and summary."""
        summary = results['summary']
        
        print(f"\n🎯 OVERALL LANGUAGE QUALITY SCORE: {summary['overall_score']:.2f}/100")
        print(f"   Grade: {summary['grade']}")
        print(f"   Assessment: {summary['assessment']}")
        print(f"\n   📊 Sections Analyzed: {summary['sections_analyzed']}")
        
        if summary['strongest_section']:
            print(f"   ✓ Strongest Section: {summary['strongest_section'].upper()}")
        if summary['weakest_section']:
            print(f"   ⚠ Weakest Section: {summary['weakest_section'].upper()}")
    
    def _display_section_summary(self, results: dict):
        """Display summary of section scores."""
        section_scores = results['section_scores']
        
        if not section_scores:
            print("No sections available for analysis.")
            return
        
        print("\n📋 Section Scores:")
        print("-" * 80)
        
        for section_name, section_data in section_scores.items():
            score = section_data['language_quality_score']
            components = section_data['components']
            
            # Score bar visualization
            bar_length = int(score / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            print(f"\n{section_name.upper()}: {score:.1f}/100")
            print(f"[{bar}]")
            print(f"  Grammar:     {components['grammar']['score']:.1f}")
            print(f"  Readability: {components['readability']['score']:.1f}")
            print(f"  Clarity:     {components['clarity']['score']:.1f}")
    
    def _display_section_analysis(self, results: dict):
        """Display detailed section-by-section analysis."""
        section_scores = results['section_scores']
        
        for section_name, section_data in section_scores.items():
            print(f"\n{'─' * 80}")
            print(f"📝 {section_name.upper()} SECTION")
            print(f"{'─' * 80}")
            
            score = section_data['language_quality_score']
            components = section_data['components']
            
            print(f"\nOverall Score: {score:.2f}/100")
            print(f"Assessment: {section_data['overall_assessment']}")
            
            # Grammar Details
            grammar = components['grammar']
            print(f"\n  📖 GRAMMAR: {grammar['score']:.1f}/100")
            print(f"     Total Issues: {grammar['total_issues']}")
            if grammar['issue_breakdown']:
                print(f"     Breakdown:")
                for issue_type, count in grammar['issue_breakdown'].items():
                    if count > 0:
                        print(f"       - {issue_type.capitalize()}: {count}")
            print(f"     {grammar['explanation']}")
            
            # Readability Details
            readability = components['readability']
            print(f"\n  📊 READABILITY: {readability['score']:.1f}/100")
            print(f"     Flesch Reading Ease: {readability['flesch_reading_ease']:.1f}")
            print(f"     Interpretation: {readability['interpretation']}")
            print(f"     {readability['explanation']}")
            
            # Clarity Details
            clarity = components['clarity']
            print(f"\n  ✨ CLARITY: {clarity['score']:.1f}/100")
            if 'analysis' in clarity and clarity['analysis']:
                analysis = clarity['analysis']
                print(f"     Avg Sentence Length: {analysis.get('avg_sentence_length', 0):.1f} words")
                print(f"     Passive Voice: {analysis.get('passive_voice_ratio', 0)*100:.1f}%")
                print(f"     Filler Words: {analysis.get('filler_word_ratio', 0)*100:.1f}%")
            print(f"     {clarity['explanation']}")
            
            # Section-specific recommendations
            if section_data.get('recommendations'):
                print(f"\n  💡 Recommendations:")
                for rec in section_data['recommendations'][:3]:  # Top 3
                    print(f"     [{rec['priority'].upper()}] {rec['issue']}")
                    print(f"     → {rec['suggestion']}")
    
    def _display_component_details(self, results: dict):
        """Display deep dive into each component."""
        global_analysis = results['global_analysis']
        components = global_analysis['components']
        
        # Grammar Deep Dive
        print("\n📖 GRAMMAR ANALYSIS")
        print("-" * 80)
        grammar = components['grammar']
        print(f"Score: {grammar['score']:.2f}/100")
        print(f"Issues Detected: {grammar['total_issues']}")
        print(f"Explanation: {grammar['explanation']}")
        
        if grammar.get('issue_breakdown'):
            print("\nIssue Breakdown:")
            for issue_type, count in grammar['issue_breakdown'].items():
                print(f"  • {issue_type.capitalize()}: {count}")
        
        # Readability Deep Dive
        print("\n\n📊 READABILITY ANALYSIS")
        print("-" * 80)
        readability = components['readability']
        print(f"Score: {readability['score']:.2f}/100")
        print(f"Flesch Reading Ease: {readability['flesch_reading_ease']:.2f}")
        print(f"Interpretation: {readability['interpretation']}")
        print(f"Explanation: {readability['explanation']}")
        
        # Clarity Deep Dive
        print("\n\n✨ CLARITY ANALYSIS")
        print("-" * 80)
        clarity = components['clarity']
        print(f"Score: {clarity['score']:.2f}/100")
        print(f"Explanation: {clarity['explanation']}")
        
        if 'analysis' in clarity and clarity['analysis']:
            analysis = clarity['analysis']
            print("\nDetailed Metrics:")
            print(f"  • Average Sentence Length: {analysis.get('avg_sentence_length', 0):.2f} words")
            print(f"  • Sentence Length Variance: {analysis.get('sentence_length_variance', 0):.2f}")
            print(f"  • Passive Voice Ratio: {analysis.get('passive_voice_ratio', 0)*100:.2f}%")
            print(f"  • Filler Word Ratio: {analysis.get('filler_word_ratio', 0)*100:.2f}%")
            print(f"  • Weak Verb Ratio: {analysis.get('weak_verb_ratio', 0)*100:.2f}%")
            print(f"  • Variety Score: {analysis.get('variety_score', 0):.2f}/100")
    
    def _display_recommendations(self, results: dict):
        """Display actionable recommendations."""
        global_analysis = results['global_analysis']
        recommendations = global_analysis.get('recommendations', [])
        
        if not recommendations:
            print("✓ No major issues detected. Language quality is excellent!")
            return
        
        print("\n💡 ACTIONABLE RECOMMENDATIONS")
        print("-" * 80)
        
        # Group by priority
        high_priority = [r for r in recommendations if r['priority'] == 'high']
        medium_priority = [r for r in recommendations if r['priority'] == 'medium']
        low_priority = [r for r in recommendations if r['priority'] == 'low']
        
        if high_priority:
            print("\n🔴 HIGH PRIORITY:")
            for i, rec in enumerate(high_priority, 1):
                print(f"\n  {i}. {rec['issue']}")
                print(f"     Category: {rec['category'].upper()}")
                print(f"     💡 Suggestion: {rec['suggestion']}")
        
        if medium_priority:
            print("\n🟡 MEDIUM PRIORITY:")
            for i, rec in enumerate(medium_priority, 1):
                print(f"\n  {i}. {rec['issue']}")
                print(f"     Category: {rec['category'].upper()}")
                print(f"     💡 Suggestion: {rec['suggestion']}")
        
        if low_priority:
            print("\n🟢 LOW PRIORITY:")
            for i, rec in enumerate(low_priority, 1):
                print(f"\n  {i}. {rec['issue']}")
                print(f"     Category: {rec['category'].upper()}")
                print(f"     💡 Suggestion: {rec['suggestion']}")
    
    def _save_results(self, resume_path: str, results: dict) -> str:
        """Save analysis results to JSON file."""
        # Create output directory if needed
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        resume_name = Path(resume_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{resume_name}_language_analysis_{timestamp}.json"
        output_path = output_dir / output_filename
        
        # Add metadata
        results['metadata'] = {
            'resume_file': str(resume_path),
            'analysis_date': datetime.now().isoformat(),
            'phase': 'Phase 5 - Grammar & Readability Intelligence'
        }
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def demonstrate_individual_components(self, sample_text: str):
        """
        Demonstrate each component individually with sample text.
        
        Args:
            sample_text: Sample text to analyze
        """
        print("\n" + "=" * 80)
        print("INDIVIDUAL COMPONENT DEMONSTRATION")
        print("=" * 80)
        print(f"\nSample Text:\n\"{sample_text}\"\n")
        
        # Grammar Check
        print("\n1️⃣ GRAMMAR CHECKER")
        print("-" * 80)
        grammar_result = self.grammar_checker.calculate_grammar_score(sample_text)
        print(f"Grammar Score: {grammar_result['score']:.2f}/100")
        print(f"Total Issues: {grammar_result.get('total_issues', 0)}")
        print(f"Explanation: {grammar_result['explanation']}")
        
        # Readability Analysis
        print("\n\n2️⃣ READABILITY ANALYZER")
        print("-" * 80)
        readability_result = self.readability_analyzer.calculate_readability_score(sample_text)
        print(f"Readability Score: {readability_result['score']:.2f}/100")
        print(f"Flesch Reading Ease: {readability_result['flesch_reading_ease']:.2f}")
        print(f"Interpretation: {readability_result['interpretation']}")
        print(f"Explanation: {readability_result['explanation']}")
        
        # Clarity Analysis
        print("\n\n3️⃣ CLARITY SCORER")
        print("-" * 80)
        clarity_result = self.clarity_scorer.calculate_clarity_score(sample_text)
        print(f"Clarity Score: {clarity_result['score']:.2f}/100")
        print(f"Explanation: {clarity_result['explanation']}")
        
        if 'analysis' in clarity_result and clarity_result['analysis']:
            analysis = clarity_result['analysis']
            print(f"\nMetrics:")
            print(f"  • Passive Voice: {analysis.get('passive_voice_ratio', 0)*100:.1f}%")
            print(f"  • Filler Words: {analysis.get('filler_word_ratio', 0)*100:.1f}%")
            print(f"  • Sentence Variety: {analysis.get('variety_score', 0):.1f}/100")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Phase 5: Grammar & Readability Intelligence Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python grammar_readability.py
  python grammar_readability.py --resume data/sample_resumes/sample_resume.pdf
  python grammar_readability.py --resume my_resume.pdf --detailed
  python grammar_readability.py --demo
        """
    )
    
    parser.add_argument(
        '--resume',
        type=str,
        help='Path to resume PDF/DOCX file'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed component analysis'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run component demonstration with sample text'
    )
    
    parser.add_argument(
        '--use-language-tool',
        action='store_true',
        help='Enable LanguageTool (requires Java runtime)'
    )
    
    args = parser.parse_args()
    
    # Initialize demo
    demo = GrammarReadabilityDemo(use_language_tool=args.use_language_tool)
    
    # Component demonstration mode
    if args.demo:
        sample_text = (
            "Experienced software engineer with strong background in backend development. "
            "The system was built using Python and FastAPI. "
            "Really good at designing scalable architectures. "
            "Performance improvements were achieved through optimization."
        )
        demo.demonstrate_individual_components(sample_text)
        return
    
    # Determine resume path
    if args.resume:
        resume_path = args.resume
    else:
        # Try to find sample resume
        possible_paths = [
            'data/sample_resumes/sample_resume.pdf',
            'data/sample_resume/sample_resume.pdf',
            'sample_resume.pdf'
        ]
        
        resume_path = None
        for path in possible_paths:
            if os.path.exists(path):
                resume_path = path
                break
        
        if not resume_path:
            print("❌ Error: No resume file specified and no sample resume found.")
            print("\nUsage:")
            print("  python grammar_readability.py --resume path/to/resume.pdf")
            print("\nOr place a sample resume at:")
            print("  data/sample_resumes/sample_resume.pdf")
            sys.exit(1)
    
    # Validate file exists
    if not os.path.exists(resume_path):
        print(f"❌ Error: Resume file not found: {resume_path}")
        sys.exit(1)
    
    # Run analysis
    try:
        results = demo.run_complete_analysis(resume_path, detailed=args.detailed)
        
        if results:
            print("\n" + "=" * 80)
            print("✅ ANALYSIS COMPLETE")
            print("=" * 80)
            print(f"\n🎯 Final Language Quality Score: {results['summary']['overall_score']:.2f}/100")
            print(f"   Grade: {results['summary']['grade']}")
            
            # Quick tips
            print("\n📌 Quick Tips:")
            if results['summary']['overall_score'] >= 85:
                print("   • Excellent work! Your resume demonstrates professional language quality.")
            elif results['summary']['overall_score'] >= 70:
                print("   • Good foundation. Review recommendations for final polish.")
            else:
                print("   • Focus on high-priority recommendations for maximum impact.")
            
            print("\n   Run with --detailed flag for comprehensive section analysis.")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()