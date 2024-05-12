from dishka import Provider, Scope

from contribution.domain.value_objects import (
    AddMovieContributionId,
    EditMovieContributionId,
    AddPersonContributionId,
    EditPersonContributionId,
    AchievementId,
)
from contribution.application.common.command_processors import (
    CommandProcessor,
)
from contribution.application.command_processors import (
    create_user_factory,
    update_user_factory,
    create_movie_factory,
    update_movie_factory,
    create_person_factory,
    update_person_factory,
    add_movie_factory,
    edit_movie_factory,
    add_person_factory,
    edit_person_factory,
    accept_movie_addition_factory,
    accept_movie_editing_factory,
    reject_movie_addition_factory,
    reject_movie_editing_factory,
    accept_person_addition_factory,
    accept_person_editing_factory,
    reject_person_addition_factory,
    reject_person_editing_factory,
)
from contribution.application.commands import (
    CreateUserCommand,
    UpdateUserCommand,
    CreateMovieCommand,
    UpdateMovieCommand,
    CreatePersonCommand,
    UpdatePersonCommand,
    AddMovieCommand,
    EditMovieCommand,
    AddPersonCommand,
    EditPersonCommand,
    AcceptMovieAdditionCommand,
    AcceptMovieEditingCommand,
    RejectMovieAdditionCommand,
    RejectMovieEditingCommand,
    AcceptPersonAdditionCommand,
    AcceptPersonEditingCommand,
    RejectPersonAdditionCommand,
    RejectPersonEditingCommand,
)


def command_processors_provider_factory() -> Provider:
    provider = Provider(scope=Scope.REQUEST)

    provider.provide(
        create_user_factory,
        provides=CommandProcessor[CreateUserCommand, None],
    )
    provider.provide(
        update_user_factory,
        provides=CommandProcessor[UpdateUserCommand, None],
    )
    provider.provide(
        create_movie_factory,
        provides=CommandProcessor[CreateMovieCommand, None],
    )
    provider.provide(
        update_movie_factory,
        provides=CommandProcessor[UpdateMovieCommand, None],
    )
    provider.provide(
        create_person_factory,
        provides=CommandProcessor[CreatePersonCommand, None],
    )
    provider.provide(
        update_person_factory,
        provides=CommandProcessor[UpdatePersonCommand, None],
    )
    provider.provide(
        add_movie_factory,
        provides=CommandProcessor[AddMovieCommand, AddMovieContributionId],
    )
    provider.provide(
        edit_movie_factory,
        provides=CommandProcessor[EditMovieCommand, EditMovieContributionId],
    )
    provider.provide(
        add_person_factory,
        provides=CommandProcessor[AddPersonCommand, AddPersonContributionId],
    )
    provider.provide(
        edit_person_factory,
        provides=CommandProcessor[EditPersonCommand, EditPersonContributionId],
    )
    provider.provide(
        accept_movie_addition_factory,
        provides=CommandProcessor[AcceptMovieAdditionCommand, AchievementId],
    )
    provider.provide(
        accept_movie_editing_factory,
        provides=CommandProcessor[AcceptMovieEditingCommand, AchievementId],
    )
    provider.provide(
        reject_movie_addition_factory,
        provides=CommandProcessor[RejectMovieAdditionCommand, AchievementId],
    )
    provider.provide(
        reject_movie_editing_factory,
        provides=CommandProcessor[RejectMovieEditingCommand, AchievementId],
    )
    provider.provide(
        accept_person_addition_factory,
        provides=CommandProcessor[AcceptPersonAdditionCommand, AchievementId],
    )
    provider.provide(
        accept_person_editing_factory,
        provides=CommandProcessor[AcceptPersonEditingCommand, AchievementId],
    )
    provider.provide(
        reject_person_addition_factory,
        provides=CommandProcessor[RejectPersonAdditionCommand, AchievementId],
    )
    provider.provide(
        reject_person_editing_factory,
        provides=CommandProcessor[RejectPersonEditingCommand, AchievementId],
    )

    return provider