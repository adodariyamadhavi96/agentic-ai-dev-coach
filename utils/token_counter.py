from typing import List

import tiktoken


def count_tokens(texts: List[str], model: str = "gpt-3.5-turbo") -> int:
    encoder = tiktoken.encoding_for_model(model)
    return sum(len(encoder.encode(t)) for t in texts)
