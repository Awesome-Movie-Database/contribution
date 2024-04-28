from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass(frozen=True, slots=True)
class AddPersonCommand:
    first_name: str
    last_name: str
    birth_date: date
    death_date: Optional[date]