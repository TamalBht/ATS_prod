"""
ATS Structural Compatibility Validator - Phase 6.
Detects layout and formatting issues that break ATS parsing.
"""
import re
from pathlib import Path
from typing import List, Tuple, Optional
import logging

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from src.models.structural_models import (
    StructuralAnalysis,
    StructuralIssue,
    IssueSeverity,
    IssueCategory
)


logger = logging.getLogger(__name__)


class StructuralValidator:
    """
    Validates resume structure for ATS compatibility.
    Uses deterministic rule-based detection.
    """
    
    # Penalty configuration (can be overridden from config.yaml)
    PENALTIES = {
        "multi_column_layout": 25,
        "table_with_merged_cells": 20,
        "simple_table": 10,
        "text_boxes": 15,
        "images": 12,
        "icons": 8,
        "header_footer": 5,
        "special_unicode": 3,
        "complex_formatting": 10
    }
    
    # Character ranges that commonly break ATS systems
    PROBLEMATIC_UNICODE_RANGES = [
        (0x2190, 0x21FF),  # Arrows
        (0x2600, 0x26FF),  # Miscellaneous Symbols
        (0x2700, 0x27BF),  # Dingbats
        (0x1F300, 0x1F9FF),  # Emojis
    ]
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize validator with optional configuration.
        
        Args:
            config: Optional penalty configuration override
        """
        if config and "structural_penalties" in config:
            self.PENALTIES.update(config["structural_penalties"])
        
        if fitz is None:
            logger.warning("PyMuPDF not installed. Structural validation will be limited.")
    
    def validate(self, pdf_path: str) -> StructuralAnalysis:
        """
        Perform complete structural validation on a PDF resume.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            StructuralAnalysis with detected issues and penalties
        """
        analysis = StructuralAnalysis()
        
        if not Path(pdf_path).exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return analysis
        
        if fitz is None:
            logger.warning("Structural validation skipped: PyMuPDF not available")
            return analysis
        
        try:
            doc = fitz.open(pdf_path)
            analysis.num_pages = len(doc)
            
            # Run all detection methods
            self._detect_multi_column_layout(doc, analysis)
            self._detect_tables(doc, analysis)
            self._detect_images(doc, analysis)
            self._detect_text_boxes(doc, analysis)
            self._detect_headers_footers(doc, analysis)
            self._detect_special_characters(doc, analysis)
            
            doc.close()
            
            # Calculate final score
            analysis.total_penalty = sum(issue.penalty for issue in analysis.issues)
            analysis.final_score = max(0, analysis.base_score - analysis.total_penalty)
            analysis.is_ats_friendly = analysis.final_score >= 70
            
        except Exception as e:
            logger.error(f"Error during structural validation: {e}")
        
        return analysis
    
    def _detect_multi_column_layout(self, doc: "fitz.Document", analysis: StructuralAnalysis) -> None:
        """Detect multi-column layouts by analyzing text block positions."""
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            text_blocks = [b for b in blocks if b["type"] == 0]  # Text blocks only
            
            if len(text_blocks) < 2:
                continue
            
            # Group blocks by vertical position (y-coordinate)
            y_positions = {}
            for block in text_blocks:
                y = int(block["bbox"][1] / 10) * 10  # Round to nearest 10
                if y not in y_positions:
                    y_positions[y] = []
                y_positions[y].append(block["bbox"][0])  # x-coordinate
            
            # Check if any horizontal level has multiple distinct x-positions
            for y, x_coords in y_positions.items():
                if len(x_coords) >= 2:
                    x_sorted = sorted(x_coords)
                    # If blocks are sufficiently separated horizontally
                    if x_sorted[-1] - x_sorted[0] > page.rect.width * 0.4:
                        analysis.has_multi_column = True
                        analysis.num_columns_detected = max(analysis.num_columns_detected, 2)
                        
                        issue = StructuralIssue(
                            category=IssueCategory.LAYOUT,
                            severity=IssueSeverity.CRITICAL,
                            description="Multi-column layout detected",
                            location=f"Page {page_num + 1}",
                            penalty=self.PENALTIES["multi_column_layout"],
                            recommendation="Use single-column layout for maximum ATS compatibility",
                            detected_elements=[f"Columns detected on page {page_num + 1}"]
                        )
                        analysis.issues.append(issue)
                        return  # Only report once
    
    def _detect_tables(self, doc: "fitz.Document", analysis: StructuralAnalysis) -> None:
        """Detect tables by analyzing line drawings and cell structures."""
        for page_num, page in enumerate(doc):
            # Get all drawings (lines, rectangles)
            drawings = page.get_drawings()
            
            # Count horizontal and vertical lines
            h_lines = []
            v_lines = []
            
            for drawing in drawings:
                for item in drawing["items"]:
                    if item[0] == "l":  # Line
                        p1, p2 = item[1], item[2]
                        if abs(p1.y - p2.y) < 2:  # Horizontal line
                            h_lines.append((p1, p2))
                        elif abs(p1.x - p2.x) < 2:  # Vertical line
                            v_lines.append((p1, p2))
            
            # If we have both h and v lines, likely a table
            if len(h_lines) >= 2 and len(v_lines) >= 2:
                analysis.has_tables = True
                analysis.num_tables += 1
                
                # Determine if table has merged cells (complex structure)
                is_complex = len(h_lines) > 5 or len(v_lines) > 5
                
                penalty = (self.PENALTIES["table_with_merged_cells"] if is_complex 
                          else self.PENALTIES["simple_table"])
                
                issue = StructuralIssue(
                    category=IssueCategory.LAYOUT,
                    severity=IssueSeverity.CRITICAL if is_complex else IssueSeverity.MAJOR,
                    description=f"{'Complex' if is_complex else 'Simple'} table detected",
                    location=f"Page {page_num + 1}",
                    penalty=penalty,
                    recommendation="Replace tables with simple text sections using bullet points",
                    detected_elements=[f"Table with ~{len(h_lines)}x{len(v_lines)} cells"]
                )
                analysis.issues.append(issue)
    
    def _detect_images(self, doc: "fitz.Document", analysis: StructuralAnalysis) -> None:
        """Detect embedded images (photos, logos, icons)."""
        for page_num, page in enumerate(doc):
            images = page.get_images()
            
            if images:
                analysis.has_images = True
                analysis.num_images += len(images)
                
                # Classify by size
                for img in images:
                    xref = img[0]
                    try:
                        bbox = page.get_image_bbox(xref)
                        width = bbox.x1 - bbox.x0
                        height = bbox.y1 - bbox.y0
                        area = width * height
                        
                        # Small images are likely icons
                        is_icon = area < 2000  # pixels squared
                        
                        penalty = (self.PENALTIES["icons"] if is_icon 
                                  else self.PENALTIES["images"])
                        
                        issue = StructuralIssue(
                            category=IssueCategory.CONTENT,
                            severity=IssueSeverity.MINOR if is_icon else IssueSeverity.MAJOR,
                            description=f"{'Icon' if is_icon else 'Image'} detected",
                            location=f"Page {page_num + 1}",
                            penalty=penalty,
                            recommendation="Remove images and icons; use text-only formatting",
                            detected_elements=[f"{width:.0f}x{height:.0f}px image"]
                        )
                        analysis.issues.append(issue)
                    except:
                        pass  # Skip if bbox extraction fails
    
    def _detect_text_boxes(self, doc: "fitz.Document", analysis: StructuralAnalysis) -> None:
        """Detect text boxes and floating text elements."""
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            
            # Look for blocks with unusual positioning or overlapping
            for i, block in enumerate(blocks):
                if block["type"] != 0:  # Only text blocks
                    continue
                
                bbox = block["bbox"]
                
                # Check if block overlaps with others (sign of text box)
                for other_block in blocks[i+1:]:
                    if other_block["type"] != 0:
                        continue
                    
                    other_bbox = other_block["bbox"]
                    
                    # Check for overlap
                    if (bbox[0] < other_bbox[2] and bbox[2] > other_bbox[0] and
                        bbox[1] < other_bbox[3] and bbox[3] > other_bbox[1]):
                        
                        analysis.has_text_boxes = True
                        
                        issue = StructuralIssue(
                            category=IssueCategory.FORMATTING,
                            severity=IssueSeverity.MAJOR,
                            description="Overlapping text boxes detected",
                            location=f"Page {page_num + 1}",
                            penalty=self.PENALTIES["text_boxes"],
                            recommendation="Use standard text flow without floating elements",
                            detected_elements=["Overlapping text elements"]
                        )
                        analysis.issues.append(issue)
                        return  # Only report once
    
    def _detect_headers_footers(self, doc: "fitz.Document", analysis: StructuralAnalysis) -> None:
        """Detect headers and footers that may confuse ATS."""
        if len(doc) < 2:
            return  # Need multiple pages to detect patterns
        
        # Get text from top and bottom of each page
        top_texts = []
        bottom_texts = []
        
        for page in doc:
            rect = page.rect
            
            # Top 10% of page
            top_area = fitz.Rect(0, 0, rect.width, rect.height * 0.1)
            top_text = page.get_text("text", clip=top_area).strip()
            top_texts.append(top_text)
            
            # Bottom 10% of page
            bottom_area = fitz.Rect(0, rect.height * 0.9, rect.width, rect.height)
            bottom_text = page.get_text("text", clip=bottom_area).strip()
            bottom_texts.append(bottom_text)
        
        # Check for repeated text (sign of header/footer)
        has_header = len(set(top_texts)) < len(top_texts) and any(top_texts)
        has_footer = len(set(bottom_texts)) < len(bottom_texts) and any(bottom_texts)
        
        if has_header or has_footer:
            analysis.has_headers_footers = True
            
            location = []
            if has_header:
                location.append("headers")
            if has_footer:
                location.append("footers")
            
            issue = StructuralIssue(
                category=IssueCategory.METADATA,
                severity=IssueSeverity.MINOR,
                description=f"Repeating {' and '.join(location)} detected",
                location="Multiple pages",
                penalty=self.PENALTIES["header_footer"],
                recommendation="Remove headers/footers or include info only on first page",
                detected_elements=location
            )
            analysis.issues.append(issue)
    
    def _detect_special_characters(self, doc: "fitz.Document", analysis: StructuralAnalysis) -> None:
        """Detect special Unicode characters that may break ATS parsing."""
        special_chars = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            
            for char in text:
                code_point = ord(char)
                
                # Check if in problematic range
                for start, end in self.PROBLEMATIC_UNICODE_RANGES:
                    if start <= code_point <= end:
                        special_chars.append(char)
                        analysis.special_char_count += 1
        
        if special_chars:
            analysis.has_special_chars = True
            
            # Only penalize if there are many special chars
            if len(special_chars) >= 5:
                unique_chars = list(set(special_chars))[:5]
                
                issue = StructuralIssue(
                    category=IssueCategory.CONTENT,
                    severity=IssueSeverity.MINOR,
                    description=f"Special characters detected ({len(special_chars)} instances)",
                    location="Throughout document",
                    penalty=self.PENALTIES["special_unicode"],
                    recommendation="Replace special characters with standard ASCII equivalents",
                    detected_elements=[f"Examples: {', '.join(unique_chars)}"]
                )
                analysis.issues.append(issue)