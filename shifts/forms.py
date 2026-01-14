from django import forms

from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ("start_datetime", "end_datetime", "reason")
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Accept html5 datetime-local input format
        self.fields["start_datetime"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_datetime"].input_formats = ["%Y-%m-%dT%H:%M"]
        base_class = "mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " " + base_class).strip()

        # If the form is unbound and editing an instance, format initial datetimes
        if not self.is_bound and hasattr(self, "instance") and self.instance is not None:
            inst = self.instance
            if getattr(inst, "start_datetime", None):
                try:
                    self.initial["start_datetime"] = inst.start_datetime.strftime("%Y-%m-%dT%H:%M")
                except Exception:
                    pass
            if getattr(inst, "end_datetime", None):
                try:
                    self.initial["end_datetime"] = inst.end_datetime.strftime("%Y-%m-%dT%H:%M")
                except Exception:
                    pass
