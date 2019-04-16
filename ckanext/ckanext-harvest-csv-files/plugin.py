#!/usr/bin/env python
# encoding: utf-8
__name__ = "ckanext-harvest-csv-files"
__description__= """ Ce plugin permet à l'application CKAN de moissonner un répertoire contenant des fichiers CSV.

Le chemin d'accès au répertoire doit être identifié à l'aide d'une variable d'environnement : METADATA_FOLDER
"""
from os import environ
from os import listdir, path

import ckan.plugins as p
from flask import jsonify, send_from_directory, Blueprint, abort, redirect, url_for

CURRENT_PATH = environ['METADATA_FOLDER']

app = Blueprint('file_server', __name__)

def get_folder_content(guid):
    if guid in listdir(CURRENT_PATH):
        folder_content =listdir(path.join(CURRENT_PATH, guid))
        xml_file = "{}.xml".format(guid)
        if xml_file in folder_content:
            folder_content.remove(xml_file)
            return folder_content
    else:
        return False

def get_folder_by_index(index):
    print("in get by index")
    data_content = listdir(CURRENT_PATH)
    if index > len(data_content):
        return False
    else:
        return data_content[index]



@app.route("/data")
@app.route("/data/")
def get_data_content():
    return jsonify({'data_content':listdir(CURRENT_PATH)})


@app.route("/data/<string:guid>")
@app.route("/data/<string:guid>/")
def get_content(guid):
    content = get_folder_content(guid)
    if content:
        return jsonify({'folder_content':content})
    else:
        return 'Folder not found. Check metadata.'

@app.route("/data/<int:index>")
@app.route("/data/<int:index>/")
def get_index(index):
    data_content = listdir(CURRENT_PATH)
    if index > len(data_content):
        return abort(404)
    else:
        guid = data_content[index]
        return redirect(url_for('file_server.get_content',guid=guid))


@app.route("/data/<string:guid>/<string:file_name>")
@app.route("/data/<string:guid>/<string:file_name>/")
def get_file(guid, file_name):
    folder_content = get_folder_content(guid)
    if folder_content:
        if file_name in folder_content:
            return send_from_directory(path.join(CURRENT_PATH, guid),file_name)
    else:
        return 'Folder not found. Check metadata.'

@app.route("/data/<int:folder_index>/<string:file_name>")
@app.route("/data/<int:folder_index>/<string:file_name>/")
def get_file_by_folder_index(folder_index, file_name):
    print('get_file_by_folder_index')
    guid = get_folder_by_index(folder_index)
    if guid:
        return redirect(url_for('file_server.get_file',guid=guid,file_name=file_name))

@app.route("/data/<string:guid>/<int:file_index>")
@app.route("/data/<string:guid>/<int:file_index>/")
def get_file_by_index_in_folder(guid, file_index):
    print('get_file_by_index_in_folder')
    folder_content = get_folder_content(guid)
    if folder_content and file_index < len(folder_content):
        file_name = folder_content[file_index]
        return redirect(url_for('file_server.get_file',guid=guid,file_name=file_name))

class Create_Resource_From_CsvPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    def get_blueprint(self):
        return app
