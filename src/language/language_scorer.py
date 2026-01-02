from typing import Dict
import logging

from src.language.grammar_checker import GrammarChecker
from src.language.readability_analyzer import ReadabilityAnalyzer
from src.language.clarity_scorer import ClarityScorer

logger = logging.getLogger(__name__)


class LanguageScorer:
    """
    Main language quality scorer.
    Combines grammar, readability, and clarity analysis.
    """

    def __init__(self, use_language_tool: bool = True):
        self.grammar_checker = GrammarChecker(use_language_tool=use_language_tool)
        self.readability_analyzer = ReadabilityAnalyzer()
        self.clarity_scorer = ClarityScorer()

        logger.info("Language scorer initialized")

    # ------------------------------------------------------------------
    # Section-level scoring
    # ------------------------------------------------------------------

    def score_text(self, text: str, section_name: str = "unknown") -> Dict:
        if not text or len(text.strip()) < 10:
            return self._empty_result(section_name)

        grammar_result = self.grammar_checker.calculate_grammar_score(text)
        readability_result = self.readability_analyzer.calculate_readability_score(text)
        clarity_result = self.clarity_scorer.calculate_clarity_score(text)

        total_score = (
            grammar_result["score"] * 0.40 +
            readability_result["score"] * 0.30 +
            clarity_result["score"] * 0.30
        )

        return {
            "section": section_name,
            "language_quality_score": round(total_score, 2),
            "components": {
                "grammar": {
                    "score": grammar_result["score"],
                    "total_issues": grammar_result.get("total_issues", 0),
                    "issue_breakdown": grammar_result.get("issue_breakdown", {}),
                    "explanation": grammar_result["explanation"],
                },
                "readability": {
                    "score": readability_result["score"],
                    "flesch_reading_ease": readability_result["flesch_reading_ease"],
                    "interpretation": readability_result["interpretation"],
                    "explanation": readability_result["explanation"],
                },
                "clarity": {
                    "score": clarity_result["score"],
                    "analysis": clarity_result["analysis"],
                    "explanation": clarity_result["explanation"],
                },
            },
            "recommendations": self._generate_recommendations(
                grammar_result, readability_result, clarity_result
            ),
            "overall_assessment": self._generate_assessment(total_score),
        }

    # ------------------------------------------------------------------
    # Resume-level scoring (FIXED)
    # ------------------------------------------------------------------

    def score_resume_sections(self, parsed_resume) -> Dict:
        """
        parsed_resume is a ResumeData object (NOT a dict)
        """
        section_scores = {}
        total_text = ""

        sections_to_analyze = ["summary", "experience", "projects", "education"]

        for section in sections_to_analyze:
            section_obj = parsed_resume.sections.get(section)

            if not section_obj or not hasattr(section_obj, "content"):
                continue

            section_text = section_obj.content.strip()
            if len(section_text) < 10:
                continue

            section_scores[section] = self.score_text(section_text, section)
            total_text += " " + section_text

        # Overall resume language score
        if total_text.strip():
            overall_score_data = self.score_text(total_text, "overall_resume")
        else:
            overall_score_data = self._empty_result("overall_resume")

        # Weighted aggregation
        section_weights = {
            "summary": 0.25,
            "experience": 0.40,
            "projects": 0.20,
            "education": 0.15,
        }

        weighted_score = 0.0
        total_weight = 0.0

        for section, weight in section_weights.items():
            if section in section_scores:
                weighted_score += section_scores[section]["language_quality_score"] * weight
                total_weight += weight

        final_score = (
            weighted_score / total_weight
            if total_weight > 0
            else overall_score_data["language_quality_score"]
        )

        return {
            "overall_language_score": round(final_score, 2),
            "section_scores": section_scores,
            "global_analysis": overall_score_data,
            "summary": self._generate_summary(final_score, section_scores),
        }

    # ------------------------------------------------------------------
    # Recommendation & summary helpers
    # ------------------------------------------------------------------

    def _generate_recommendations(
        self, grammar_result: Dict, readability_result: Dict, clarity_result: Dict
    ) -> list:
        recommendations = []

        if grammar_result["score"] < 80:
            recommendations.append({
                "category": "grammar",
                "priority": "high",
                "issue": f"{grammar_result.get('total_issues', 0)} grammar issues detected",
                "suggestion": "Review spelling and grammar using a proofreading tool",
            })

        flesch = readability_result["flesch_reading_ease"]
        if flesch < 50:
            recommendations.append({
                "category": "readability",
                "priority": "medium",
                "issue": "Text is difficult to scan quickly",
                "suggestion": "Use shorter sentences and simpler wording",
            })

        clarity = clarity_result["analysis"]
        if clarity.get("passive_voice_ratio", 0) > 0.25:
            recommendations.append({
                "category": "clarity",
                "priority": "medium",
                "issue": "High passive voice usage",
                "suggestion": "Prefer active voice (e.g., 'Led', 'Built', 'Designed')",
            })

        return recommendations

    def _generate_assessment(self, score: float) -> str:
        if score >= 90:
            return "Exceptional language quality. Professional and clear."
        elif score >= 80:
            return "Excellent language quality with minor refinements needed."
        elif score >= 70:
            return "Good language quality. Some improvements recommended."
        elif score >= 60:
            return "Acceptable language quality. Review highlighted issues."
        else:
            return "Language quality needs significant improvement."

    def _generate_summary(self, overall_score: float, section_scores: Dict) -> Dict:
        if section_scores:
            sorted_sections = sorted(
                section_scores.items(),
                key=lambda x: x[1]["language_quality_score"],
                reverse=True,
            )
            strongest = sorted_sections[0][0]
            weakest = sorted_sections[-1][0]
        else:
            strongest = weakest = None

        return {
            "overall_score": overall_score,
            "grade": self._score_to_grade(overall_score),
            "strongest_section": strongest,
            "weakest_section": weakest,
            "sections_analyzed": len(section_scores),
            "assessment": self._generate_assessment(overall_score),
        }

    def _score_to_grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        return "F"

    def _empty_result(self, section_name: str) -> Dict:
        return {
            "section": section_name,
            "language_quality_score": 100.0,
            "components": {},
            "recommendations": [],
            "overall_assessment": "Insufficient text for analysis",
        }
