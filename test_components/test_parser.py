"""
Example: Parse a resume file
"""

import sys
from pathlib import Path
import json

# ✅ Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.parser.resume_parser import ResumeParser


def main():
    parser = ResumeParser()

    resume_path = PROJECT_ROOT / "data/sample_resume/Tamal Bhattacharjee.pdf"
    resume_data = parser.parse(str(resume_path))

    print("=" * 60)
    print("RESUME PARSING RESULTS")
    print("=" * 60)

    print(f"\n📄 File: {resume_data.metadata.file_name}")
    print(f"⏱️  Parsing time: {resume_data.metadata.parsing_time_ms:.2f}ms")
    print(f"📊 Confidence: {resume_data.metadata.parsing_confidence:.2%}")

    print(f"\n👤 Contact:")
    print(f"   Name: {resume_data.contact.name}")
    print(f"   Email: {resume_data.contact.email}")
    print(f"   Phone: {resume_data.contact.phone}")

    print(f"\n📝 Summary:")
    print(f"   {resume_data.summary}")

    print(f"\n🛠️  Skills ({len(resume_data.skills)}):")
    for skill in resume_data.skills[:10]:
        print(f"   • {skill}")

    print(f"\n📑 Sections detected:")
    for section_name in resume_data.get_all_section_names():
        print(f"   • {section_name.title()}")

    output_path = PROJECT_ROOT / "data/output/parsed_resume.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(resume_data.to_dict(), f, indent=2)

    print(f"\n💾 Full output saved to: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
