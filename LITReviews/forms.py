from django import forms
from django.forms import RadioSelect
from LITReviews.models import Review
from LITReviews.models import Ticket
from django.core.validators import MinValueValidator, MaxValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import InlineRadios
from django.urls import reverse_lazy


class TicketForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}), required=False
    )

    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        # Set custom labels for the fieldss
        self.fields["title"].label = "Titre:"
        self.fields["description"].label = "Description:"
        self.fields["image"].label = "Image:"

        self.helper.form_action = reverse_lazy("post")
        self.helper.add_input(Submit("Envoyer", "Envoyer"))


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(int(i), int(i)) for i in range(1, 6)],
        widget=RadioSelect,
    )
    headline = forms.CharField(max_length=128)
    body = forms.CharField(
        max_length=8192, widget=forms.Textarea(attrs={"rows": 4}), required=False
    )

    class Meta:
        model = Review
        fields = ["rating", "headline", "body"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        # Set custom labels for the fields
        self.fields["rating"].label = "Note:"
        self.fields["headline"].label = "Titre de la critique:"
        self.fields["body"].label = "Commentaire:"

        self.helper.form_action = reverse_lazy("post")
        self.helper.add_input(Submit("Envoyer", "Envoyer"))


class ReviewTicketForm(forms.ModelForm):
    # Fields from the Ticket model
    title = forms.CharField(max_length=128)
    description = forms.CharField(
        max_length=2048, widget=forms.Textarea(attrs={"rows": 2}), required=False
    )
    image = forms.ImageField(required=False)

    # Fields from the Review model
    rating = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], required=False
    )
    headline = forms.CharField(max_length=128)
    body = forms.CharField(
        max_length=8192, widget=forms.Textarea(attrs={"rows": 4}), required=False
    )

    class Meta:
        model = Ticket  # This is required, but we won't use it in the form.
        fields = ["title"]  # No need to specify any fields here.
        blank = {"title": False}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        # Set custom labels for the fields
        self.fields["title"].label = "Titre:"
        self.fields["description"].label = "Description:"
        self.fields["image"].label = "Image:"
        self.fields["rating"].label = "Note:"
        self.fields["body"].label = "Commentaire:"
        self.fields["headline"].label = "Titre de la critique:"

        self.helper.add_input(Submit("submit", "Envoyer", css_class="button white"))

    def make_review_ticket(self, commit=True):
        # Save the Ticket and Review instances separately.
        ticket = Ticket(
            title=self.cleaned_data["title"],
            description=self.cleaned_data["description"],
            image=self.cleaned_data["image"],
        )
        review = Review(
            ticket=ticket,
            rating=self.cleaned_data["rating"],
            headline=self.cleaned_data["headline"],
            body=self.cleaned_data["body"],
        )
        return ticket, review
