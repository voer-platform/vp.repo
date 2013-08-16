import requests
import zipfile
import re
import json

from os import path, listdir
from migrate import getTagContent, getAuthorInfo, buildRegex

URL = 'http://rhaptos.voer.vn/content/%s/latest/source/'
URL_ZIP = 'http://rhaptos.voer.vn/content/%s/latest/complete/'
URL_ZIP_2 = 'http://rhaptos.voer.vn/content/%s/latest/module_export?format=zip'

def getCollectionCNXML(cid):
    """Download and save cnxml file of specific collection"""
    try:
        url = URL_ZIP % cid
        res = requests.get(url)
        if res.status_code == 200:
            ofile = open(cid+'.zip', 'w')
            ofile.write(res.content)
            ofile.close()
            print "ZIP downloaded: " + cid
        else:
            print "Error while getting ZIP content of collection %s. Try to download CNXML file... " % cid
            url = URL % cid
            res = requests.get(url)
            if res.status_code == 200:
                ofile = open(cid+'.cnxml', 'w')
                ofile.write(res.content)
                ofile.close()
            else:
                print "Both were failed. Pls try this manually (%s)" % cid
    except:
        print "Both were failed. Pls try this manually (%s)" % cid
    

def downloadModule(mid):
    """ """
    try:
        url = URL_ZIP_2 % mid
        res = requests.get(url)
        if res.status_code == 200:
            ofile = open(mid+'.zip', 'w')
            ofile.write(res.content)
            ofile.close()
            print "ZIP downloaded: " + mid
        else:
            raise
    except:
        print 'Error when downloading module ' + mid


def downloadAllModules():
    """ """
    mf = open('missing_modules.txt', 'r')
    missing = json.loads(mf.read())
    for mid in missing:
        downloadModule(mid)
    return 'DONE'


def getAllCollections():
    all_ids = [cid.strip() for cid in RAW_COLLECTION_IDS.split('\n')]
    for cid in all_ids:
        if cid:
            getCollectionCNXML(cid) 


def listIncludedModules(collection_path):
    """Returns list of modules IDs inside a collection"""
    col_path = collection_path.lower().strip()
    xml_content = ''

    # extract the module ID in case of ZIP file
    if col_path.endswith('.zip'):
        zf = zipfile.ZipFile(col_path)
        xml_path = ''
        for file_name in zf.namelist():            
            if file_name.lower().endswith('collection.xml'):
                xml_path = file_name
                break
        if xml_path:
            xf = zf.open(xml_path)
            xml_content = xf.read()
            xf.close()
        zf.close()
    elif col_path.endswith('.cnxml'):
        cf = open(col_path)
        xml_content = cf.read()
        cf.close()
    xml_content = xml_content.replace('\n', '')

    # read the list of modules
    re_module = re.compile('(?<=document=").*?(?=")')
    RTAG = '(?<=<%(tag)s\s).*?(?=</%(tag)s>)'
    rtag = buildRegex('col:module', RTAG)
    res = rtag.findall(xml_content)
    children = []
    for line in res:
        try:
            module_id = re_module.findall(line)[0]
            module_title = getTagContent('md:title', line)[0]
            children.append((module_id, module_title))
        except:
            pass
    
    return children
        
def saveAllNeededModules(root_path):
    """Save all needed modules into external file"""
    collections = listdir(root_path)
    included_modules = {}
    for col in collections:
        print '.'
        modules = listIncludedModules(path.join(root_path, col))
        for mod in modules:
            if mod[0] not in included_modules:
                included_modules[mod[0]] = mod[1]
    
    of = open('needed_modules.txt', 'w')
    of.write(json.dumps(included_modules))
    of.close()


# ./manage.py shell
def getMissingModules(mfile='needed_modules.txt'):
    """Determine if a module if missing from database"""
    from vpr_content.models import OriginalID

    mf = open(mfile, 'r')
    modules = json.loads(mf.read())
    mf.close()
    missing = {}

    for item in modules:
        try:
            oid = OriginalID.objects.filter(original_id__startswith=item)
            if len(oid) > 0:
                print item + ' exists'
            else:
                missing[item] = modules[item]
                print item + ' missing'
        except OriginalID.DoesNotExist:
            missing[item] = modules[item]
            print item + ' missing'
    
    mf = open('missing_modules.txt', 'w')
    mf.write(json.dumps(missing))
    mf.close()



RAW_COLLECTION_IDS = """
col10001
col10002
col10003
col10004
col10005
col10006
col10007
col10008
col10009
col10010
col10011
col10012
col10013
col10014
col10015
col10016
col10017
col10018
col10019
col10020
col10021
col10022
col10023
col10024
col10025
col10026
col10027
col10028
col10029
col10030
col10031
col10032
col10033
col10034
col10035
col10036
col10037
col10038
col10039
col10040
col10041
col10042
col10043
col10044
col10045
col10046
col10047
col10048
col10049
col10050
col10051
col10052
col10053
col10054
col10055
col10056
col10057
col10058
col10059
col10060
col10061
col10062
col10063
col10064
col10065
col10066
col10067
col10068
col10069
col10070
col10071
col10072
col10073
col10074
col10075
col10076
col10077
col10078
col10079
col10080
col10081
col10082
col10083
col10084
col10085
col10086
col10087
col10088
col10089
col10090
col10091
col10092
col10093
col10094
col10095
col10096
col10097
col10098
col10099
col10100
col10101
col10102
col10103
col10104
col10105
col10106
col10107
col10108
col10109
col10110
col10111
col10112
col10113
col10114
col10115
col10116
col10117
col10118
col10119
col10120
col10121
col10122
col10123
col10124
col10125
col10126
col10127
col10128
col10129
col10130
col10131
col10132
col10133
col10134
col10135
col10136
col10137
col10138
col10139
col10140
col10141
col10142
col10143
col10144
col10145
col10146
col10147
col10148
col10149
col10150
col10151
col10152
col10153
col10154
col10155
col10156
col10157
col10158
col10159
col10160
col10161
col10162
col10163
col10164
col10165
col10166
col10167
col10168
col10169
col10170
col10171
col10172
col10173
col10174
col10175
col10176
col10177
col10178
col10179
col10180
col10181
col10182
col10183
col10184
col10185
col10186
col10187
col10188
col10189
col10190
col10191
col10192
col10193
col10194
col10195
col10196
col10197
col10198
col10199
col10200
col10201
col10202
col10203
col10204
col10205
col10206
col10207
col10208
col10209
col10210
col10211
col10212
col10213
col10214
col10215
col10216
col10217
col10218
col10219
col10220
col10221
col10222
col10223
col10224
col10225
col10226
col10227
col10228
col10229
col10230
col10231
col10232
col10233
col10234
col10235
col10236
col10237
col10238
col10239
col10240
col10241
col10242
col10243
col10244
col10245
col10246
col10247
col10248
col10249
col10250
col10251
col10252
col10253
col10254
col10255
col10256
col10257
col10258
col10259
col10260
col10261
col10262
col10263
col10264
col10265
col10266
col10267
col10268
col10269
col10270
col10271
col10272
col10273
col10274
col10275
"""
