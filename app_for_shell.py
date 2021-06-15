import subprocess
import uuid
import os

from flask import Flask, request, make_response
from flask_cors import cross_origin


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))


app = CustomFlask(__name__, template_folder="templates")


@app.route("/semrep/", methods=["POST"])
@cross_origin()
def semrep():
    if request.method == "POST":
        contents = request.get_json()
        if not contents.get("text", None):
            return make_response({
                "code": 401,
                "data": None,
                "message": "must input some text"
            })
        # data directory is if exists
        data_path = "/home/tom/data"
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        input_filename = "{}.txt".format(str(uuid.uuid4()))
        with open(os.path.join(data_path, input_filename), "w", encoding="utf-8", errors="ignore") as f:
            f.write(contents["text"])
        # execute model
        commands = [
            "cd /home/tom/public_semrep/",
            "./bin/semrep.v1.8 -L 2018 -Z 2018AA ../data/{}".format(input_filename)
        ]
        execute_command = " && ".join(commands)
        execute_status = subprocess.run(execute_command, shell=True)
        if execute_status.returncode == 0:
            out_filepath = "{}/{}.sem.v1.8".format(data_path, input_filename)
            res_data = {
                "code": 200,
                "data": {},
                "message": "semrep execute successfully."
            }
            with open(out_filepath, "r", encoding="utf-8", errors="ignore") as f:
                res_data["data"]["text"] = f.read()
            return make_response(res_data)
        else:
            res_data = {
                "code": 400,
                "data": None,
                "message": "semrep failed to execute."
            }
            return make_response(res_data)


@app.route("/openie/", methods=["POST"])
@cross_origin()
def openie():
    if request.method == "POST":
        contents = request.get_json()
        if not contents.get("text", None):
            return make_response({
                "code": 401,
                "data": None,
                "message": "must input some text"
            })
        # data directory is if exists
        data_path = "/home/test/openie/data"
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        input_filename = "{}.txt".format(str(uuid.uuid4()))
        input_filepath = os.path.join(data_path, input_filename)
        output_filepath = os.path.join(data_path, "{}.out".format(input_filename))
        with open(input_filepath, "w", encoding="utf-8", errors="ignore") as f:
            f.write(contents["text"])
        # execute model
        commands = [
            "cd /home/test/openie/",
            "nohup java -jar openie-assembly.jar --ignore-errors --encoding utf-8 {} {}".format(
                input_filepath, output_filepath)
        ]
        execute_command = " && ".join(commands)
        execute_status = subprocess.run(execute_command, shell=True)
        if execute_status.returncode == 0:
            res_data = {
                "code": 200,
                "data": {},
                "message": "openie execute successfully."
            }
            with open(output_filepath, "r", encoding="utf-8", errors="ignore") as f:
                res_data["data"]["text"] = f.read()
            return make_response(res_data)
        else:
            res_data = {
                "code": 400,
                "data": None,
                "message": "openie failed to execute."
            }
            return make_response(res_data)


@app.route("/test/", methods=["POST"])
@cross_origin()
def test():
    if request.method == "POST":
        contents = request.get_json()
        if not contents.get("text", None):
            return make_response({
                "code": 401,
                "data": None,
                "message": "must input some text"
            })
        # data directory is if exists
        data_path = "/home/charles/data"
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        input_filename = "{}.txt".format(str(uuid.uuid4()))
        input_filepath = os.path.join(data_path, input_filename)
        output_filepath = "/home/charles/{}".format(input_filename)
        with open(input_filepath, "w", encoding="utf-8", errors="ignore") as f:
            f.write(contents["text"])
        # execute model
        commands = [
            "cd /home/charles/data",
            "cp -f {} ../".format(input_filename)
        ]
        execute_command = " && ".join(commands)
        execute_status = subprocess.run(execute_command, shell=True)
        if execute_status.returncode == 0:
            res_data = {
                "code": 200,
                "data": {},
                "message": "openie execute successfully."
            }
            with open(output_filepath, "r", encoding="utf-8", errors="ignore") as f:
                res_data["data"]["text"] = f.read()
            return make_response(res_data)
        else:
            res_data = {
                "code": 400,
                "data": None,
                "message": "openie failed to execute."
            }
            return make_response(res_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9001, debug=True)
