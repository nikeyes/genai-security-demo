from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    provider_name: str

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @classmethod
    def empty(cls, provider_name: str = 'Unknown') -> 'TokenUsage':
        return cls(input_tokens=0, output_tokens=0, provider_name=provider_name)


def format_token_usage(usage: Optional[TokenUsage]) -> str:
    if usage is None:
        return 'Tokens: unavailable'

    return f'Tokens: {usage.input_tokens} + {usage.output_tokens} = {usage.total_tokens} ({usage.provider_name})'
