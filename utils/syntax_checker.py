from __future__ import annotations

import ast
import logging
from typing import Dict


logger = logging.getLogger(__name__)


class SyntaxChecker:
    """Performs lightweight syntax validation before deeper review."""

    def check_python(self, code: str) -> Dict:
        """Use AST to verify Python syntax without execution."""

        try:
            ast.parse(code or "")
            return {"valid": True, "error": None}
        except SyntaxError as exc:
            logger.error("Syntax Error detected: %s at line %s", exc.msg, exc.lineno)
            return {"valid": False, "error": exc.msg, "line": exc.lineno}

    def check(self, code: str, language: str) -> Dict:
        """Route to language-specific checkers."""

        if language.lower() == "python":
            return self.check_python(code)
        return {"valid": True, "error": None}
