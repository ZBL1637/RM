from __future__ import annotations

from app.repositories.method_repository import MethodRepository, method_repository
from app.schemas.methods import MethodDetail, MethodSummary


class MethodService:
    def __init__(self, repository: MethodRepository) -> None:
        self._repository = repository

    def list_methods(self) -> list[MethodSummary]:
        methods = self._repository.list_active()
        return [self._to_summary(method) for method in methods]

    def get_method_by_slug(self, slug: str) -> MethodDetail | None:
        return self._repository.get_active_by_slug(slug)

    @staticmethod
    def _to_summary(method: MethodDetail) -> MethodSummary:
        return MethodSummary.model_validate(
            method.model_dump(
                include={
                    "id",
                    "slug",
                    "name",
                    "category",
                    "description",
                    "applicable_scenarios",
                    "data_type_label",
                    "analysis_difficulty",
                    "sample_requirement",
                    "is_recommended",
                }
            )
        )


method_service = MethodService(repository=method_repository)
