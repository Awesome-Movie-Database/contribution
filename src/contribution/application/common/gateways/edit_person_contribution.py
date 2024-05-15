from typing import Protocol, Optional

from contribution.domain import (
    EditPersonContributionId,
    EditPersonContribution,
)


class EditPersonContributionGateway(Protocol):
    async def with_id(
        self,
        id: EditPersonContributionId,
    ) -> Optional[EditPersonContribution]:
        raise NotImplementedError

    async def save(self, contribution: EditPersonContribution) -> None:
        raise NotImplementedError

    async def update(self, contribution: EditPersonContribution) -> None:
        raise NotImplementedError
