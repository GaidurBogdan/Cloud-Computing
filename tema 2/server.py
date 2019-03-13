from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import subprocess
import time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("./config/tema2cloud-db9c8-firebase-adminsdk-3wjgm-7f78440167.json")
firebase_admin.initialize_app(cred, {
  'projectId': 'tema2cloud-db9c8',
})

db = firestore.client()

class S(BaseHTTPRequestHandler):
    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()





    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        request_id = parsed_path.path

        path_list = request_id.split("/")

        if path_list[2] == 'name':
            requested_movie_name = request_id.split("/")[3]
            requested_movie_name = requested_movie_name.replace("%20", " ")
            users_ref = db.collection('movies').where('name', '==', requested_movie_name)
            docs = list(users_ref.get())
            if len(docs) == 0:
                self._set_headers(404)
                response = {'error_message': 'No movie with this name exists. Check the spelling for typos.' }
            else:
                response = docs[0].to_dict()
        elif path_list[2] == 'genre':
            requested_movie_genre = request_id.split("/")[3]
            users_ref = db.collection('movies').where('genre', '==', requested_movie_genre)
            docs = list(users_ref.get())
            if len(docs) == 0:
                self._set_headers(300)
                response = {'error_message': 'No movies belonging to this genre exist. Check the spelling for typos.' }
            else:
                response = {'genre': requested_movie_genre,
                        'movies_list': []}
                for doc in docs:
                    response['movies_list'].append(doc.to_dict())
        else:
            self._set_headers(404)
            response = {'error_message': 'Please provide a path to the requested resource, such as /movies/name/movie_name or /movies/genre/movie_genre.'}
        
        self._set_headers(200)        
        self.wfile.write(bytes(json.dumps(response), "UTF-8"))





    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        request_id = parsed_path.path

        path_list = request_id.split("/")

        content_length = int(self.headers['Content-Length'])
        body_content = self.rfile.read(content_length)
        fields = urllib.parse.parse_qs(body_content)

        if path_list[2] == 'name':
            movies_list = list(db.collection('movies').where('name', '==', fields[b'name'][0].decode('utf-8')).get())

            if len(movies_list) > 0:
                self._set_headers(404)
                response = {'error_message': 'A movie with this name already exists.'}
            else:
                new_movie_id = db.collection('movies').add({
                    'name': fields[b'name'][0].decode('utf-8'),
                    'genre': fields[b'genre'][0].decode('utf-8'), 
                    'year': int(fields[b'year'][0].decode('utf-8'))
                })
                new_movie_id = list(db.collection('movies').where('name', '==', fields[b'name'][0].decode('utf-8')).get())[0]
                response = {'New movie\'s ID': new_movie_id.id}
        elif path_list[2] == 'bulk':
            bulk_list = json.loads(body_content.decode("utf-8"))

            response = {}
            for item in bulk_list["batch"]:
                movies_list = list(db.collection('movies').where('name', '==', item["name"]).get())
                if len(movies_list) > 0:
                    self._set_headers(404)
                    response = {'error_message': 'The movie with the name '+ item["name"] +' already exists.'}
                    break
            if len(response) == 0:
                for item in bulk_list["batch"]:
                    db.collection('movies').add(item)
                    response[item["name"]] = list(db.collection('movies').where('name', '==', item["name"]).get())[0].id
        else:
            self._set_headers(404)
            response = {'error_message': 'Please provide a path to the requested resource, such as /movies/name or /movies/bulk.'}
        
        self._set_headers(200)
        self.wfile.write(bytes(json.dumps(response), "UTF-8"))


    def do_DELETE(self):
        parsed_path = urllib.parse.urlparse(self.path)
        request_id = parsed_path.path

        path_list = request_id.split("/")

        if path_list[2] == 'name':
            requested_movie_name = request_id.split("/")[3]
            requested_movie_name = requested_movie_name.replace("%20", " ")
            users_ref = db.collection('movies').where('name', '==', requested_movie_name)
            docs = list(users_ref.get())
            if len(docs) == 0:
                self._set_headers(404)
                response = {'error_message': 'No movie with this name exists. Check the spelling for typos.' }
            else:
                response = {'Deleted items IDs': []}
                old_nr_docs = len(list(db.collection('movies').get()))
                for doc in docs:
                    response['Deleted items IDs'].append(doc.id)
                    db.collection('movies').document(doc.id).delete()
                new_nr_docs = len(list(db.collection('movies').get()))
                response['Number of movies before deletions'] = old_nr_docs
                response['Number of movies after deletions'] = new_nr_docs
        elif path_list[2] == 'genre':
            requested_movie_genre = request_id.split("/")[3]
            users_ref = db.collection('movies').where('genre', '==', requested_movie_genre)
            docs = list(users_ref.get())
            if len(docs) == 0:
                self._set_headers(404)
                response = {'error_message': 'No movies belonging to this genre exist. Check the spelling for typos.' }
            else:
                response = {'Deleted items IDs': []}
                old_nr_docs = len(list(db.collection('movies').get()))
                for doc in docs:
                    response['Deleted items IDs'].append(doc.id)
                    db.collection('movies').document(doc.id).delete()
                new_nr_docs = len(list(db.collection('movies').get()))
                response['Number of movies before deletions'] = old_nr_docs
                response['Number of movies after deletions'] = new_nr_docs
        else:
            self._set_headers(404)
            response = {'error_message': 'Please provide a path to the requested resource, such as /movies/name/movie_name or /movies/genre/movie_genre.'}
        
        self._set_headers(200)        
        self.wfile.write(bytes(json.dumps(response), "UTF-8"))


    def do_PUT(self):
        parsed_path = urllib.parse.urlparse(self.path)
        request_id = parsed_path.path

        path_list = request_id.split("/")

        content_length = int(self.headers['Content-Length'])
        body_content = self.rfile.read(content_length)
        fields = urllib.parse.parse_qs(body_content)

        if path_list[2] == 'name':
            movies_list = list(db.collection('movies').where('name', '==', fields[b'name'][0].decode('utf-8')).get())

            if len(movies_list) < 1:
                self._set_headers(404)
                response = {'error_message': 'The movie does not exist. Try making a POST request to add a movie..'}
            else:
                db.collection('movies').document(movies_list[0].id).set({
                    'name': fields[b'name'][0].decode('utf-8'),
                    'genre': fields[b'genre'][0].decode('utf-8'), 
                    'year': int(fields[b'year'][0].decode('utf-8'))
                })
                new_movie_id = movies_list[0].id
                response = {'Updated movie\'s id': str(new_movie_id)}
        elif path_list[2] == 'bulk':
            bulk_list = json.loads(body_content.decode("utf-8"))

            response = {}
            for item in bulk_list["batch"]:
                movies_list = list(db.collection('movies').where('name', '==', item["name"]).get())
                if len(movies_list) < 1:
                    self._set_headers(404)
                    response = {'error_message': 'The movie with the name'+ item["name"] +'does not exist. You need to add it before modifying it.'}
                    break
            if len(response) == 0:
                for item in bulk_list["batch"]:
                    item_id = list(db.collection('movies').where('name', '==', item["name"]).get())[0].id
                    db.collection('movies').document(item_id).set(item)
                    response['Updated \'' + item["name"] + '\' at ID'] = item_id
        else:
            self._set_headers(404)
            response = {'error_message': 'Please provide a path to the requested resource, such as /movies/name or /movies/genre.'}
        
        self._set_headers(200)
        self.wfile.write(bytes(json.dumps(response), "UTF-8"))

def run(server_class=HTTPServer, handler_class=S, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print ('Service started!')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()