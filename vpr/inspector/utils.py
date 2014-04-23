from haystack.query import SearchQuerySet as sqs

from models import FlagTerm


def scan_content(content):
    """ Scan given content and returns list of found terms """
    pass


def scan_search_index():
    terms = FlagTerm.objects.all()
    results = {}
    for term in terms:
        result = sqs().filter(content=term.value).values('pk')
        if result:
            doc_ids = [item['pk'] for item in result]
            results[term.value] = doc_ids
    return results
