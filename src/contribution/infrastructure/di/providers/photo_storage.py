from dishka import Provider, Scope
from types_aiobotocore_s3 import S3Client

from contribution.application import PhotoGateway
from contribution.infrastructure.s3 import MinIOConfig, PhotoStorage


def photo_storage_provider_factory() -> Provider:
    provider = Provider(Scope.APP)

    provider.provide(photo_storage_factory, provides=PhotoGateway)

    return provider


def photo_storage_factory(
    aioboto3_s3_client: S3Client,
    minio_config: MinIOConfig,
) -> PhotoStorage:
    return PhotoStorage(
        client=aioboto3_s3_client,
        bucket=minio_config.bucket,
    )
