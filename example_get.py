import requests
import json

# endpoint for retrieving and parsing subjects
subj_query="https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=1268"
subjects=[s['subject'] for s in requests.get(subj_query).json()['subjects']]

# endpoint for searching through each subject
# sis api is partially documented here: https://s23.cs3240.org/sis-api.html
# hooslist api has no documentation, i had to find it through capturing the network calls of hooslist using dev tools
num_template='https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1268&subject='
desc_template='https://hooslist.virginia.edu/ClassSchedule/_GetCourseDescription?subject='

# local storage of descs, probably redundant now i found the hooslist endpoint that works
out={}
for subject in subjects:
    print(subject)
    query=num_template+subject+'&page='
    pageCount=requests.get(query+'1').json()['pageCount']
    subj_ids={}
    for page in range(pageCount):
        response=requests.get(query+f'{page+1}').json()['classes']
        for course in response:
            if course['catalog_nbr'] not in subj_ids:
                print(course['catalog_nbr'])
                desc_query=desc_template+subject+'&courseNum='+course['catalog_nbr']
                desc_response=requests.get(desc_query).text
                subj_ids[course['catalog_nbr']]=desc_response
    out[subject]=subj_ids
with open('desc.json','w') as f: json.dump(out,f,indent=4)