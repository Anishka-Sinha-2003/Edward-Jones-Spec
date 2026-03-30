"""API-layer exceptions with machine-readable error codes (spec 2603-002)."""


class APIError(Exception):
    """Base API error with HTTP status and error code."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class PDFProcessingError(APIError):
    """Base class for PDF upload / parse failures."""

    pass


class FileTooLargeError(PDFProcessingError):
    """Uploaded file exceeds size limit."""

    def __init__(self, code: str = "PDF_TOO_LARGE", message: str = "") -> None:
        super().__init__(
            code,
            message or "PDF exceeds maximum allowed size (50MB)",
            status_code=413,
        )


class PDFValidationError(PDFProcessingError):
    """File is missing, wrong type, or not a valid PDF."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
    ) -> None:
        super().__init__(code, message, status_code)


class PDFParsingError(PDFProcessingError):
    """pdfplumber failed to read the document."""

    def __init__(self, message: str) -> None:
        super().__init__("PDF_PARSING_ERROR", message, status_code=500)


class DetectorRuntimeError(APIError):
    """Detector raised an unexpected error."""

    def __init__(self, message: str) -> None:
        super().__init__("DETECTOR_ERROR", message, status_code=500)


class DetectionTimeoutError(APIError):
    """Detection exceeded time limit."""

    def __init__(self) -> None:
        super().__init__(
            "DETECTION_TIMEOUT",
            "Detection exceeded time limit (5 seconds)",
            status_code=408,
        )
