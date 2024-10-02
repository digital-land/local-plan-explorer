import csv
import datetime
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_serializer, model_validator

from application.models import LocalPlan, Status


class OrganisationModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=lambda x: x.replace("_", "-"),
        populate_by_name=True,
    )

    organisation: str


class DateModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=lambda x: x.replace("_", "-"),
        populate_by_name=True,
    )

    entry_date: Optional[datetime.date]
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]

    @field_serializer(
        "entry_date",
        "start_date",
        "end_date",
    )
    def serialize_date(self, value):
        if value is not None:
            return value.strftime("%Y-%m-%d")
        return ""


class LocalPlanBaseModel(DateModel):
    reference: str
    name: Optional[str] = None

    organisations: Optional[List[OrganisationModel]]

    @field_serializer(
        "organisations",
    )
    def serialize_organisations(self, value):
        orgs = []
        if value is not None:
            for val in value:
                orgs.append(val.organisation)
        if orgs:
            return ";".join(orgs)
        return ""

    @model_validator(mode="after")
    def replace_none_with_empty_string(cls, values):
        for field in [
            "name",
        ]:
            if getattr(values, field) is None:
                setattr(values, field, "")
        return values


class LocalPlanModel(LocalPlanBaseModel):
    description: Optional[str] = None
    period_start_date: Optional[int]
    period_end_date: Optional[int]
    local_plan_boundary: Optional[str] = None
    documentation_url: Optional[str] = None
    adopted_date: Optional[str] = None

    @model_validator(mode="after")
    def replace_none_with_empty_string(cls, values):
        for field in [
            "description",
            "local_plan_boundary",
            "documentation_url",
            "adopted_date",
        ]:
            if getattr(values, field) is None:
                setattr(values, field, "")
        return values


class LocalPlanDocumentModel(LocalPlanBaseModel):
    local_plan: str
    document_type: str
    document_url: str
    documentation_url: str
    notes: Optional[str] = None
    description: Optional[str] = None
    document_types: Optional[List[str]] = None

    @model_validator(mode="after")
    def replace_none_with_empty_string(cls, values):
        for field in [
            "notes",
            "description",
        ]:
            if getattr(values, field) is None:
                setattr(values, field, "")
        return values


class LocalPlanBoundaryModel(LocalPlanBaseModel):
    geometry: str
    local_plan_boundary_type: str


def export_data_to_file():
    tempdir = TemporaryDirectory()
    path = Path(tempdir.name)
    csv_path = os.path.join(path, "local-plan.csv")
    with open(csv_path, "w") as f:
        fieldnames = list(LocalPlanModel.model_fields.keys())
        fieldnames = [field.replace("_", "-") for field in fieldnames]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for obj in LocalPlan.query.filter(LocalPlan.status == Status.TO):
            m = LocalPlanModel.model_validate(obj)
            data = m.model_dump(by_alias=True)
            writer.writerow(data)

    return tempdir
