# mypy: disable-error-code="assignment"

from typing import Any, Sequence

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import InsertOne, UpdateOne, DeleteOne

from contribution.domain import AddPersonContribution


class CommitAddPersonContributionCollectionChanges:
    def __init__(self, user_collection: AsyncIOMotorCollection):
        self._collection = user_collection

    async def __call__(
        self,
        *,
        new: Sequence[AddPersonContribution],
        clean: Sequence[AddPersonContribution],
        dirty: Sequence[AddPersonContribution],
        deleted: Sequence[AddPersonContribution],
    ) -> None:
        inserts = [
            InsertOne(self._contribution_to_document(contribution))
            for contribution in new
        ]
        updates = [
            UpdateOne(
                {"id": clean_contribution.id},
                self._pipeline_to_update_contribution(
                    clean_contribution,
                    dirty_contribution,
                ),
            )
            for clean_contribution, dirty_contribution in zip(clean, dirty)
        ]
        deletes = [
            DeleteOne({"id": contribution.id}) for contribution in deleted
        ]

        changes = [*inserts, *updates, *deletes]
        await self._collection.bulk_write(changes)

    def _contribution_to_document(
        self,
        contribution: AddPersonContribution,
    ) -> dict[str, Any]:
        document = {
            "id": contribution.id.hex,
            "status": contribution.status.value,
            "author_id": contribution.author_id.hex,
            "first_name": contribution.first_name,
            "last_name": contribution.last_name,
            "sex": contribution.sex.value,
            "birth_date": contribution.birth_date.isoformat(),
            "photos": list(contribution.photos),
        }

        if contribution.status_updated_at:
            document[
                "status_updated_at"
            ] = contribution.status_updated_at.isoformat()
        else:
            document["status_updated_at"] = None
        if contribution.death_date:
            document["death_date"] = contribution.death_date.isoformat()
        else:
            document["death_date"] = None

        return document

    def _pipeline_to_update_contribution(
        self,
        clean: AddPersonContribution,
        dirty: AddPersonContribution,
    ) -> dict[str, Any]:
        pipeline = {"$set": {}}

        if clean.status != dirty.status:
            pipeline["$set"]["status"] = dirty.status.value
        if clean.status_updated_at != dirty.status_updated_at:
            if dirty.status_updated_at:
                pipeline["$set"][
                    "status_updated_at"
                ] = dirty.status_updated_at.isoformat()
            else:
                pipeline["$set"]["status_updated_at"] = None
        if clean.first_name != dirty.first_name:
            pipeline["$set"]["first_name"] = dirty.first_name
        if clean.last_name != dirty.last_name:
            pipeline["$set"]["last_name"] = dirty.last_name
        if clean.sex != dirty.sex:
            pipeline["$set"]["sex"] = dirty.sex.value
        if clean.birth_date != dirty.birth_date:
            pipeline["$set"]["birth_date"] = dirty.birth_date.isoformat()
        if clean.death_date != dirty.death_date:
            if dirty.death_date:
                pipeline["$set"]["death_date"] = dirty.death_date.isoformat()
            else:
                pipeline["$set"]["death_date"] = None
        if clean.photos != dirty.photos:
            pipeline["$set"]["photos"] = list(dirty.photos)

        return pipeline
