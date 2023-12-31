# Generated by Django 4.2.2 on 2023-10-02 18:25

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('django_ledger', '0010_delete_importjobmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportJobModel',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200, verbose_name='Description')),
                ('completed', models.BooleanField(default=False, verbose_name='Import Job Completed')),
                ('bank_account_model', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='django_ledger.bankaccountmodel', verbose_name='Associated Bank Account Model')),
                ('ledger_model', models.OneToOneField(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_ledger.ledgermodel', verbose_name='Ledger Model')),
            ],
            options={
                'verbose_name': 'Import Job Model',
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='accountmodel',
            name='role',
            field=models.CharField(choices=[('Assets', (('asset_ca_cash', 'Current Asset'), ('asset_ca_mkt_sec', 'Marketable Securities'), ('asset_ca_recv', 'Receivables'), ('asset_ca_inv', 'Inventory'), ('asset_ca_uncoll', 'Uncollectibles'), ('asset_ca_prepaid', 'Prepaid'), ('asset_ca_other', 'Other Liquid Assets'), ('asset_lti_notes', 'Notes Receivable'), ('asset_lti_land', 'Land'), ('asset_lti_sec', 'Securities'), ('asset_ppe_build', 'Buildings'), ('asset_ppe_build_accum_depr', 'Buildings - Accum. Depreciation'), ('asset_ppe_plant', 'Plant'), ('asset_ppe_plant_depr', 'Plant - Accum. Depreciation'), ('asset_ppe_equip', 'Equipment'), ('asset_ppe_equip_accum_depr', 'Equipment - Accum. Depreciation'), ('asset_ia', 'Intangible Assets'), ('asset_ia_accum_amort', 'Intangible Assets - Accum. Amortization'), ('asset_adjustment', 'Other Assets'))), ('Liabilities', (('lia_cl_acc_payable', 'Accounts Payable'), ('lia_cl_wages_payable', 'Wages Payable'), ('lia_cl_int_payable', 'Interest Payable'), ('lia_cl_taxes_payable', 'Taxes Payable'), ('lia_cl_st_notes_payable', 'Short Term Notes Payable'), ('lia_cl_ltd_mat', 'Current Maturities of Long Tern Debt'), ('lia_cl_def_rev', 'Deferred Revenue'), ('lia_cl_other', 'Other Liabilities'), ('lia_ltl_notes', 'Long Term Notes Payable'), ('lia_ltl_bonds', 'Bonds Payable'), ('lia_ltl_mortgage', 'Mortgage Payable'))), ('Equity', (('eq_capital', 'Capital'), ('eq_stock_common', 'Common Stock'), ('eq_stock_preferred', 'Preferred Stock'), ('eq_adjustment', 'Other Equity Adjustments'), ('eq_dividends', 'Dividends & Distributions to Shareholders'), ('in_operational', 'Operational Income'), ('in_passive', 'Investing/Passive Income'), ('in_interest', 'Interest Income'), ('in_gain_loss', 'Capital Gain/Loss Income'), ('in_other', 'Other Income'), ('cogs_regular', 'Cost of Goods Sold'), ('ex_regular', 'Regular Expense'), ('ex_interest_st', 'Interest Expense - Short Term Debt'), ('ex_interest', 'Interest Expense - Long Term Debt'), ('ex_taxes', 'Tax Expense'), ('ex_capital', 'Capital Expense'), ('ex_depreciation', 'Depreciation Expense'), ('ex_amortization', 'Amortization Expense'), ('ex_other', 'Other Expense'))), ('Root', (('root_coa', 'CoA Root Account'), ('root_assets', 'Assets Root Account'), ('root_liabilities', 'Liabilities Root Account'), ('root_capital', 'Capital Root Account'), ('root_income', 'Income Root Account'), ('root_cogs', 'COGS Root Account'), ('root_expenses', 'Expenses Root Account')))], max_length=30, verbose_name='Account Role'),
        ),
        migrations.CreateModel(
            name='StagedTransactionModel',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('fit_id', models.CharField(max_length=100)),
                ('date_posted', models.DateField(verbose_name='Date Posted')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=15, null=True)),
                ('amount_split', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('memo', models.CharField(blank=True, max_length=200, null=True)),
                ('account_model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='django_ledger.accountmodel')),
                ('import_job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_ledger.importjobmodel')),
                ('parent', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='split_transaction_set', to='django_ledger.stagedtransactionmodel', verbose_name='Parent Transaction')),
                ('transaction_model', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_ledger.transactionmodel')),
                ('unit_model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='django_ledger.entityunitmodel', verbose_name='Entity Unit Model')),
            ],
            options={
                'verbose_name': 'Staged Transaction Model',
                'abstract': False,
                'indexes': [models.Index(fields=['import_job'], name='django_ledg_import__8e6511_idx'), models.Index(fields=['date_posted'], name='django_ledg_date_po_cbcc8c_idx'), models.Index(fields=['account_model'], name='django_ledg_account_53aea9_idx'), models.Index(fields=['transaction_model'], name='django_ledg_transac_51a6b9_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='importjobmodel',
            index=models.Index(fields=['bank_account_model'], name='django_ledg_bank_ac_0bad20_idx'),
        ),
        migrations.AddIndex(
            model_name='importjobmodel',
            index=models.Index(fields=['ledger_model'], name='django_ledg_ledger__d9e03f_idx'),
        ),
        migrations.AddIndex(
            model_name='importjobmodel',
            index=models.Index(fields=['completed'], name='django_ledg_complet_42632b_idx'),
        ),
    ]
