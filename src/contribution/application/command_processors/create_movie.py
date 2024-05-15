import logging

from uuid_extensions import uuid7

from contribution.domain import (
    InvalidMovieEngTitleError,
    InvalidMovieOriginalTitleError,
    InvalidMovieDurationError,
    CreateMovie,
)
from contribution.application.common import (
    CreateAndSaveRoles,
    CreateAndSaveWriters,
    CreateAndSaveCrew,
    CommandProcessor,
    TransactionProcessor,
    MovieIdIsAlreadyTakenError,
    PersonsDoNotExistError,
    RolesAlreadyExistError,
    WritersAlreadyExistError,
    CrewMembersAlreadyExistError,
    MovieGateway,
    PersonGateway,
    UnitOfWork,
)
from contribution.application.commands import CreateMovieCommand


logger = logging.getLogger(__name__)


def create_movie_factory(
    create_movie: CreateMovie,
    create_and_save_roles: CreateAndSaveRoles,
    create_and_save_writers: CreateAndSaveWriters,
    create_and_save_crew: CreateAndSaveCrew,
    movie_gateway: MovieGateway,
    person_gateway: PersonGateway,
    unit_of_work: UnitOfWork,
) -> CommandProcessor[CreateMovieCommand, None]:
    create_movie_processor = CreateMovieProcessor(
        create_movie=create_movie,
        create_and_save_roles=create_and_save_roles,
        create_and_save_writers=create_and_save_writers,
        create_and_save_crew=create_and_save_crew,
        movie_gateway=movie_gateway,
        person_gateway=person_gateway,
    )
    tx_processor = TransactionProcessor(
        processor=create_movie_processor,
        unit_of_work=unit_of_work,
    )
    log_processor = LoggingProcessor(
        processor=tx_processor,
    )

    return log_processor


class CreateMovieProcessor:
    def __init__(
        self,
        *,
        create_movie: CreateMovie,
        create_and_save_roles: CreateAndSaveRoles,
        create_and_save_writers: CreateAndSaveWriters,
        create_and_save_crew: CreateAndSaveCrew,
        movie_gateway: MovieGateway,
        person_gateway: PersonGateway,
    ):
        self._create_movie = create_movie
        self._create_and_save_roles = create_and_save_roles
        self._create_and_save_writers = create_and_save_writers
        self._create_and_save_crew = create_and_save_crew
        self._movie_gateway = movie_gateway
        self._person_gateway = person_gateway

    async def process(self, command: CreateMovieCommand) -> None:
        movie = await self._movie_gateway.with_id(command.id)
        if not movie:
            raise MovieIdIsAlreadyTakenError()

        new_movie = self._create_movie(
            id=command.id,
            eng_title=command.eng_title,
            original_title=command.original_title,
            release_date=command.release_date,
            countries=command.countries,
            genres=command.genres,
            mpaa=command.mpaa,
            duration=command.duration,
            budget=command.budget,
            revenue=command.revenue,
        )
        await self._movie_gateway.save(new_movie)

        await self._create_and_save_roles(
            movie=new_movie,
            movie_roles=command.roles,
        )
        await self._create_and_save_writers(
            movie=new_movie,
            movie_writers=command.writers,
        )
        await self._create_and_save_crew(
            movie=new_movie,
            movie_crew=command.crew,
        )


class LoggingProcessor:
    def __init__(self, processor: TransactionProcessor):
        self._processor = processor

    async def process(self, command: CreateMovieCommand) -> None:
        command_processing_id = uuid7()

        logger.debug(
            "'Create Movie' command processing started",
            extra={
                "processing_id": command_processing_id,
                "command": command,
            },
        )

        try:
            result = await self._processor.process(command)
        except MovieIdIsAlreadyTakenError as e:
            logger.error(
                "Unexpected error occurred: Movie id is already taken",
                extra={"processing_id": command_processing_id},
            )
            raise e
        except InvalidMovieEngTitleError as e:
            logger.error(
                "Unexpected error occurred: Invalid movie eng title",
                extra={"processing_id": command_processing_id},
            )
            raise e
        except InvalidMovieOriginalTitleError as e:
            logger.error(
                "Unexpected error occurred: Invalid movie original title",
                extra={"processing_id": command_processing_id},
            )
            raise e
        except InvalidMovieDurationError as e:
            logger.error(
                "Unexpected error occurred: Invalid movie duration",
                extra={"processing_id": command_processing_id},
            )
            raise e
        except PersonsDoNotExistError as e:
            logger.error(
                "Unexpected error occurred: "
                "Person ids do not belong to any persons",
                extra={
                    "processing_id": command_processing_id,
                    "ids_of_missing_persons": e.ids_of_missing_persons,
                },
            )
            raise e
        except RolesAlreadyExistError as e:
            logger.error(
                "Unexpected error occurred: "
                "Role ids already belong to some roles",
                extra={
                    "processing_id": command_processing_id,
                    "ids_of_existing_roles": e.ids_of_existing_roles,
                },
            )
            raise e
        except WritersAlreadyExistError as e:
            logger.error(
                "Unexpected error occurred: "
                "Writer ids already belong to some writers",
                extra={
                    "processing_id": command_processing_id,
                    "ids_of_existing_writers": e.ids_of_existing_writers,
                },
            )
            raise e
        except CrewMembersAlreadyExistError as e:
            logger.error(
                "Unexpected error occurred: "
                "Crew member ids already belong to some crew members",
                extra={
                    "processing_id": command_processing_id,
                    "ids_of_existing_crew_members": e.ids_of_existing_crew_members,
                },
            )
            raise e
        except Exception as e:
            logger.exception(
                "Unexpected error occurred",
                exc_info=e,
                extra={
                    "processing_id": command_processing_id,
                    "error": e,
                },
            )
            raise e

        logger.debug(
            "'Create Movie' command processing completed",
            extra={"processing_id": command_processing_id},
        )

        return result
