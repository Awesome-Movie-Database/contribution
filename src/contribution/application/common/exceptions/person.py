from typing import Sequence

from contribution.domain.value_objects import PersonId
from .base import ApplicationError


class PersonsDoNotExistError(ApplicationError):
    def __init__(
        self,
        ids_of_missing_persons: Sequence[PersonId],
    ):
        self.ids_of_missing_persons = ids_of_missing_persons