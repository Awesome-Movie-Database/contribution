from typing import Optional

from contribution.domain import (
    EditPersonContributionId,
    EditPersonContribution,
)


class EditPersonContributionMap:
    def __init__(self):
        self._contributions: set[EditPersonContribution] = set()

    def with_id(
        self,
        id: EditPersonContributionId,
    ) -> Optional[EditPersonContribution]:
        for contribution in self._contributions:
            if contribution.id == id:
                return contribution
        return None

    def save(self, contribution: EditPersonContribution) -> None:
        """
        Saves contribution in identity map if contribution doesn't
        exist, otherwise raises ValueError.
        """
        contribution_from_map = self.with_id(contribution.id)
        if contribution_from_map:
            message = "Edit person contribution already exists in identity map"
            raise ValueError(message)
        self._contributions.add(contribution)

    def update(self, contribution: EditPersonContribution) -> None:
        """
        Updates contribution in identity map if contribution exists,
        otherwise raises ValueError.
        """
        contribution_from_map = self.with_id(contribution.id)
        if not contribution_from_map:
            message = "Edit person contribution doesn't exist in identity map"
            raise ValueError(message)
        self._contributions.remove(contribution_from_map)
        self._contributions.add(contribution)