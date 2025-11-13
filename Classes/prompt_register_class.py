from dataclasses import dataclass

@dataclass
class PromptRegister:
    variable: str
    prompt_function: object
    reasoning_effort: str
    verbosity: str



