import json
from vpr_content.models import Material, Category, restoreAssignedCategory

def exportMaterialCats():
    """ Export all material categories into JSON file
    """
    cat_data = list(Material.objects.values_list('id', 'categories'))
    jsfile = open('exported-cats.json', 'w')
    json.dump(cat_data, jsfile)
    jsfile.close()
    return 'Done exporting all material categories'


def importMaterialCats():
    cat_objs = Category.objects.all() 
    jsfile = open('exported-cats.json', 'r')
    cats = json.load(jsfile)
    for cat in cats:
        try:
            raw_cats = restoreAssignedCategory(cat[1])
            material = Material.objects.get(pk=cat[0])
            if isinstance(raw_cats, list) or isinstance(raw_cats, tuple):
                [material.categories.add(cat_objs[cid-1]) for cid in raw_cats]
            else:
                material.categories.add(cat_objs[raw_cats])
            print cat[0]
        except:
            import pdb;pdb.set_trace()
            raise




