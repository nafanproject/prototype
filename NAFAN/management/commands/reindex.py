from django.core.management.base import BaseCommand, CommandError
from .models import Repository, FindingAid

class Command(BaseCommand):
    help = "Reindexes all repositories"

    def handle(self, *args, **options):
        for r in Repository.objects.all():
            elasticsearch_id = FindingAid.CreateIndex(r.pk, "repository", r.repository_name, r.repository_name, r.description, "")

            # Add the elasticsearch id to the repository
            if elasticsearch_id != "Fail":
                r.elasticsearch_id = elasticsearch_id
                r.save()
            else:
                print(f'Failed to index repository: {r}')

        for f in FindingAid.objects.all():
            elasticsearch_id = FindingAid.CreateIndex(f.pk, f.aid_type, f.title, f.repository, f.scope_and_content, "")

            # Add the elasticsearch id to the repository
            if elasticsearch_id != "Fail":
                r.elasticsearch_id = elasticsearch_id
                r.save()
            else:
                print(f'Failed to index repository: {r}')
