from django import forms
from community.models import Demand, Offering, Grievance


class AskFor(forms.ModelForm):
    
    class Meta:
        model = Demand
        exclude = ['feedback', 'available', 'timeStamp', 'price', 'borrower']
        
    def __init__(self, *args, **kwargs):
        super(AskFor, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'col-12 my-3', 'style': 'border-radius: 1px; border: 1px solid grey'})
            if field_name == 'description':
                field.widget.attrs.update({'rows': '5'})  # Adjusting the rows for the description field


class Offer(forms.ModelForm):
    
    class Meta:
        model = Offering
        exclude = ['feedback', 'available', 'timeStamp', 'price', 'lender']
        
    def __init__(self, *args, **kwargs):
        super(Offer, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'col-12 my-3', 'style': 'border-radius: 1px; border: 1px solid grey'})
            if field_name == 'description':
                field.widget.attrs.update({'rows': '5'})  # Adjusting the rows for the description field


class PutGrievance(forms.ModelForm):
    
    class Meta:
        model = Grievance
        exclude = ['count', 'resolved' ,'timeStamp', 'defaulter', 'deal']
        
    def __init__(self, *args, **kwargs):
        super(PutGrievance, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'col-12 my-3', 'style': 'border-radius: 1px; border: 1px solid grey'})
            if field_name == 'description':
                field.widget.attrs.update({'rows': '5'})  # Adjusting the rows for the description field

