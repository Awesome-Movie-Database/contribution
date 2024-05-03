import logging

from uuid_extensions import uuid7

from contribution.domain.value_objects import AchievementId
from contribution.domain.services import (
    AcceptContribution,
    CreateMovie,
)
from contribution.application.common.command_processors import (
    CommandProcessor,
    TransactionProcessor,
)
from contribution.application.common.exceptions import (
    MovieIdIsAlreadyTakenError,
    UserDoesNotExistError,
    ContributionDoesNotExistError,
)
from contribution.application.common.gateways import (
    AddMovieContributionGateway,
    MovieGateway,
    UserGateway,
    AchievementGateway,
)
from contribution.application.common.unit_of_work import UnitOfWork
from contribution.application.common.callbacks import OnAchievementEarned
from contribution.application.commands import AcceptMovieAdditionCommand


logger = logging.getLogger(__name__)


def accept_movie_addition_factory(
    accept_contribution: AcceptContribution,
    create_movie: CreateMovie,
    add_movie_contribution_gateway: AddMovieContributionGateway,
    user_gateway: UserGateway,
    movie_gateway: MovieGateway,
    achievement_gateway: AchievementGateway,
    unit_of_work: UnitOfWork,
    on_achievement_earned: OnAchievementEarned,
) -> CommandProcessor[AcceptMovieAdditionCommand, None]:
    accept_movie_addition_processor = AcceptMovieAdditionProcessor(
        accept_contribution=accept_contribution,
        create_movie=create_movie,
        add_movie_contribution_gateway=add_movie_contribution_gateway,
        user_gateway=user_gateway,
        movie_gateway=movie_gateway,
        achievement_gateway=achievement_gateway,
        on_achievement_earned=on_achievement_earned,
    )
    tx_processor = TransactionProcessor(
        processor=accept_movie_addition_processor,
        unit_of_work=unit_of_work,
    )
    log_processor = LoggingProcessor(
        processor=tx_processor,
    )

    return log_processor


class AcceptMovieAdditionProcessor:
    def __init__(
        self,
        *,
        accept_contribution: AcceptContribution,
        create_movie: CreateMovie,
        add_movie_contribution_gateway: AddMovieContributionGateway,
        user_gateway: UserGateway,
        movie_gateway: MovieGateway,
        achievement_gateway: AchievementGateway,
        on_achievement_earned: OnAchievementEarned,
    ):
        self._accept_contribution = accept_contribution
        self._create_movie = create_movie
        self._add_movie_contribution_gateway = add_movie_contribution_gateway
        self._user_gateway = user_gateway
        self._movie_gateway = movie_gateway
        self._achievement_gateway = achievement_gateway
        self._on_achievement_earned = on_achievement_earned

    async def process(
        self,
        command: AcceptMovieAdditionCommand,
    ) -> None:
        contribution = await self._add_movie_contribution_gateway.with_id(
            id=command.contribution_id,
        )
        if not contribution:
            raise ContributionDoesNotExistError()

        author = await self._user_gateway.acquire_with_id(
            id=contribution.author_id,
        )
        if not author:
            raise UserDoesNotExistError(contribution.author_id)

        movie = await self._movie_gateway.with_id(command.movie_id)
        if movie:
            raise MovieIdIsAlreadyTakenError()

        achievement = self._accept_contribution(
            achievement_id=AchievementId(uuid7()),
            contribution=contribution,
            author=author,
            current_timestamp=command.accepted_at,
        )
        if achievement:
            await self._achievement_gateway.save(achievement)

        await self._user_gateway.update(author)
        await self._add_movie_contribution_gateway.update(contribution)

        new_movie = self._create_movie(
            id=command.movie_id,
            title=contribution.title,
            release_date=contribution.release_date,
            countries=contribution.countries,
            genres=contribution.genres,
            mpaa=contribution.mpaa,
            duration=contribution.duration,
            budget=contribution.budget,
            revenue=contribution.revenue,
        )
        await self._movie_gateway.save(new_movie)

        if achievement:
            await self._on_achievement_earned(
                id=achievement.id,
                user_id=achievement.user_id,
                achieved=achievement.achieved,
                achieved_at=command.accepted_at,
            )


class LoggingProcessor:
    def __init__(self, processor: TransactionProcessor):
        self._processor = processor

    async def process(
        self,
        command: AcceptMovieAdditionCommand,
    ) -> None:
        logger.debug(
            msg="Processing Accept Movie Addition command",
            extra={"command": command},
        )

        try:
            result = await self._processor.process(command)
        except ContributionDoesNotExistError as e:
            logger.error(
                msg="Contribution doesn't exist",
                extra={"contribution_id": command.contribution_id},
            )
            raise e
        except UserDoesNotExistError as e:
            logger.error(
                msg=(
                    "Contribution has author id, "
                    "using which user gateway returns None"
                ),
                extra={"user_id": e.id},
            )
            raise e
        except MovieIdIsAlreadyTakenError as e:
            logger.error(
                msg="Movie id is already taken",
                extra={"movie_id": command.movie_id},
            )
            raise e

        logger.debug(
            msg="Accept Movie Addition command was processed",
        )

        return result
