"""
Django Ledger created by Miguel Sanda <msanda@arrobalytics.com>.
Copyright© EDMA Group Inc licensed under the GPLv3 Agreement.

Contributions to this module:
    * Miguel Sanda <msanda@arrobalytics.com>

The LedgerModel is the heart of Django Ledger. It is a self-contained unit of accounting that implements a
double-entry accounting system capable of creating and managing transactions into the ledger and producing any financial
statements. In essence, an EntityModel is made of a collection of LedgerModels that drive the whole bookkeeping process.
Each LedgerModel is independent and they can operate as an individual or as a group.

Each LedgerModel encapsulates a collection of JournalEntryModels, which in turn hold a collection of TransactionModels.
LedgerModels can be used to represent any part of the EntityModel and can be extended to add additional functionality
and custom logic that drives how transactions are recorded into the books. One example of this is the LedgerWrapperMixIn
(see django_ledger.models.mixins.LedgerWrapperMixIn), which is the foundation of LedgerModel abstractions such as the
BillModel, InvoiceModel, PurchaseOrderModel and EstimateModel. Extending the LedgerModel can add additional
functionality necessary to implement industry-specific functionality to almost anything you can think of. Examples:
Farming Equipment, Real Estate, Investment Portfolio, etc.

Also, the LedgerModel inherits functionality from the all mighty IOMixIn (see django_ledger.io.io_mixin.IOMixIn),
which is the class responsible for making accounting queries to the Database in an efficient and performing way.
The digest() method executes all necessary aggregations and optimizations in order to push as much work to the Database
layer as possible in order to minimize the amount of data being pulled for analysis into the Python memory.

The Django Ledger core model follows the following structure: \n
EntityModel -< LedgerModel -< JournalEntryModel -< TransactionModel
"""
from datetime import date
from string import ascii_lowercase, digits
from typing import Optional
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_ledger.io import IOMixIn
from django_ledger.models import lazy_loader
from django_ledger.models.mixins import CreateUpdateMixIn

LEDGER_ID_CHARS = ascii_lowercase + digits


class LedgerModelValidationError(ValidationError):
    pass


class LedgerModelQuerySet(models.QuerySet):
    """
    Custom defined LedgerModel QuerySet.
    """

    def posted(self):
        """
        Filters the QuerySet to only posted LedgerModel.

        Returns
        -------
        LedgerModelQuerySet
            A QuerySet with applied filters.
        """
        return self.filter(posted=True)

    def hidden(self):
        return self.filter(hidden=True)

    def visible(self):
        return self.filter(hidden=False)


class LedgerModelManager(models.Manager):
    """
    A custom-defined LedgerModelManager that implements custom QuerySet methods related to the LedgerModel.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('entity')

    def for_entity(self, entity_slug, user_model):
        """
        Returns a QuerySet of LedgerModels associated with a specific EntityModel & UserModel.
        May pass an instance of EntityModel or a String representing the EntityModel slug.

        Parameters
        ----------
        entity_slug: str or EntityModel
            The entity slug or EntityModel used for filtering the QuerySet.
        user_model
            The request UserModel to check for privileges.

        Returns
        -------
        LedgerModelQuerySet
            A Filtered LedgerModelQuerySet.
        """
        qs = self.get_queryset()
        if isinstance(entity_slug, lazy_loader.get_entity_model()):
            return qs.filter(
                Q(entity=entity_slug) &
                (
                        Q(entity__admin=user_model) |
                        Q(entity__managers__in=[user_model])
                )
            )
        return qs.filter(
            Q(entity__slug__exact=entity_slug) &
            (
                    Q(entity__admin=user_model) |
                    Q(entity__managers__in=[user_model])
            )
        )


class LedgerModelAbstract(CreateUpdateMixIn, IOMixIn):
    """
    Base implmentation of the LedgerModel.

    Attributes
    ----------
    uuid: UUID
        This is a unique primary key generated for the table. The default value of this field is uuid4().
    name: str
        Human-readable name of the LedgerModel. Maximum 150 characters.
    entity: EntityModel
        The EntityModel associated with the LedgerModel instance.
    posted: bool
        Determines if the LedgerModel is posted. Defaults to False. Mandatory.
    locked: bool
        Determines if the LedgerModel is locked. Defaults to False. Mandatory.
    hidden: bool
        Determines if the LedgerModel is hidden. Defaults to False. Mandatory.
    """
    uuid = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('Ledger Name'))

    # todo: rename to entity_model...
    entity = models.ForeignKey('django_ledger.EntityModel',
                               editable=False,
                               on_delete=models.CASCADE,
                               verbose_name=_('Ledger Entity'))
    posted = models.BooleanField(default=False, verbose_name=_('Posted Ledger'))
    locked = models.BooleanField(default=False, verbose_name=_('Locked Ledger'))
    hidden = models.BooleanField(default=False, verbose_name=_('Hidden Ledger'))

    objects = LedgerModelManager.from_queryset(queryset_class=LedgerModelQuerySet)()

    class Meta:
        abstract = True
        ordering = ['-created']
        verbose_name = _('Ledger')
        verbose_name_plural = _('Ledgers')
        indexes = [
            models.Index(fields=['entity']),
            models.Index(fields=['entity', 'posted']),
            models.Index(fields=['entity', 'locked']),
        ]

    def __str__(self):
        return self.name

    def is_posted(self) -> bool:
        """
        Determines if the LedgerModel instance is posted.

        Returns
        -------
        bool
            True if posted, else False.
        """
        return self.posted is True

    def is_locked(self) -> bool:
        """
        Determines if the LedgerModel instance is locked.

        Returns
        -------
        bool
            True if locked, else False.
        """
        return self.locked is True

    def is_hidden(self) -> bool:
        """
        Determines if the LedgerModel instance is hidden.

        Returns
        -------
        bool
            True if hidden, else False.
        """
        return self.hidden is True

    def can_post(self) -> bool:
        """
        Determines if the LedgerModel can be marked as posted.

        Returns
        -------
        bool
            True if can be posted, else False.
        """
        return self.posted is False

    def can_unpost(self) -> bool:
        """
        Determines if the LedgerModel can be un-posted.

        Returns
        -------
        bool
            True if can be un-posted, else False.
        """
        return all([
            self.is_posted(),
            not self.is_locked()
        ])

    def can_lock(self) -> bool:
        """
        Determines if the LedgerModel can be locked.

        Returns
        -------
        bool
            True if can be locked, else False.
        """
        return all([
            not self.locked,
            self.posted
        ])

    def can_unlock(self, **kwargs) -> bool:
        """
        Determines if the LedgerModel can be un-locked.

        Returns
        -------
        bool
            True if can be un-locked, else False.
        """
        return all([
            self.locked,
            self.posted
        ])

    def can_delete(self) -> bool:
        if not self.is_locked() and not self.is_posted():
            return True
        return False

    def delete(self, **kwargs):

        if not self.can_delete():
            raise LedgerModelValidationError(
                message=_(f'LedgerModel {self.name} cannot be deleted because posted is {self.is_posted()} '
                          f'and locked is {self.is_locked()}')
            )
        earliest_je_timestamp = self.journal_entries.posted().order_by('-timestamp').values('timestamp').first()
        if earliest_je_timestamp is not None:
            earliest_date = earliest_je_timestamp['timestamp'].date()
            if earliest_date <= self.entity.last_closing_date:
                raise LedgerModelValidationError(
                    message=_(
                        f'Journal Entries with date {earliest_date} cannot be deleted because of lastest closing '
                        f'entry on {self.get_entity_last_closing_date()}')
                )

        return super().delete(**kwargs)

    def post(self, commit: bool = False, **kwargs):
        """
        Posts the LedgerModel.

        Parameters
        ----------
        commit: bool
            If True, saves the LedgerModel instance instantly. Defaults to False.
        """
        if self.can_post():
            self.posted = True
            if commit:
                self.save(update_fields=[
                    'posted',
                    'updated'
                ])

    def unpost(self, commit: bool = False, **kwargs):
        """
        Un-posts the LedgerModel.

        Parameters
        ----------
        commit: bool
            If True, saves the LedgerModel instance instantly. Defaults to False.
        """
        if self.can_unpost():
            self.posted = False
            if commit:
                self.save(update_fields=[
                    'posted',
                    'updated'
                ])

    def lock(self, commit: bool = False, **kwargs):
        """
        Locks the LedgerModel.

        Parameters
        ----------
        commit: bool
            If True, saves the LedgerModel instance instantly. Defaults to False.
        """
        if self.can_lock():
            self.locked = True
            if commit:
                self.save(update_fields=[
                    'locked',
                    'updated'
                ])

    def unlock(self, commit: bool = False, **kwargs):
        """
        Un-locks the LedgerModel.

        Parameters
        ----------
        commit: bool
            If True, saves the LedgerModel instance instantly. Defaults to False.
        """
        if self.can_unlock():
            self.locked = False
            if commit:
                self.save(update_fields=[
                    'locked',
                    'updated'
                ])

    def get_entity_name(self) -> str:
        return self.entity.name

    def get_entity_last_closing_date(self) -> Optional[date]:
        return self.entity.last_closing_date

    def get_absolute_url(self) -> str:
        """
        Determines the absolute URL of the LedgerModel instance.
        Results in additional Database query if entity field is not selected in QuerySet.

        Returns
        -------
        str
            URL as a string.
        """
        return reverse('django_ledger:ledger-detail',
                       kwargs={
                           # pylint: disable=no-member
                           'entity_slug': self.entity.slug,
                           'ledger_pk': self.uuid
                       })

    def get_update_url(self) -> str:
        """
        Determines the update URL of the LedgerModel instance.
        Results in additional Database query if entity field is not selected in QuerySet.

        Returns
        -------
        str
            URL as a string.
        """
        return reverse('django_ledger:ledger-update',
                       kwargs={
                           'entity_slug': self.entity.slug,
                           'ledger_pk': self.uuid
                       })

    def get_delete_message(self):
        return _(f'Are you sure you want to delete Ledger {self.name} from Entity {self.get_entity_name()}?')


class LedgerModel(LedgerModelAbstract):
    """
    Base LedgerModel from Abstract.
    """
