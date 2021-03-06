# Generated by Django 2.1.7 on 2019-02-19 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20190210_1254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalprinter',
            name='current_print_alert_muted',
        ),
        migrations.RemoveField(
            model_name='printer',
            name='current_print_alert_muted',
        ),
        migrations.AddField(
            model_name='historicalprinter',
            name='alert_acknowledged_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='printer',
            name='alert_acknowledged_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='historicalprinter',
            name='action_on_failure',
            field=models.CharField(choices=[('NONE', 'Just email me.'), ('PAUSE', 'Pause the print and email me.'), ('CANCEL', 'Cancel the print and email me (not available during beta testing).')], default='PAUSE', max_length=10),
        ),
        migrations.AlterField(
            model_name='printer',
            name='action_on_failure',
            field=models.CharField(choices=[('NONE', 'Just email me.'), ('PAUSE', 'Pause the print and email me.'), ('CANCEL', 'Cancel the print and email me (not available during beta testing).')], default='PAUSE', max_length=10),
        ),
        migrations.AlterField(
            model_name='printercommand',
            name='status',
            field=models.CharField(choices=[('PENDING', 'pending'), ('SENT', 'sent'), ('ABORTED', 'aborted')], default='PENDING', max_length=10),
        ),
    ]
