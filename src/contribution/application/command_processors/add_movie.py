from datetime import datetime, timezone

from uuid_extensions import uuid7

from contribution.domain.value_objects import AddMovieContributionId
from contribution.domain.services import AddMovie
from contribution.application.common.services import (
    AccessConcern,
    EnsurePersonsExist,
)
from contribution.application.common.command_processors import (
    CommandProcessor,
    AuthorizationProcessor,
    TransactionProcessor,
)
from contribution.application.common.exceptions import UserDoesNotExistError
from contribution.application.common.gateways import (
    AddMovieContributionGateway,
    UserGateway,
    PermissionsGateway,
)
from contribution.application.common.unit_of_work import UnitOfWork
from contribution.application.common.identity_provider import IdentityProvider
from contribution.application.common.callbacks import OnMovieAdded
from contribution.application.commands import AddMovieCommand


def add_movie_factory(
    add_movie: AddMovie,
    access_concern: AccessConcern,
    ensure_persons_exist: EnsurePersonsExist,
    add_movie_contribution_gateway: AddMovieContributionGateway,
    user_gateway: UserGateway,
    permissions_gateway: PermissionsGateway,
    unit_of_work: UnitOfWork,
    identity_provider: IdentityProvider,
    on_movie_added: OnMovieAdded,
) -> CommandProcessor[AddMovieCommand, AddMovieContributionId]:
    current_timestamp = datetime.now(timezone.utc)

    add_movie_processor = AddMovieProcessor(
        add_movie=add_movie,
        ensure_persons_exist=ensure_persons_exist,
        add_movie_contribution_gateway=add_movie_contribution_gateway,
        user_gateway=user_gateway,
        identity_provider=identity_provider,
        current_timestamp=current_timestamp,
    )
    authz_processor = AuthorizationProcessor(
        processor=add_movie_processor,
        access_concern=access_concern,
        permissions_gateway=permissions_gateway,
        identity_provider=identity_provider,
    )
    callback_processor = CallbackProcessor(
        processor=authz_processor,
        on_movie_added=on_movie_added,
        identity_provider=identity_provider,
        current_timestamp=current_timestamp,
    )
    tx_processor = TransactionProcessor(
        processor=callback_processor,
        unit_of_work=unit_of_work,
    )
    return tx_processor


class AddMovieProcessor:
    def __init__(
        self,
        *,
        add_movie: AddMovie,
        ensure_persons_exist: EnsurePersonsExist,
        add_movie_contribution_gateway: AddMovieContributionGateway,
        user_gateway: UserGateway,
        identity_provider: IdentityProvider,
        current_timestamp: datetime,
    ):
        self._add_movie = add_movie
        self._ensure_persons_exist = ensure_persons_exist
        self._add_movie_contribution_gateway = add_movie_contribution_gateway
        self._user_gateway = user_gateway
        self._identity_provider = identity_provider
        self._current_timestamp = current_timestamp

    async def process(
        self,
        command: AddMovieCommand,
    ) -> AddMovieContributionId:
        current_user_id = await self._identity_provider.user_id()

        author = await self._user_gateway.with_id(current_user_id)
        if not author:
            raise UserDoesNotExistError(current_user_id)

        await self._ensure_persons_exist(
            *(role.person_id for role in command.roles),
            *(writer.person_id for writer in command.writers),
            *(crew_member.person_id for crew_member in command.crew),
        )

        contribution = self._add_movie(
            id=AddMovieContributionId(uuid7()),
            author=author,
            title=command.title,
            release_date=command.release_date,
            countries=command.countries,
            genres=command.genres,
            mpaa=command.mpaa,
            duration=command.duration,
            budget=command.budget,
            revenue=command.revenue,
            roles=command.roles,
            writers=command.writers,
            crew=command.crew,
            current_timestamp=self._current_timestamp,
        )
        await self._add_movie_contribution_gateway.save(contribution)

        return contribution.id


class CallbackProcessor:
    def __init__(
        self,
        *,
        processor: AuthorizationProcessor,
        on_movie_added: OnMovieAdded,
        identity_provider: IdentityProvider,
        current_timestamp: datetime,
    ):
        self._processor = processor
        self._on_movie_added = on_movie_added
        self._identity_provider = identity_provider
        self._current_timestamp = current_timestamp

    async def process(
        self,
        command: AddMovieCommand,
    ) -> AddMovieContributionId:
        result = await self._processor.process(command)
        current_user_id = await self._identity_provider.user_id()

        await self._on_movie_added(
            id=result,
            author_id=current_user_id,
            title=command.title,
            release_date=command.release_date,
            countries=command.countries,
            genres=command.genres,
            mpaa=command.mpaa,
            duration=command.duration,
            budget=command.budget,
            revenue=command.revenue,
            roles=command.roles,
            writers=command.writers,
            crew=command.crew,
            added_at=self._current_timestamp,
        )

        return result