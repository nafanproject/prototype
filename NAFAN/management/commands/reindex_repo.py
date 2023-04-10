from django.core.management.base import BaseCommand, CommandError

from NAFAN.models import Repository, FindingAid

class Command(BaseCommand):
    help = "Reindex repository by name"

    def add_arguments(self, parser):
        parser.add_argument("repository_name",  type=str)

    def handle(self, *args, **options):
        name = options.get("repository_name")
        r = Repository.objects.get(repository_name=name)
        eid = FindingAid.CreateIndex(r.pk, "repository", r.repository_name, r.repository_name, r.description, "")
        if eid == 'Fail':
            print(f'Failed to index repository: {r}')
        else:
            r.elasticsearch_id = eid
            r.save()