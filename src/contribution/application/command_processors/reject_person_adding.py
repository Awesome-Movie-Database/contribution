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
    AddPersonContributionGateway,
    UserGateway,
    AchievementGateway,
    ObjectStorage,
    UnitOfWork,
    OnEventOccurred,
    AchievementEarnedEvent,
)
from contribution.application.commands import RejectPersonAddingCommand


logger = logging.getLogger(__name__)


def reject_person_adding_factory(
    correlation_id: CorrelationId,
    reject_contribution: RejectContribution,
    add_person_contribution_gateway: AddPersonContributionGateway,
    user_gateway: UserGateway,
    achievement_gateway: AchievementGateway,
    unit_of_work: UnitOfWork,
    object_storage: ObjectStorage,
    on_achievement_earned: OnEventOccurred[AchievementEarnedEvent],
) -> CommandProcessor[RejectPersonAddingCommand, Optional[AchievementId]]:
    reject_person_addition_processor = RejectPersonAddingProcessor(
        reject_contribution=reject_contribution,
        add_person_contribution_gateway=add_person_contribution_gateway,
        user_gateway=user_gateway,
        achievement_gateway=achievement_gateway,
        object_storage=object_storage,
    )
    callback_processor = AchievementEearnedCallbackProcessor(
        processor=reject_person_addition_processor,
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


class RejectPersonAddingProcessor:
    def __init__(
        self,
        *,
        reject_contribution: RejectContribution,
        add_person_contribution_gateway: AddPersonContributionGateway,
        user_gateway: UserGateway,
        achievement_gateway: AchievementGateway,
        object_storage: ObjectStorage,
    ):
        self._reject_contribution = reject_contribution
        self._add_person_contribution_gateway = add_person_contribution_gateway
        self._user_gateway = user_gateway
        self._achievement_gateway = achievement_gateway
        self._object_storage = object_storage

    async def process(
        self,
        command: RejectPersonAddingCommand,
    ) -> Optional[AchievementId]:
        contribution = (
            await self._add_person_contribution_gateway.acquire_by_id(
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
        await self._add_person_contribution_gateway.update(contribution)

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
        command: RejectPersonAddingCommand,
    ) -> Optional[AchievementId]:
        self._correlation_id = uuid7()

        logger.debug(
            "'Reject Person Adding' command processing started",
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
            "'Reject Person Adding' command processing completed",
            extra={
                "correlation_id": self._correlation_id,
                "achievement_id": result,
            },
        )

        return result
