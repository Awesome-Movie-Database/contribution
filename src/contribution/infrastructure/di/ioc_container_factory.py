from dishka import AsyncContainer, make_async_container

from .providers import (
    domain_validators_provider_factory,
    domain_services_provider_factrory,
    identity_maps_provider_factory,
    application_services_provider_factory,
    command_processors_provider_factory,
)


def ioc_container_factory() -> AsyncContainer:
    ioc_container = make_async_container(
        domain_validators_provider_factory(),
        domain_services_provider_factrory(),
        identity_maps_provider_factory(),
        application_services_provider_factory(),
        command_processors_provider_factory(),
    )
    return ioc_container