from dataclasses import dataclass

from contribution.domain.constants import CrewMembership
from contribution.domain.value_objects import PersonId


@dataclass(slots=True)
class ContributionCrewMember:
    person_id: PersonId
    membership: CrewMembership
