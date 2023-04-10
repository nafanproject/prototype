from django.core.management.base import BaseCommand, CommandError

from NAFAN.models import FindingAid

class Command(BaseCommand):
    help = "Reindex finding aid by pk"

    def add_arguments(self, parser):
        parser.add_argument("findingaid_id",  type=int)

    def handle(self, *args, **options):
        pk = options.get("findingaid_id")
        f = FindingAid.objects.get(pk=pk)
        eid = FindingAid.CreateIndex(f.pk, f.aid_type, f.title, f.repository, f.scope_and_content, "")
        if eid == 'Fail':
            print(f'Failed to index repository: {r}')
        else:
            f.elasticsearch_id = eid
            f.save()