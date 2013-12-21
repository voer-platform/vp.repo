import re
import json
from vpr_content import models


PREFIX_MID = '"material_id": '

def correctIDs(text):
    rg = re.compile('(?<="material_id": )[^"].*?(?=,)')
    wrongs = rg.findall(text)
    for _ in wrongs:
        text = text.replace(PREFIX_MID + _, PREFIX_MID + '"' + _ + '"')
    return text


def updateMaterialExtra(file_name):
    models.MaterialViewCount.objects.all().delete()
    with open(file_name, 'r') as f0:
        extra = json.load(f0)
    print len(extra)
    for piece in extra:
        try:
            if piece['view_count']:
                vc = models.MaterialViewCount(
                    material_id = models.getMaterialRawID(piece['material_id']),
                    count = piece['view_count']
                    )
                vc.save()
            else:
                print "-"
        except:
            print piece['material_id']
    return "DONE" 
