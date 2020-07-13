from django.http import Http404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from django_ledger.forms.ledger import LedgerModelCreateForm, LedgerModelUpdateForm
from django_ledger.models.entity import EntityModel
from django_ledger.models.ledger import LedgerModel


# Ledger Views ----
class LedgerModelListView(ListView):
    context_object_name = 'ledgers'
    template_name = 'django_ledger/ledger_list.html'
    extra_context = {
        'page_title': _('ledgers'),
        'header_title': _('entity ledgers')
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('entity ledgers')
        context['header_title'] = _('entity ledgers')
        return context

    def get_queryset(self):
        sort = self.request.GET.get('sort')
        if not sort:
            sort = '-updated'
        entity_slug = self.kwargs.get('entity_slug')
        return LedgerModel.objects.for_entity(
            entity_slug=entity_slug,
            user_model=self.request.user
        ).order_by(sort)


class LedgerModelCreateView(CreateView):
    template_name = 'django_ledger/ledger_create.html'
    form_class = LedgerModelCreateForm

    def form_valid(self, form):
        entity_qs = EntityModel.objects.for_user(user_model=self.request.user)
        entity = entity_qs.get(slug__iexact=self.kwargs['entity_slug'])
        form.instance.entity = entity
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _l('create ledger')
        context['header_title'] = _l('create ledger')
        return context

    def get_initial(self):
        slug = self.kwargs.get('entity_slug')
        return {
            'entity': EntityModel.objects.get(slug=slug)
        }

    def get_success_url(self):
        return reverse('django_ledger:ledger-list',
                       kwargs={
                           'entity_slug': self.kwargs.get('entity_slug')
                       })


class LedgerModelUpdateView(UpdateView):
    template_name = 'django_ledger/ledger_update.html'
    form_class = LedgerModelUpdateForm
    context_object_name = 'ledger'
    slug_url_kwarg = 'ledger_pk'

    def get_slug_field(self):
        return 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('update ledger: ') + self.object.name
        context['header_title'] = _('update ledger: ') + self.object.name
        return context

    def get_queryset(self):
        entity_slug = self.kwargs['entity_slug']
        return LedgerModel.objects.for_entity(
            user_model=self.request.user,
            entity_slug=entity_slug
        )

    def get_success_url(self):
        return reverse('django_ledger:ledger-list',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug']
                       })


class LedgerBalanceSheetView(DetailView):
    context_object_name = 'ledger'
    template_name = 'django_ledger/balance_sheet.html'
    slug_url_kwarg = 'ledger_pk'

    def get_slug_field(self):
        return 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Ledger BS: ') + self.object.name
        context['header_title'] = _('Ledger BS: ') + self.object.name
        return context

    def get_queryset(self):
        entity_slug = self.kwargs['entity_slug']
        return LedgerModel.objects.for_entity(
            user_model=self.request.user,
            entity_slug=entity_slug)


class LedgerIncomeStatementView(DetailView):
    context_object_name = 'ledger'
    template_name = 'django_ledger/income_statement.html'
    slug_url_kwarg = 'ledger_pk'

    def get_slug_field(self):
        return 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Ledger IC: ') + self.object.name
        context['header_title'] = _('Ledger IC: ') + self.object.name
        return context

    def get_queryset(self):
        entity_slug = self.kwargs['entity_slug']
        return LedgerModel.objects.for_entity(
            user_model=self.request.user,
            entity_slug=entity_slug)
