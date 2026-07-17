"""
MediLens AI - Configuration Module.
This is a placeholder for environment and application configuration.
"""

import os

# Configuration placeholders
DB_PATH = os.path.join("data", "medilens.db")
UPLOAD_DIR = "uploads"

# Phase 1: PDF Validation Constraints
MAX_PDF_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
MAX_PAGE_COUNT: int = 40
MIN_MEANINGFUL_TEXT_LENGTH: int = 30
ALLOWED_MIME_TYPE: str = "application/pdf"
ALLOWED_EXTENSION: str = ".pdf"
