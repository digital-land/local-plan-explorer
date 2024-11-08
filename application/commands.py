import csv
import os
from datetime import datetime
from pathlib import Path

import click
import requests
from flask import current_app
from flask.cli import AppGroup
from slugify import slugify
from sqlalchemy import not_, select, text
from sqlalchemy.inspection import inspect

from application.extensions import db
from application.models import (
    EventCategory,
    LocalPlan,
    LocalPlanBoundary,
    LocalPlanDocument,
    LocalPlanDocumentType,
    LocalPlanEvent,
    LocalPlanEventType,
    LocalPlanTimetable,
    Organisation,
    Status,
    document_organisation,
)

data_cli = AppGroup("data")


@data_cli.command("load-orgs")
def load_orgs():
    url = "https://datasette.planning.data.gov.uk/digital-land/organisation.json?_shape=array"
    orgs = []
    columns = set([column.name for column in inspect(Organisation).c])
    while url:
        resp = requests.get(url)
        try:
            url = resp.links.get("next").get("url")
        except AttributeError:
            url = None
        orgs.extend(resp.json())

    for org in orgs:
        if not org["organisation"]:
            print("Skipping invalid org", org["name"])
            continue
        if org["end_date"]:
            print("Skipping end dated org", org["organisation"])
            continue
        if org["dataset"] not in [
            "local-authority",
            "development-corporation",
            "national-park-authority",
        ]:
            print(
                "Skipping org",
                org["organisation"],
                "as not a local authority, development corporation or national park authority",
            )
            continue
        try:
            org_obj = Organisation.query.get(org["organisation"])
            if org_obj is None:
                org_obj = Organisation()
                print("Adding new org", org["organisation"])
            else:
                print("Updating org", org["organisation"])
            for key, value in org.items():
                if key in columns:
                    v = value if value else None
                    setattr(org_obj, key, v)
            db.session.add(org_obj)
            db.session.commit()
        except Exception as e:
            print(e)
            continue


@data_cli.command("load-plans")
def load_plans():
    current_file_path = Path(__file__).resolve()
    data_directory = os.path.join(current_file_path.parent.parent, "data")
    file_path = os.path.join(data_directory, "local-plan.csv")

    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        columns = set([column.name for column in inspect(LocalPlan).c])

        for row in reader:
            try:
                plan = LocalPlan.query.get(row["reference"])
                if plan is None:
                    print("Adding new plan", row["reference"])
                    plan = LocalPlan()
                    for key, value in row.items():
                        k = key.lower().replace("-", "_")
                        if k in columns:
                            setattr(plan, k, value if value else None)
                else:
                    print("Updating plan", row["reference"])
                    for key, value in row.items():
                        k = key.lower().replace("-", "_")
                        if k in columns and not k.endswith("date"):
                            setattr(plan, k, value if value else None)
                db.session.add(plan)
                organisations = row.get("organisations")
                for org in organisations.split(";") if organisations else []:
                    organisation = Organisation.query.get(org)
                    if (
                        organisation is not None
                        and organisation not in plan.organisations
                    ):
                        plan.organisations.append(organisation)
                db.session.commit()
            except Exception as e:
                print(f"Error processing row {row['reference']}: {e}")
                db.session.rollback()


@data_cli.command("load-boundaries")
def load_boundaries():
    from application.extensions import db

    orgs = Organisation.query.all()
    for org in orgs:
        curie = f"statistical-geography:{org.statistical_geography}"
        g = _get_geography(curie)
        if g is not None:
            print("Loading boundary for", org.organisation)
            org.geometry = g["geometry"]
            org.geojson = g["geojson"]
            org.point = g["point"]
            db.session.add(org)
            db.session.commit()
        else:
            print("No boundary found for", org.organisation)


def _get_geography(reference):
    url = "https://www.planning.data.gov.uk/entity.json"
    params = {"curie": reference}
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status
        data = resp.json()
        if len(data["entities"]) == 0:
            print("No entities found for url", resp.url)
            return None
        point = data["entities"][0].get("point")
        entity = data["entities"][0].get("entity")
        geojson_url = f"https://www.planning.data.gov.uk/entity/{entity}.geojson"
        try:
            resp = requests.get(geojson_url)
            resp.raise_for_status()
            geography = {
                "geojson": resp.json(),
                "geometry": data["entities"][0].get("geometry"),
                "point": point,
            }
            return geography
        except Exception as e:
            print(e)
            return None
    except Exception as e:
        print(e)
        return None


@data_cli.command("create-import-docs")
def create_importable_docs():
    current_file_path = Path(__file__).resolve()
    data_directory = os.path.join(current_file_path.parent.parent, "data")
    file_path = os.path.join(data_directory, "local-plan-document.csv")
    out_file_path = os.path.join(data_directory, "local-plan-document-copyable.csv")
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        with open(out_file_path, mode="w") as out_file:
            fieldnames = list(reader.fieldnames) + [
                "start-date",
                "end-date",
                "description",
                "status",
            ]
            fieldnames = [field.replace("-", "_") for field in fieldnames]
            writer = csv.DictWriter(out_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                fixed_row = {}
                try:
                    plan = LocalPlan.query.get(row["local-plan"])
                    if plan is None:
                        print(
                            "Skipping document",
                            row["reference"],
                            "as local plan not found",
                        )
                        continue

                    fixed_row["name"] = row["name"]
                    fixed_row["reference"] = row["reference"]
                    fixed_row["local_plan"] = row["local-plan"]
                    fixed_row["document_types"] = (
                        "{" + row["document-types"].replace("-", "_").upper() + "}"
                    )
                    fixed_row["document_url"] = row["document-url"]
                    fixed_row["documentation_url"] = row["documentation-url"]
                    fixed_row["start_date"] = ""
                    fixed_row["description"] = ""
                    fixed_row["status"] = "FOR_REVIEW"
                    writer.writerow(fixed_row)
                except Exception as e:
                    print(f"Error processing row {row['reference']}: {e}")
    print("Copyable file created")


@data_cli.command("set-orgs")
def set_orgs():
    subquery = (
        select(document_organisation.c.local_plan_document_reference)
        .where(
            document_organisation.c.local_plan_document_reference
            == LocalPlanDocument.reference
        )
        .exists()
    )
    query = select(LocalPlanDocument).where(not_(subquery))
    result = db.session.execute(query).scalars().all()

    for doc in result:
        doc.organisations = doc.plan.organisations
        db.session.add(doc)
        db.session.commit()


@data_cli.command("default-boundaries")
def set_default_boundaries():
    from application.models import Organisation

    orgs = Organisation.query.filter(Organisation.geometry.isnot(None)).all()
    for org in orgs:
        reference = org.statistical_geography
        boundary = LocalPlanBoundary.query.get(reference)
        if boundary is None:
            boundary = LocalPlanBoundary(
                reference=reference,
                name=f"{org.name} statistical geography",
                description="Default local plan boundary",
                geometry=org.geometry,
                geojson=org.geojson,
                plan_boundary_type="statistical-geography",
            )
            boundary.organisations.append(org)

        for plan in org.local_plans:
            if plan.local_plan_boundary is None:
                plan.local_plan_boundary = boundary.reference
                plan.boundary_status = Status.FOR_REVIEW
                boundary.local_plans.append(plan)
                print("Boundary set for plan", plan.reference)

        db.session.add(boundary)
        db.session.commit()

    print("Default boundaries set")


@data_cli.command("load-doc-types")
def load_doc_types():
    document_types_url = (
        "https://dluhc-datasets.planning-data.dev/dataset/local-plan-document-type.json"
    )
    try:
        resp = requests.get(document_types_url)
        resp.raise_for_status()
        data = resp.json()
        for doc_type in data["records"]:
            name = doc_type["name"]
            reference = doc_type["reference"]
            entry_date = doc_type["entry-date"]
            end_date = doc_type.get("end-date") if doc_type.get("end-date") else None
            sql = text(
                """
                    INSERT INTO local_plan_document_type (name, reference, entry_date, end_date)
                    VALUES (:name, :reference, :entry_date, :end_date)
                    ON CONFLICT (reference)
                    DO UPDATE
                    SET end_date = EXCLUDED.end_date;
                """
            )
            db.session.execute(
                sql,
                {
                    "name": name,
                    "reference": reference,
                    "entry_date": entry_date,
                    "end_date": end_date,
                },
            )
        db.session.commit()
    except requests.exceptions.HTTPError as e:
        print("Error fetching document types:", e)


@data_cli.command("load-event-types")
def load_event_types():
    event_types_url = (
        "https://dluhc-datasets.planning-data.dev/dataset/local-plan-event.json"
    )
    try:
        resp = requests.get(event_types_url)
        resp.raise_for_status()
        data = resp.json()
        for event_type in data["records"]:
            name = event_type["name"]
            reference = event_type["reference"]
            entry_date = event_type["entry-date"]
            end_date = (
                event_type.get("end-date") if event_type.get("end-date") else None
            )
            sql = text(
                """
                    INSERT INTO local_plan_event_type (name, reference, entry_date, end_date)
                    VALUES (:name, :reference, :entry_date, :end_date)
                    ON CONFLICT (reference)
                    DO UPDATE
                    SET end_date = EXCLUDED.end_date;
                """
            )
            db.session.execute(
                sql,
                {
                    "name": name,
                    "reference": reference,
                    "entry_date": entry_date,
                    "end_date": end_date,
                },
            )
        db.session.commit()
    except requests.exceptions.HTTPError as e:
        print("Error fetching event types:", e)


@data_cli.command("load-all")
@click.pass_context
def load_all(ctx):
    ctx.invoke(load_orgs)
    ctx.invoke(load_plans)
    ctx.invoke(load_boundaries)
    ctx.invoke(set_default_boundaries)
    ctx.invoke(load_doc_types)
    ctx.invoke(load_event_types)
    print("Data load complete")


@data_cli.command("load-db-backup")
def load_db_backup():
    import subprocess
    import sys
    import tempfile

    # check heroku cli installed
    result = subprocess.run(["which", "heroku"], capture_output=True, text=True)

    if result.returncode == 1:
        print("Heroku CLI is not installed. Please install it and try again.")
        sys.exit(1)

    # check heroku login
    result = subprocess.run(["heroku", "whoami"], capture_output=True, text=True)

    if "Error: not logged in" in result.stderr:
        print("Please login to heroku using 'heroku login' and try again.")
        sys.exit(1)

    print("Starting load data into", current_app.config["SQLALCHEMY_DATABASE_URI"])
    if (
        input(
            "Completing process will overwrite your local database. Enter 'y' to continue, or anything else to exit. "
        )
        != "y"
    ):
        print("Exiting without making any changes")
        sys.exit(0)

    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, "latest.dump")

        # get the latest dump from heroku
        result = subprocess.run(
            [
                "heroku",
                "pg:backups:download",
                "-a",
                "local-plans-explorer",
                "-o",
                path,
            ]
        )

        if result.returncode != 0:
            print("Error downloading the backup")
            sys.exit(1)

        # restore the dump to the local database
        subprocess.run(
            [
                "pg_restore",
                "--verbose",
                "--clean",
                "--no-acl",
                "--no-owner",
                "-h",
                "localhost",
                "-d",
                "local_plans",
                path,
            ]
        )
        print(
            "\n\nRestored the dump to the local database using pg_restore. You can ignore warnings from pg_restore."
        )

    print("Data loaded successfully")


@data_cli.command("set-org-websites")
def set_org_websites():
    base_url = "https://datasette.planning.data.gov.uk/digital-land/organisation.json"
    orgs = Organisation.query.all()
    for org in orgs:
        params = {
            "website__notblank": 1,
            "organisation__exact": org.organisation,
            "_shape": "array",
        }

        try:
            resp = requests.get(base_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            print(f"Fetching data for {org.organisation}")
            if len(data) > 0:
                website = data[0].get("website")
                if website:
                    org.website = website
                    db.session.add(org)
                    db.session.commit()
                    print(f"Set website {website} for {org.organisation}")
            else:
                print(f"No website found for {org.organisation}")
        except Exception as e:
            print(f"Error fetching data for {org.organisation}: {e}")
            continue


@data_cli.command("housing-numbers-timetable-data")
def load_housing_numbers_timetable_data():
    current_file_path = Path(__file__).resolve()
    data_directory = os.path.join(current_file_path.parent.parent, "data")
    file_path = os.path.join(data_directory, "local-plan-housing-numbers-prototype.csv")

    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            documentation_url = row.get("documentation_url")
            if documentation_url.endswith("/"):
                documentation_url = documentation_url[:-1]
            if documentation_url:
                plan = LocalPlan.query.filter(
                    LocalPlan.documentation_url == documentation_url
                ).first()
                if plan is not None and plan.timetable is None:
                    print("Updating plan timetable", plan.reference)
                    plan.period_start_date = (
                        (
                            row.get("period_start_date")
                            if row.get("period_start_date")
                            else None
                        ),
                    )
                    plan.period_end_date = (
                        (
                            row.get("period_end_date")
                            if row.get("period_end_date")
                            else None
                        ),
                    )
                    plan.adopted_date = (
                        row.get("adopted_date") if row.get("adopted_date") else None
                    )
                    db.session.add(plan)
                    dates = [
                        "published_date",
                        "sound_date",
                        "submitted_date",
                        "adopted_date",
                    ]
                    event_types = {
                        "published_date": "reg-19-publication-local-plan-published",
                        "sound_date": "planning‑inspectorate‑found‑sound",
                        "submitted_date": "submit‑plan‑for‑examination",
                        "adopted_date": "plan‑adopted",
                    }

                    events = []
                    for date_field in dates:
                        date_value = row.get(date_field)
                        if date_value:
                            event_type = LocalPlanEventType.query.filter(
                                LocalPlanEventType.reference == event_types[date_field]
                            ).one_or_none()
                            if event_type:
                                to_date = datetime.strptime(date_value, "%Y-%m-%d")
                                event = LocalPlanEvent(
                                    event_type=event_type.reference,
                                    event_date=date_value,
                                    event_day=to_date.day,
                                    event_month=to_date.month,
                                    event_year=to_date.year,
                                )
                                events.append(event)
                    if events:
                        reference = f"{plan.reference}-timetable"
                        timetable = LocalPlanTimetable(
                            reference=reference,
                            events=events,
                            local_plan=plan.reference,
                        )
                        plan.timetable = timetable
                        db.session.add(timetable)
                    db.session.commit()


def _make_reference(name, period_start_date, period_end_date, organisation):
    reference = slugify(name)
    if LocalPlan.query.get(reference) is None:
        return reference

    reference = slugify(f"{organisation.name}-{name}")
    if LocalPlan.query.get(reference) is None:
        return reference

    reference = slugify(f"{reference}-{period_start_date}-{period_end_date}")
    if LocalPlan.query.get(reference) is None:
        return reference

    reference = f"{reference}-{datetime.now().strftime('%Y-%m-%d')}"
    if LocalPlan.query.get(reference) is None:
        return reference

    return reference


@data_cli.command("migrate-doc-types")
def migrate_doc_types():
    documents = LocalPlanDocument.query.filter(
        LocalPlanDocument.document_types.isnot(None)
    ).all()
    for document in documents:
        updated_document_types = []
        for doc_type in document.document_types:
            ref = doc_type.lower().replace("_", "-")
            if ref == "financial-viability-study":
                ref = "viability-assessment"
            document_type = LocalPlanDocumentType.query.get(ref)
            if document_type is None:
                print(
                    f"No matching document type found for {ref} for document {document.reference}"
                )
            else:
                updated_document_types.append(document_type.reference)
        if updated_document_types:
            document.document_types = updated_document_types
            db.session.add(document)
            db.session.commit()
            print(f"Updated document types for {document.reference}")


@data_cli.command("seed-timetable")
def seed_timetable():
    current_file_path = Path(__file__).resolve()
    data_directory = os.path.join(current_file_path.parent.parent, "data")
    file_path = os.path.join(data_directory, "timetable-seed-data.csv")

    records = {}

    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            local_plan_reference = row.get("local-plan", "").strip()
            plan = LocalPlan.query.get(local_plan_reference)
            if plan is None:
                print(f"Local plan not found for reference {local_plan_reference}")
                continue
            reference = row["reference"]
            if reference not in records:
                records[reference] = [row]
            else:
                records[reference].append(row)

    for reference, rows in records.items():
        local_plan_reference = rows[0]["local-plan"]
        plan = LocalPlan.query.get(local_plan_reference)
        if plan is None:
            print(f"Local plan not found for reference {reference}")
            continue
        if plan.timetable is None:
            print(f"Creating timetable for {local_plan_reference}")
            timetable_name = f"{plan.name} timetable"
            timetable_reference = f"{plan.reference}-timetable"
            plan.timetable = LocalPlanTimetable(
                reference=timetable_reference, name=timetable_name, events=[]
            )
            db.session.add(plan)
            db.session.commit()

        local_plan_event = LocalPlanEvent.query.get(reference)
        if local_plan_event is not None:
            print(f"Event {reference} already exists")
            continue
        event_reference = f"{plan.timetable.reference}-{len(plan.timetable.events)}"
        local_plan_event = LocalPlanEvent(reference=event_reference)
        data = {}
        for row in rows:
            event_type = LocalPlanEventType.query.get(row["local-plan-event"])
            if event_type is None:
                print(f"Event type not found for reference {row['event-type']}")
                continue
            date_fields = row.get("event-date").split("-")
            if len(date_fields) == 3:
                year, month, day = date_fields
            if len(date_fields) == 2:
                year, month = date_fields
                day = ""
            if len(date_fields) == 1 and date_fields[0] != "":
                year = date_fields[0]
                month, day = "", ""
            data[event_type.reference.replace("-", "_")] = {
                "day": day,
                "month": month,
                "year": year,
            }
        event_category = _get_event_category(event_type.reference)
        local_plan_event.event_category = event_category
        local_plan_event.event_data = data
        plan.timetable.events.append(local_plan_event)
        db.session.add(plan.timetable)
        db.session.commit()


def _get_event_category(event_type):
    if event_type == "timetable-published":
        return EventCategory.ESTIMATED_EXAMINATION_AND_ADOPTION
    if "estimated" in event_type and "reg-18" in event_type:
        return EventCategory.ESTIMATED_REGULATION_18
    elif "estimated" in event_type and "reg-19" in event_type:
        return EventCategory.ESTIMATED_REGULATION_19
    elif "estimated" in event_type:
        return EventCategory.ESTIMATED_EXAMINATION_AND_ADOPTION
    elif "reg-18" in event_type:
        return EventCategory.REGULATION_18
    elif "reg-19" in event_type:
        return EventCategory.REGULATION_19
    else:
        return EventCategory.EXAMINATION_AND_ADOPTION
