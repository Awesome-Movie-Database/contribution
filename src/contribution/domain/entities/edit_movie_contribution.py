from typing import Optional, Sequence
from dataclasses import dataclass
from datetime import date, datetime

from contribution.domain.constants import (
    Genre,
    MPAA,
    ContributionStatus,
)
from contribution.domain.value_objects import (
    EditMovieContributionId,
    UserId,
    MovieId,
    RoleId,
    WriterId,
    CrewMemberId,
    ContributionRole,
    ContributionWriter,
    ContributionCrewMember,
    Country,
    Money,
)
from contribution.domain.maybe import Maybe


@dataclass(slots=True)
class EditMovieContribution:
    id: EditMovieContributionId
    author_id: UserId
    movie_id: MovieId
    title: Maybe[str]
    release_date: Maybe[date]
    countries: Maybe[Sequence[Country]]
    genres: Maybe[Sequence[Genre]]
    mpaa: Maybe[MPAA]
    duration: Maybe[int]
    budget: Maybe[Optional[Money]]
    revenue: Maybe[Optional[Money]]

    add_roles: Sequence[ContributionRole]
    remove_roles: Sequence[RoleId]

    add_writers: Sequence[ContributionWriter]
    remove_writers: Sequence[WriterId]

    add_crew: Sequence[ContributionCrewMember]
    remove_crew: Sequence[CrewMemberId]

    status: ContributionStatus
    created_at: datetime
    updated_at: Optional[datetime]