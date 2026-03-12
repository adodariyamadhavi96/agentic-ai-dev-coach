import logging
import re
from typing import Dict, List


logger = logging.getLogger(__name__)

CODE_FENCE = re.compile(r"```(?P<lang>[\w\+\#\-\.]*)\n(?P<code>.*?)```", re.DOTALL)


def extract_code_blocks(text: str) -> List[str]:
    """Return raw code blocks from markdown text (legacy helper)."""
    return [match.strip() for match in re.findall(r"```(.*?)```", text, re.DOTALL)]


class CodeExtractor:
    """Parses LLM responses into code, language, deps, and explanation."""

    def extract_code(self, text: str) -> Dict[str, str | List[str]]:
        matches = CODE_FENCE.findall(text)
        if not matches:
            logger.debug("No fenced code blocks found; returning raw text as explanation.")
            return {"code": "", "language": "", "dependencies": [], "explanation": text.strip()}

        # Choose largest block as primary code
        primary_lang, primary_code = max(matches, key=lambda x: len(x[1]))

        dependencies = self._extract_dependencies(text)
        explanation = self._strip_code_from_text(text, matches)

        return {
            "code": primary_code.strip(),
            "language": (primary_lang or "").strip(),
            "dependencies": dependencies,
            "explanation": explanation,
        }

    def _extract_dependencies(self, text: str) -> List[str]:
        dep_pattern = r"(?:pip install|npm install)\s+([\w\-\s]+)"
        deps = re.findall(dep_pattern, text, re.IGNORECASE)
        flattened = " ".join(deps).split()
        return sorted(set(d.strip() for d in flattened if d.strip()))

    def _strip_code_from_text(self, text: str, matches: List[tuple]) -> str:
        explanation = text
        for lang, code in matches:
            block = f"```{lang}\n{code}```"
            explanation = explanation.replace(block, "")
        return explanation.strip()
