from datetime import datetime

from flask import render_template, request
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import (
    Field,
    RadioField,
    StringField,
    TextAreaField,
    URLField,
    ValidationError,
)
from wtforms.validators import DataRequired, Optional, Regexp

from application.models import EventCategory


class LocalPlanForm(FlaskForm):
    def validate_period_start_date(form, field):
        if field.data and not field.data.isdigit():
            raise ValidationError("Start date must be numeric.")

    def validate_period_end_date(form, field):
        if field.data and not field.data.isdigit():
            raise ValidationError("End date must be numeric.")

    name = StringField("Name of plan", validators=[DataRequired()])
    organisations = StringField("Organisation", validators=[DataRequired()])
    description = TextAreaField("Brief description of plan", validators=[Optional()])
    period_start_date = StringField(
        "Plan start date",
        validators=[Optional()],
        description="The year the plan starts, for example, 2022",
    )
    period_end_date = StringField(
        "Plan end date",
        validators=[Optional()],
        description="The year the plan ends, for example, 2045",
    )
    documentation_url = URLField(
        "URL for plan information",
        validators=[
            DataRequired(),
            Regexp("^https?://", message="URL must start with http or https"),
        ],
    )
    adopted_date_year = StringField("Adopted date year", validators=[Optional()])
    adopted_date_month = StringField("Adopted date month", validators=[Optional()])
    adopted_date_day = StringField("Adopted date day", validators=[Optional()])

    status = RadioField("Status", validators=[Optional()])


class DatePartsInputWidget:
    def __call__(self, field, **kwargs):
        return Markup(
            render_template("partials/date-parts-form.html", field=field, **kwargs)
        )


class DatePartField(Field):
    widget = DatePartsInputWidget()

    def _value(self):
        if self.data:
            return {
                "day": self.data.get("day", ""),
                "month": self.data.get("month", ""),
                "year": self.data.get("year", ""),
            }
        return {"day": "", "month": "", "year": ""}

    def process_formdata(self, valuelist):
        day_str = request.form.get(f"{self.name}_day", "")
        month_str = request.form.get(f"{self.name}_month", "")
        year_str = request.form.get(f"{self.name}_year", "")

        day = int(day_str) if day_str else None
        month = int(month_str) if month_str else None
        year = int(year_str) if year_str else None

        if (day or month) and not year:
            raise ValidationError(
                "Invalid date: a year is required if day or month is provided."
            )

        try:
            if year:
                if month and day:
                    datetime(year, month, day)
                elif month:
                    datetime(year, month, 1)
                else:
                    datetime(year, 1, 1)
            else:
                raise ValidationError("Invalid date: at least a year is required.")
        except ValueError:
            raise ValidationError(
                "Invalid date input: please check day, month, and year."
            )

        self.data = {
            "day": day_str,
            "month": month_str,
            "year": year_str,
        }

    def process_data(self, value):
        if isinstance(value, dict):
            self.data = {
                "day": value.get("day", ""),
                "month": value.get("month", ""),
                "year": value.get("year", ""),
            }
        else:
            self.data = {"day": "", "month": "", "year": ""}


class EstimatedRegulation18Form(FlaskForm):
    estimated_reg_18_draft_local_plan_published = DatePartField(
        "Draft local plan published", validators=[Optional()]
    )
    estimated_reg_18_public_consultation_start = DatePartField(
        "Regulation 18 consultation start", validators=[Optional()]
    )
    estimated_reg_18_public_consultation_end = DatePartField(
        "Regulation 18 consultation end", validators=[Optional()]
    )
    notes = TextAreaField("What does the consultation cover?", validators=[Optional()])

    def __init__(self, obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request.method == "GET" and obj:
            self.estimated_reg_18_draft_local_plan_published.process_data(
                obj.get("estimated_reg_18_draft_local_plan_published")
            )
            self.estimated_reg_18_public_consultation_start.process_data(
                obj.get("estimated_reg_18_public_consultation_start")
            )
            self.estimated_reg_18_public_consultation_end.process_data(
                obj.get("estimated_reg_18_public_consultation_end")
            )
            self.notes.data = obj.get("notes", "")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        date_fields = [
            self.estimated_reg_18_draft_local_plan_published,
            self.estimated_reg_18_public_consultation_start,
            self.estimated_reg_18_public_consultation_end,
        ]
        if not any(field.data.get("year") for field in date_fields if field.data):
            date_error = "At least one of the dates should have at least a year"
            self.estimated_reg_18_draft_local_plan_published.errors.append(date_error)
            self.estimated_reg_18_public_consultation_start.errors.append(date_error)
            self.estimated_reg_18_public_consultation_end.errors.append(date_error)
            return False

        return True

    def get_error_summary(self):
        errors = []
        for field in [
            self.estimated_reg_18_draft_local_plan_published,
            self.estimated_reg_18_public_consultation_start,
            self.estimated_reg_18_public_consultation_end,
        ]:
            if field.errors:
                errors.extend(field.errors)
        return errors[0] if errors else None


class EstimatedRegulation19Form(FlaskForm):
    estimated_reg_19_publication_local_plan_published = DatePartField(
        "Publication local plan published", validators=[Optional()]
    )
    estimated_reg_19_public_consultation_start = DatePartField(
        "Regulation 19 consultation start", validators=[Optional()]
    )
    estimated_reg_19_public_consultation_end = DatePartField(
        "Regulation 19 consultation end", validators=[Optional()]
    )
    notes = TextAreaField("What does the consultation cover?", validators=[Optional()])

    def __init__(self, obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request.method == "GET" and obj:
            self.estimated_reg_19_publication_local_plan_published.process_data(
                obj.get("estimated_reg_19_publication_local_plan_published")
            )
            self.estimated_reg_19_public_consultation_start.process_data(
                obj.get("estimated_reg_19_public_consultation_start")
            )
            self.estimated_reg_19_public_consultation_end.process_data(
                obj.get("estimated_reg_19_public_consultation_end")
            )
            self.notes.data = obj.get("notes", "")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        date_fields = [
            self.estimated_reg_19_publication_local_plan_published,
            self.estimated_reg_19_public_consultation_start,
            self.estimated_reg_19_public_consultation_end,
        ]
        if not any(field.data.get("year") for field in date_fields if field.data):
            date_error = "At least one of the dates should have at least a year"
            self.estimated_reg_19_publication_local_plan_published.errors.append(
                date_error
            )
            self.estimated_reg_19_public_consultation_start.errors.append(date_error)
            self.estimated_reg_19_public_consultation_end.errors.append(date_error)
            return False

        return True

    def get_error_summary(self):
        errors = []
        for field in [
            self.estimated_reg_19_publication_local_plan_published,
            self.estimated_reg_19_public_consultation_start,
            self.estimated_reg_19_public_consultation_end,
        ]:
            if field.errors:
                errors.extend(field.errors)
        return errors[0] if errors else None


class EsitmatedExaminationAndAdoptionForm(FlaskForm):
    estimated_submit_plan_for_examination = DatePartField(
        "Submit plan for examination", validators=[Optional()]
    )
    estimated_plan_adoption_date = DatePartField(
        "Adoption of local plan", validators=[Optional()]
    )

    def __init__(self, obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request.method == "GET" and obj:
            self.estimated_submit_plan_for_examination.process_data(
                obj.get("estimated_submit_plan_for_examination")
            )
            self.estimated_plan_adoption_date.process_data(
                obj.get("estimated_plan_adoption_date")
            )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        date_fields = [
            self.estimated_submit_plan_for_examination,
            self.estimated_plan_adoption_date,
        ]
        if not any(field.data.get("year") for field in date_fields if field.data):
            date_error = "At least one of the dates should have at least a year"
            self.estimated_submit_plan_for_examination.errors.append(date_error)
            self.estimated_plan_adoption_date.errors.append(date_error)
            return False

        return True

    def get_error_summary(self):
        errors = []
        for field in [
            self.estimated_submit_plan_for_examination,
            self.estimated_plan_adoption_date,
        ]:
            if field.errors:
                errors.extend(field.errors)
        return errors[0] if errors else None


class Regulation18Form(FlaskForm):
    reg_18_draft_local_plan_published = DatePartField(
        "Draft local plan published", validators=[Optional()]
    )
    reg_18_public_consultation_start = DatePartField(
        "Regulation 18 consultation start", validators=[Optional()]
    )
    reg_18_public_consultation_end = DatePartField(
        "Regulation 18 consultation end", validators=[Optional()]
    )
    notes = TextAreaField("What does the consultation cover?", validators=[Optional()])

    def __init__(self, obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request.method == "GET" and obj:
            self.reg_18_draft_local_plan_published.process_data(
                obj.get("reg_18_draft_local_plan_published")
            )
            self.reg_18_public_consultation_start.process_data(
                obj.get("reg_18_public_consultation_start")
            )
            self.reg_18_public_consultation_end.process_data(
                obj.get("reg_18_public_consultation_end")
            )
            self.notes.data = obj.get("notes", "")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        date_fields = [
            self.reg_18_draft_local_plan_published,
            self.reg_18_public_consultation_start,
            self.reg_18_public_consultation_end,
        ]
        if not any(field.data.get("year") for field in date_fields if field.data):
            date_error = "At least one of the dates should have at least a year"
            self.reg_18_draft_local_plan_published.errors.append(date_error)
            self.reg_18_public_consultation_start.errors.append(date_error)
            self.reg_18_public_consultation_end.errors.append(date_error)
            return False

        return True

    def get_error_summary(self):
        errors = []
        for field in [
            self.reg_18_draft_local_plan_published,
            self.reg_18_public_consultation_start,
            self.reg_18_public_consultation_end,
        ]:
            if field.errors:
                errors.extend(field.errors)
        return errors[0] if errors else None


class Regulation19Form(FlaskForm):
    reg_19_publication_local_plan_published = DatePartField(
        "Publication local plan published", validators=[Optional()]
    )
    reg_19_public_consultation_start = DatePartField(
        "Regulation 19 consultation start", validators=[Optional()]
    )
    reg_19_public_consultation_end = DatePartField(
        "Regulation 19 consultation end", validators=[Optional()]
    )
    notes = TextAreaField("What does the consultation cover?", validators=[Optional()])

    def __init__(self, obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request.method == "GET" and obj:
            self.reg_19_publication_local_plan_published.process_data(
                obj.get("reg_19_publication_local_plan_published")
            )
            self.reg_19_public_consultation_start.process_data(
                obj.get("reg_19_public_consultation_start")
            )
            self.reg_19_public_consultation_end.process_data(
                obj.get("reg_19_public_consultation_end")
            )
            self.notes.data = obj.get("notes", "")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        date_fields = [
            self.reg_19_publication_local_plan_published,
            self.reg_19_public_consultation_start,
            self.reg_19_public_consultation_end,
        ]
        if not any(field.data.get("year") for field in date_fields if field.data):
            date_error = "At least one of the dates should have at least a year"
            self.reg_19_publication_local_plan_published.errors.append(date_error)
            self.reg_19_public_consultation_start.errors.append(date_error)
            self.reg_19_public_consultation_end.errors.append(date_error)
            return False

        return True

    def get_error_summary(self):
        errors = []
        for field in [
            self.reg_19_publication_local_plan_published,
            self.reg_19_public_consultation_start,
            self.reg_19_public_consultation_end,
        ]:
            if field.errors:
                errors.extend(field.errors)
        return errors[0] if errors else None


class PlanningInspectorateExaminationForm(FlaskForm):
    submit_plan_for_examination = DatePartField(
        "Plan submitted", validators=[Optional()]
    )
    planning_inspectorate_examination_start = DatePartField(
        "Examination start date", validators=[Optional()]
    )
    planning_inspectorate_examination_end = DatePartField(
        "Examination end date", validators=[Optional()]
    )

    def __init__(self, obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request.method == "GET" and obj:
            self.submit_plan_for_examination.process_data(
                obj.get("submit_plan_for_examination")
            )
            self.planning_inspectorate_examination_start.process_data(
                obj.get("planning_inspectorate_examination_start")
            )
            self.planning_inspectorate_examination_end.process_data(
                obj.get("planning_inspectorate_examination_end")
            )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        date_fields = [
            self.submit_plan_for_examination,
            self.planning_inspectorate_examination_start,
            self.planning_inspectorate_examination_end,
        ]
        if not any(field.data.get("year") for field in date_fields if field.data):
            date_error = "At least one of the dates should have at least a year"
            self.submit_plan_for_examination.errors.append(date_error)
            self.planning_inspectorate_examination_start.errors.append(date_error)
            self.planning_inspectorate_examination_end.errors.append(date_error)
            return False

        return True

    def get_error_summary(self):
        errors = []
        for field in [
            self.submit_plan_for_examination,
            self.planning_inspectorate_examination_start,
            self.planning_inspectorate_examination_end,
        ]:
            if field.errors:
                errors.extend(field.errors)
        return errors[0] if errors else None


class PlanningInspectorateFindingsForm(FlaskForm):
    planning_inspectorate_found_sound = DatePartField(
        "Planning inspectorate found sound", validators=[Optional()]
    )
    inspector_report_published = DatePartField(
        "Report published", validators=[Optional()]
    )
    plan_adpoted = DatePartField("Plan adopted", validators=[Optional()])

    def __init__(self, obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request.method == "GET" and obj:
            self.planning_inspectorate_found_sound.process_data(
                obj.get("planning_inspectorate_found_sound")
            )
            self.inspector_report_published.process_data(
                obj.get("inspector_report_published")
            )
            self.plan_adpoted.process_data(obj.get("plan_adpoted"))

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        date_fields = [
            self.planning_inspectorate_found_sound,
            self.inspector_report_published,
            self.plan_adpoted,
        ]
        if not any(field.data.get("year") for field in date_fields if field.data):
            date_error = "At least one of the dates should have at least a year"
            self.planning_inspectorate_found_sound.errors.append(date_error)
            self.inspector_report_published.errors.append(date_error)
            self.plan_adpoted.errors.append(date_error)
            return False

        return True

    def get_error_summary(self):
        errors = []
        for field in [
            self.planning_inspectorate_found_sound,
            self.inspector_report_published,
            self.plan_adpoted,
        ]:
            if field.errors:
                errors.extend(field.errors)
        return errors[0] if errors else None


def get_event_form(event_category, obj=None):
    match event_category:
        case EventCategory.ESTIMATED_REGULATION_18:
            return EstimatedRegulation18Form(obj=obj)
        case EventCategory.ESTIMATED_REGULATION_19:
            return EstimatedRegulation19Form(obj=obj)
        case EventCategory.ESTIMATED_EXAMINATION_AND_ADOPTION:
            return EsitmatedExaminationAndAdoptionForm(obj=obj)
        case EventCategory.REGULATION_18:
            return Regulation18Form(obj=obj)
        case EventCategory.REGULATION_19:
            return Regulation19Form(obj=obj)
        case EventCategory.PLANNING_INSPECTORATE_EXAMINATION:
            return PlanningInspectorateExaminationForm(obj=obj)
        case EventCategory.PLANNING_INSPECTORATE_FINDINGS:
            return PlanningInspectorateFindingsForm(obj=obj)
        case _:
            raise ValueError("Invalid event_category.")
