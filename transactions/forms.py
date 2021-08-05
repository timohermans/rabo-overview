from django import forms
from django.core.validators import FileExtensionValidator


class TransactionFileForm(forms.Form):
    # TODO: Validate the csv file properly
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["csv"])])
