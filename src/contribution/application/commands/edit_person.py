from dataclasses import dataclass
from typing import Optional
from datetime import date

from contribution.domain.value_objects import PersonId
from contribution.domain.maybe import Maybe


@dataclass(frozen=True, slots=True)
class EditPersonCommand:
    person_id: PersonId
    first_name: Maybe[str]
    last_name: Maybe[str]
    birth_date: Maybe[date]
    death_date: Maybe[Optional[date]]
