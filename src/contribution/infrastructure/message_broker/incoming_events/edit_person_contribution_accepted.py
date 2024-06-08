from dataclasses import dataclass

from contribution.domain import EditPersonContributionId
from contribution.application import OperationId


@dataclass(frozen=True, slots=True)
class IncomingEditPersonContributionAcceptedEvent:
    operation_id: OperationId
    contribution_id: EditPersonContributionId
