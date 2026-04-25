from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import Order

class Command(BaseCommand):
    help = 'Automatically update order statuses based on creation time'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Orders created 2+ days ago should be delivered
        delivered_cutoff = now - timedelta(days=2)
        delivered_orders = Order.objects.filter(
            status__in=['paid', 'shipped'],
            created_at__lte=delivered_cutoff
        )
        count_delivered = delivered_orders.update(status='delivered')
        if count_delivered:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated {count_delivered} orders to delivered'))

        # Orders created 1+ days ago but less than 2 days should be shipped
        shipped_cutoff = now - timedelta(days=1)
        shipped_orders = Order.objects.filter(
            status='paid',
            created_at__lte=shipped_cutoff
        )
        count_shipped = shipped_orders.update(status='shipped')
        if count_shipped:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated {count_shipped} orders to shipped'))

        if not count_delivered and not count_shipped:
            self.stdout.write(self.style.WARNING('No orders to update'))
