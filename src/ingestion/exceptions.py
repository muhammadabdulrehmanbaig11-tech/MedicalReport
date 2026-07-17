"""
Exceptions for the ingestion module.
"""

class DocumentProcessingError(Exception):
    """Base exception for document processing errors."""
    pass

class InvalidFileTypeError(DocumentProcessingError):
    """Raised when the file type or extension is invalid."""
    pass

class OversizedFileError(DocumentProcessingError):
    """Raised when the file exceeds the maximum allowed size."""
    pass

class EmptyFileError(DocumentProcessingError):
    """Raised when the file is empty (0 bytes)."""
    pass

class CorruptPDFError(DocumentProcessingError):
    """Raised when the PDF cannot be opened or has an invalid signature."""
    pass

class TooManyPagesError(DocumentProcessingError):
    """Raised when the PDF exceeds the maximum allowed page count."""
    pass

class PasswordProtectedPDFError(DocumentProcessingError):
    """Raised when the PDF requires a password to open."""
    pass

class NoMeaningfulTextError(DocumentProcessingError):
    """Raised when the PDF does not contain enough extractable text (e.g., scanned or image-only)."""
    pass
