from typing import Protocol, Optional
from datetime import date, datetime

from contribution.domain.value_objects import (
    AddPersonContributionId,
    UserId,
)


class OnPersonAdded(Protocol):
    async def __call__(
        self,
        *,
        id: AddPersonContributionId,
        author_id: UserId,
        first_name: str,
        last_name: str,
        birth_date: date,
        death_date: Optional[date],
        added_at: datetime,
    ) -> None:
        raise NotImplementedError
