"""Extract and segment exam questions from PDF documents."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd
import pdfplumber

from src.preprocessing.ocr_extractor import extract_text_with_ocr
from src.preprocessing.text_cleaner import fix_spacing
from src.utils import PROCESSED_DIR, setup_logging

logger = setup_logging(__name__)

QUESTION_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:"
    r"(?:Q(?:uestion)?\.?\s*)?(?P<num>\d{1,3})[\.\):]\s*)"
    r"(?P<text>.+?)"
    r"(?=(?:\n\s*(?:Q(?:uestion)?\.?\s*)?\d{1,3}[\.\):])|\Z)",
    re.DOTALL | re.IGNORECASE,
)
MARKS_PATTERN = re.compile(
    r"\((\d{1,3})\s*(?:marks?|pts?|points?)\)",
    re.IGNORECASE,
)
HEADER_FOOTER_PATTERN = re.compile(
    r"(page\s+\d+|exam\s+paper|university|department|faculty|"
    r"confidential|instructions|time allowed|total marks)",
    re.IGNORECASE,
)
PAGE_NUMBER_PATTERN = re.compile(r"^\s*\d{1,4}\s*$", re.MULTILINE)


class PDFExtractor:
    """Extract exam questions from PDF files and persist them as CSV."""

    def __init__(self, output_dir: Path | None = None) -> None:
        """Initialize the PDF extractor.

        Args:
            output_dir: Directory for processed CSV output.
        """
        self.output_dir = output_dir or PROCESSED_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._last_used_ocr: bool = False

    @property
    def last_used_ocr(self) -> bool:
        """True if the most recent extraction used OCR (scanned PDF)."""
        return self._last_used_ocr

    def extract_text_from_pdf(self, pdf_path: Path, use_ocr: bool = True) -> str:
        """Extract raw text from a PDF file, falling back to OCR if needed.

        First attempts fast pdfplumber text extraction.  If the result is too
        short (image-based / scanned PDF), and ``use_ocr`` is True, falls back
        to EasyOCR page-by-page scanning.

        Args:
            pdf_path: Path to the PDF file.
            use_ocr: Allow OCR fallback for scanned PDFs.

        Returns:
            Extracted text content.

        Raises:
            ValueError: If text cannot be extracted even with OCR.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        self._last_used_ocr = False
        text_parts: list[str] = []
        pdfplumber_ok = True

        try:
            with pdfplumber.open(pdf_path) as pdf:
                if not pdf.pages:
                    raise ValueError("PDF contains no pages.")
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_parts.append(page_text)
        except Exception as exc:
            logger.warning(
                "pdfplumber could not read '%s': %s — will try OCR", pdf_path.name, exc
            )
            pdfplumber_ok = False

        combined = "\n".join(text_parts).strip()

        if len(combined) >= 20:
            return combined

        # Insufficient text — this is a scanned / image-based PDF
        if not use_ocr:
            raise ValueError(
                f"PDF '{pdf_path.name}' appears to be image-based and OCR is disabled."
            )

        logger.info(
            "pdfplumber extracted only %d chars from '%s' — switching to OCR",
            len(combined),
            pdf_path.name,
        )
        ocr_text = extract_text_with_ocr(pdf_path)
        self._last_used_ocr = True
        return ocr_text

    def clean_text(self, text: str) -> str:
        """Remove headers, footers, and page numbers from extracted text.

        Args:
            text: Raw extracted text.

        Returns:
            Cleaned text.
        """
        cleaned = PAGE_NUMBER_PATTERN.sub("", text)
        lines = []
        for line in cleaned.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if HEADER_FOOTER_PATTERN.search(stripped) and len(stripped.split()) <= 8:
                continue
            lines.append(stripped)
        return fix_spacing("\n".join(lines))

    def segment_questions(self, text: str) -> list[dict[str, Any]]:
        """Segment cleaned text into individual questions.

        Args:
            text: Cleaned exam paper text.

        Returns:
            List of question dictionaries with text and optional marks.
        """
        questions: list[dict[str, Any]] = []
        matches = list(QUESTION_PATTERN.finditer(text))

        if not matches:
            fallback_blocks = [
                block.strip()
                for block in re.split(r"\?\s*(?=\n|$)", text)
                if block.strip()
            ]
            for idx, block in enumerate(fallback_blocks, start=1):
                question_text = block if block.endswith("?") else f"{block}?"
                questions.append(
                    {
                        "question_id": f"Q{idx}",
                        "question_text": question_text.strip(),
                        "marks": self._extract_marks(question_text),
                    }
                )
            return questions

        for match in matches:
            question_num = match.group("num")
            question_text = match.group("text").strip()
            question_text = re.sub(r"\s+", " ", question_text)
            if len(question_text) < 10:
                continue
            questions.append(
                {
                    "question_id": f"Q{question_num}",
                    "question_text": question_text,
                    "marks": self._extract_marks(question_text),
                }
            )
        return questions

    def _extract_marks(self, text: str) -> int | None:
        """Extract marks allocation from question text.

        Args:
            text: Question text.

        Returns:
            Marks value if found, otherwise None.
        """
        match = MARKS_PATTERN.search(text)
        if match:
            return int(match.group(1))
        return None

    def process_pdf(
        self,
        pdf_path: Path,
        subject: str,
        year: int,
        use_ocr: bool = True,
    ) -> pd.DataFrame:
        """Extract, clean, segment, and structure questions from a PDF.

        Args:
            pdf_path: Path to uploaded PDF.
            subject: Subject name for the exam paper.
            year: Exam year.
            use_ocr: Allow OCR fallback for scanned/image-based PDFs.

        Returns:
            DataFrame with question records.  Includes an ``extraction_method``
            column ("text" for direct extraction, "ocr" for scanned PDFs).
        """
        raw_text = self.extract_text_from_pdf(pdf_path, use_ocr=use_ocr)
        cleaned_text = self.clean_text(raw_text)
        segmented = self.segment_questions(cleaned_text)

        if not segmented:
            raise ValueError(
                f"No questions detected in '{pdf_path.name}'. "
                "Try a text-based PDF with numbered questions."
            )

        extraction_method = "ocr" if self._last_used_ocr else "text"
        records = []
        for idx, item in enumerate(segmented, start=1):
            records.append(
                {
                    "question_id": item.get("question_id") or f"Q{idx}",
                    "question_text": item["question_text"],
                    "year": year,
                    "subject": subject,
                    "marks": item.get("marks"),
                    "source_file": pdf_path.name,
                    "extraction_method": extraction_method,
                }
            )
        return pd.DataFrame(records)

    def save_questions(
        self,
        df: pd.DataFrame,
        filename: str = "extracted_questions.csv",
    ) -> Path:
        """Save extracted questions to CSV.

        Args:
            df: Question dataframe.
            filename: Output filename.

        Returns:
            Path to saved CSV file.
        """
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        logger.info("Saved %s questions to %s", len(df), output_path)
        return output_path

    def process_and_save(
        self,
        pdf_path: Path,
        subject: str,
        year: int,
        filename: str = "extracted_questions.csv",
        append: bool = True,
    ) -> pd.DataFrame:
        """Process a PDF and optionally append results to existing CSV.

        Args:
            pdf_path: PDF file path.
            subject: Subject label.
            year: Exam year.
            filename: CSV filename.
            append: Whether to append to existing processed data.

        Returns:
            Combined dataframe after save.
        """
        new_df = self.process_pdf(pdf_path, subject=subject, year=year)
        output_path = self.output_dir / filename

        if append and output_path.exists():
            existing = pd.read_csv(output_path)
            combined = pd.concat([existing, new_df], ignore_index=True)
        else:
            combined = new_df

        combined.drop_duplicates(
            subset=["question_text", "year", "subject"],
            keep="last",
            inplace=True,
        )
        combined.to_csv(output_path, index=False)
        return combined

    def process_subject_pdf(
        self, pdf_path: Path, subject: str, use_ocr: bool = True
    ) -> pd.DataFrame:
        """Extract reference text from a subject/syllabus PDF.

        Args:
            pdf_path: Path to subject material PDF.
            subject: User-defined subject name (any discipline).
            use_ocr: Allow OCR fallback for scanned PDFs.

        Returns:
            DataFrame with subject reference content.
        """
        raw_text = self.extract_text_from_pdf(pdf_path, use_ocr=use_ocr)
        cleaned_text = self.clean_text(raw_text)
        return pd.DataFrame(
            [
                {
                    "subject": subject.strip(),
                    "source_file": pdf_path.name,
                    "content_text": cleaned_text,
                    "extraction_method": "ocr" if self._last_used_ocr else "text",
                }
            ]
        )
