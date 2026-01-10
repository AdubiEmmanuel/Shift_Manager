from django import forms

from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ("start_datetime", "end_datetime", "reason")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = "mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " " + base_class).strip()
