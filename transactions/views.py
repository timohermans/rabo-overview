from datetime import date
from io import TextIOWrapper
from transactions.utils.fileparser import AnonymousStorageHandler, FileParser

from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import render

from .forms import TransactionFileForm
from .models import Transaction
from .utils.date import get_start_end_date_from


class TransactionListView(LoginRequiredMixin, ListView):
    context_object_name = "transactions"
    model = Transaction
    paginate_by = 20

    def get_queryset(self):
        month = self.get_date_for_transactions()
        date_range = get_start_end_date_from(month)
        return Transaction.objects.filter(
            date__gte=date_range[0], date__lte=date_range[1], user=self.request.user
        ).order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.get_date_for_transactions()
        context["month"] = month
        context["top_incomes"] = Transaction.statistics.top_incomes(
            month, self.request.user
        )
        context["top_expenses"] = Transaction.statistics.top_expenses(
            month, self.request.user
        )
        overview = Transaction.statistics.get_external_totals(month, self.request.user)
        context["sum_incomes"] = overview["incomes"]
        context["sum_expenses"] = overview["expenses"]
        return context

    def get_date_for_transactions(self) -> date:
        month = date.today() - relativedelta(months=1)
        if "month" in self.request.GET:
            month = date.fromisoformat(self.request.GET.get("month"))
        return month


class UploadTransactionsFormView(LoginRequiredMixin, FormView):
    template_name = "transactions/upload.html"
    success_url = "/transactions"
    form_class = TransactionFileForm

    def form_valid(self, form):
        file = TextIOWrapper(form.files["file"].file, encoding="latin1")
        result = Transaction.creators.create_bulk_from(file, self.request.user)

        return super().form_valid(form)


class UploadAnonymousTransactionsFormView(FormView):
    # TODO: Actually test the implementation
    template_name = "transactions/anonymous_upload.html"
    form_class = TransactionFileForm
    success_url = "/"

    def form_valid(self, form):
        file = TextIOWrapper(form.files["file"].file, encoding="latin1")
        results = FileParser(AnonymousStorageHandler()).parse(file)
        return render(
            self.request,
            UploadAnonymousTransactionsFormView.template_name,
            {"results": results},
        )
