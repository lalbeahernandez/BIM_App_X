from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=200)
    timezone: str = 'UTC'
    currency: str = Field(default='EUR', min_length=3, max_length=3)


class ProjectOut(ProjectCreate):
    id: UUID
    organization_id: UUID
    created_at: datetime


class ModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    discipline: str | None = Field(default=None, max_length=32)


class ModelOut(ModelCreate):
    id: UUID
    project_id: UUID
    created_at: datetime


class RevisionOut(BaseModel):
    id: UUID
    model_id: UUID
    revision_no: int
    file_name: str
    status: str
    ifc_schema: str | None = None
    error_message: str | None = None


SelectionSource = Literal['element', 'boq', 'activity']


class SelectionResolveIn(BaseModel):
    source_type: SelectionSource
    ids: list[UUID] = Field(min_length=1, max_length=1000)


class SelectionResolveOut(BaseModel):
    element_ids: list[UUID]
    boq_item_ids: list[UUID]
    activity_ids: list[UUID]


class WorkAreaBoq(BaseModel):
    id: UUID
    code: str
    description: str
    unit: str
    quantity: float
    rate: float
    amount: float


class WorkAreaActivity(BaseModel):
    id: UUID
    external_id: str | None
    name: str
    planned_start: date | None
    planned_finish: date | None
    percent_complete: float


class WorkAreaOut(BaseModel):
    boq: list[WorkAreaBoq]
    activities: list[WorkAreaActivity]
    revisions: list[RevisionOut]
