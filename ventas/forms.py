from django import forms

class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label='Archivo CSV', help_text='Seleccione un archivo CSV de ventas')
