import logging
from typing import Optional

from uuid_extensions import uuid7

from contribution.domain import (
    AchievementId,
    RejectContribution,
)
from contribution.application.common import (
    CorrelationId,
    CommandProcessor,
    TransactionProcessor,
    AchievementEearnedCallbackProcessor,
    UserDoesNotExistError,
    ContributionDoesNotExistError,
    AchievementDoesNotExistError,
    AddMovieContributionGateway,
    UserGateway,
    AchievementGateway,
    ObjectStorage,
    UnitOfWork,
    OnEventOccurred,
    AchievementEarnedEvent,
)
from contribution.application.commands import RejectMovieAddingCommand


logger = logging.getLogger(__name__)


def reject_movie_adding_factory(
    correlation_id: CorrelationId,
    reject_contribution: RejectContribution,
    add_movie_contribution_gateway: AddMovieContributionGateway,
    user_gateway: UserGateway,
    achievement_gateway: AchievementGateway,
    object_storage: ObjectStorage,
    unit_of_work: UnitOfWork,
    on_achievement_earned: OnEventOccurred[AchievementEarnedEvent],
) -> CommandProcessor[RejectMovieAddingCommand, Optional[AchievementId]]:
    accept_movie_addition_processor = RejectMovieAddingProcessor(
        reject_contribution=reject_contribution,
        add_movie_contribution_gateway=add_movie_contribution_gateway,
        user_gateway=user_gateway,
        achievement_gateway=achievement_gateway,
        object_storage=object_storage,
    )
    callback_processor = AchievementEearnedCallbackProcessor(
        processor=accept_movie_addition_processor,
        achievement_gateway=achievement_gateway,
        on_achievement_earned=on_achievement_earned,
    )
    tx_processor = TransactionProcessor(
        processor=callback_processor,
        unit_of_work=unit_of_work,
    )
    log_processor = LoggingProcessor(
        processor=tx_processor,
        correlation_id=correlation_id,
    )

    return log_processor


class RejectMovieAddingProcessor:
    def __init__(
        self,
        *,
        reject_contribution: RejectContribution,
        add_movie_contribution_gateway: AddMovieContributionGateway,
        user_gateway: UserGateway,
        achievement_gateway: AchievementGateway,
        object_storage: ObjectStorage,
    ):
        self._reject_contribution = reject_contribution
        self._add_movie_contribution_gateway = add_movie_contribution_gateway
        self._user_gateway = user_gateway
        self._achievement_gateway = achievement_gateway
        self._object_storage = object_storage

    async def process(
        self,
        command: RejectMovieAddingCommand,
    ) -> Optional[AchievementId]:
        contribution = (
            await self._add_movie_contribution_gateway.acquire_by_id(
                id=command.contribution_id,
            )
        )
        if not contribution:
            raise ContributionDoesNotExistError()

        author = await self._user_gateway.acquire_by_id(
            id=contribution.author_id,
        )
        if not author:
            raise UserDoesNotExistError()

        achievement = self._reject_contribution(
            achievement_id=AchievementId(uuid7()),
            contribution=contribution,
            author=author,
            current_timestamp=command.rejected_at,
        )
        if achievement:
            await self._achievement_gateway.save(achievement)

        await self._user_gateway.update(author)
        await self._add_movie_contribution_gateway.update(contribution)

        await self._object_storage.delete_photos_by_urls(contribution.photos)

        return achievement.id if achievement else None


class LoggingProcessor:
    def __init__(
        self,
        *,
        processor: TransactionProcessor,
        correlation_id: CorrelationId,
    ):
        self._processor = processor
        self._correlation_id = correlation_id

    async def process(
        self,
        command: RejectMovieAddingCommand,
    ) -> Optional[AchievementId]:
        logger.debug(
            "'Reject Movie Adding' command processing started",
            extra={
                "correlation_id": self._correlation_id,
                "command": command,
            },
        )

        try:
            result = await self._processor.process(command)
        except ContributionDoesNotExistError as e:
            logger.error(
                "Unexpected error occurred: Contribution doesn't exist",
                extra={"correlation_id": self._correlation_id},
            )
            raise e
        except UserDoesNotExistError as e:
            logger.error(
                "Unexpected error occurred: Contribution has author id, "
                "using which user gateway returns None",
                extra={"correlation_id": self._correlation_id},
            )
            raise e
        except AchievementDoesNotExistError as e:
            logger.error(
                "Unexpected error occurred: Achievement was created, "
                "but achievement gateway returns None",
                extra={"correlation_id": self._correlation_id},
            )
        except Exception as e:
            logger.exception(
                "Unexpected error occurred",
                exc_info=e,
                extra={
                    "correlation_id": self._correlation_id,
                    "error": e,
                },
            )
            raise e

        logger.debug(
            "'Reject Movie Adding' command processing completed",
            extra={
                "correlation_id": self._correlation_id,
                "achievement_id": result,
            },
        )

        return result