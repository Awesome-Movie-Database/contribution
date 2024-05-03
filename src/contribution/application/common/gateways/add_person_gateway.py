from typing import Protocol, Optional

from contribution.domain.value_objects import AddPersonContributionId
from contribution.domain.entities import AddPersonContribution


class AddPersonContributionGateway(Protocol):
    async def with_id(
        self,
        id: AddPersonContributionId,
    ) -> Optional[AddPersonContribution]:
        raise NotImplementedError

    async def save(self, contribution: AddPersonContribution) -> None:
        raise NotImplementedError

    async def update(self, contribution: AddPersonContribution) -> None:
        raise NotImplementedError
