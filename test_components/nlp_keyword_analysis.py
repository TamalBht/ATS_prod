"""
Example: NLP-based keyword analysis
Usage: python examples/nlp_keyword_analysis.py [resume_path]
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser.resume_parser import ResumeParser
from src.nlp.keyword_analyzer import KeywordAnalyzer
from src.nlp.text_vectorizer import TextVectorizer


def print_header(title, char="="):
    """Print formatted header."""
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}")


def main():
    """Main NLP analysis demo."""
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]
    else:
        sample_dir = Path("data/sample_resumes")
        if sample_dir.exists():
            resumes = list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.pdf"))
            if resumes:
                resume_path = str(resumes[0])
            else:
                print("❌ No sample resumes found")
                return 1
        else:
            print("❌ No resume file specified")
            return 1
    
    print_header("🧠 NLP KEYWORD ANALYSIS - PHASE 4 DEMO")
    print(f"\n📂 Analyzing: {resume_path}")
    
    try:
        # Parse resume
        print("\n⏳ Step 1/3: Parsing resume...")
        parser = ResumeParser()
        resume_data = parser.parse(resume_path)
        print(f"✓ Parsed ({resume_data.metadata.parsing_time_ms:.1f}ms)")
        
        # Initialize analyzers
        print("\n⏳ Step 2/3: Initializing NLP analyzers...")
        vectorizer = TextVectorizer()
        analyzer = KeywordAnalyzer()
        print("✓ Analyzers ready")
        
        # Extract TF-IDF keywords
        print("\n⏳ Step 3/3: Analyzing keywords...")
        tfidf_keywords = vectorizer.extract_keywords_tfidf(resume_data.raw_text, top_n=20)
        
        # Target keywords for demonstration
        target_keywords = [
            "Python", "JavaScript", "machine learning", "API", "database",
            "cloud", "Docker", "leadership", "team", "agile"
        ]
        
        # Comprehensive analysis
        analysis = analyzer.analyze_keywords(resume_data, target_keywords)
        
        # Display TF-IDF results
        print_header("📊 TF-IDF KEYWORD EXTRACTION")
        print("\n  Top 20 Keywords by Importance:")
        for i, (keyword, score) in enumerate(tfidf_keywords, 1):
            bar_length = int(score * 50)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"  {i:2}. {keyword:25} [{bar}] {score:.3f}")
        
        # Display direct matches
        if analysis['direct_matches']:
            print_header("✅ DIRECT KEYWORD MATCHES")
            for keyword, count in analysis['direct_matches'].items():
                print(f"  • {keyword}: {count} occurrence(s)")
        else:
            print_header("⚠️  NO DIRECT MATCHES")
            print("  None of the target keywords found in resume")
        
        # Display density analysis
        print_header("📈 KEYWORD DENSITY ANALYSIS")
        density = analysis['density_analysis']
        print(f"\n  Keyword Density: {density['density']:.2f} keywords per 100 words")
        print(f"  Optimal Range: {density['optimal_range'][0]:.1f} - {density['optimal_range'][1]:.1f}")
        print(f"  Maximum Allowed: {density['max_allowed']:.1f}")
        
        if density['is_optimal']:
            print("  ✓ STATUS: Optimal keyword density")
        elif density['is_stuffed']:
            print("  ✗ WARNING: Possible keyword stuffing detected")
        else:
            print("  ⚠ STATUS: Below optimal density")
        
        # Display context scores
        if analysis['context_scores']:
            print_header("🎯 KEYWORD CONTEXT ANALYSIS")
            print("\n  Context quality (keywords in meaningful sentences):")
            for keyword, score in sorted(analysis['context_scores'].items(), 
                                        key=lambda x: x[1], reverse=True):
                quality = "Excellent" if score > 0.8 else "Good" if score > 0.6 else "Fair"
                print(f"  • {keyword:20} {score:.2f} ({quality})")
        
        # Display semantic matches (if available)
        if analysis['semantic_matches']:
            print_header("🔗 SEMANTIC MATCHES")
            print("\n  Similar terms found in resume:")
            for target_kw, matches in list(analysis['semantic_matches'].items())[:5]:
                print(f"\n  Target: '{target_kw}'")
                for matched_term, similarity in matches[:3]:
                    print(f"    → '{matched_term}' (similarity: {similarity:.2f})")
        
        # Display overall quality
        print_header("⭐ OVERALL KEYWORD QUALITY")
        quality_score = analysis['quality_score']
        percentage = quality_score * 100
        
        bar_length = int(quality_score * 50)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"\n  Quality Score: [{bar}] {percentage:.1f}%")
        
        if percentage >= 80:
            print("  ✓ Excellent keyword optimization")
        elif percentage >= 60:
            print("  ✓ Good keyword usage")
        elif percentage >= 40:
            print("  ⚠ Moderate keyword optimization")
        else:
            print("  ✗ Needs improvement")
        
        # Recommendations
        print_header("💡 RECOMMENDATIONS")
        
        if density['is_stuffed']:
            print("  1. Reduce keyword repetition - may appear as spam")
        elif density['density'] < 1.0:
            print("  1. Add more relevant keywords naturally in context")
        
        missing_keywords = [kw for kw in target_keywords 
                          if kw not in analysis['direct_matches']]
        if missing_keywords:
            print(f"  2. Consider adding: {', '.join(missing_keywords[:5])}")
        
        low_context = [kw for kw, score in analysis['context_scores'].items() 
                      if score < 0.6]
        if low_context:
            print(f"  3. Use these keywords in action sentences: {', '.join(low_context[:3])}")
        
        # Save detailed results
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{Path(resume_path).stem}_nlp_analysis.json"
        
        # Prepare serializable output
        output_data = {
            'tfidf_keywords': [(kw, float(score)) for kw, score in tfidf_keywords],
            'direct_matches': analysis['direct_matches'],
            'density_analysis': analysis['density_analysis'],
            'context_scores': analysis['context_scores'],
            'quality_score': float(quality_score)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print_header("💾 ANALYSIS SAVED")
        print(f"\n  Detailed report: {output_file}")
        
        print("\n" + "=" * 70)
        print("  ✅ NLP keyword analysis complete!")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())