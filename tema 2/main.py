#!C:\Users\bgaid\AppData\Local\Programs\Python\Python37-32\python.exe



for doc in docs:
    print('{} => {}'.format(doc.id, doc.to_dict()))


# doc_ref = db.collection('movies').document('Gdj83I3ZEn06Dhuezur4')
# doc_ref.set({
#     'name': 'The Green Mile',
#     'genre': 'fantasy',
#     'year': 1999
# })
