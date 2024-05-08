from typing import Optional, Sequence
from dataclasses import dataclass
from datetime import date

from contribution.domain.constants import (
    Genre,
    MPAA,
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
    PhotoUrl,
)
from contribution.domain.maybe import Maybe
from .contribution import Contribution


@dataclass(slots=True)
class EditMovieContribution(Contribution):
    id: EditMovieContributionId
    author_id: UserId
    movie_id: MovieId
    eng_title: Maybe[str]
    original_title: Maybe[str]
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

    add_photos: Sequence[PhotoUrl]
