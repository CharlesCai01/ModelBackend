import json

from flask import Flask, request, render_template, make_response

from pre_process import del_punc_str
from flask_cors import cross_origin


from kashgari.tasks.labeling import BiGRU_Model


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))


app = CustomFlask(__name__, template_folder="templates")
loaded_model = BiGRU_Model.load_model("weak_index234_ner_model")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/label/", methods=["POST"])
@cross_origin()
def get_labels():
    """
    The front end needs to set Content-Type=application/json.
    The structure of contents json string:
    {
        "inputstring": [
            {"content": "some contents"},
            {"content": "some contents"},
            ......
        ]
    }
    :return: The contents with labels, example:
    {
        "outputstring": [
            {
                "content": "['A', 'graphene', ...]",
                "label": "['O', 'B-Subject', 'B-Verb', ...]"}
            },
            ...
        ]
    }
    """
    if request.method == "POST":
        contents = request.get_json()
        res = make_response(predict(contents))
        return res


def __get_wait_ann_four_data(contents_json):
    """
    Split contents to words.
    :param contents_json: The structure of contents json string:
    {
        "inputstring": [
            {"content": "some contents"},
            {"content": "some contents"},
            ......
        ]
    }
    :return: The list of words list.
    """
    contents = [item["content"] for item in contents_json['inputstring']]
    content_list = []
    for content in contents:
        try:
            content_list.append(del_punc_str(content.split(" ")))
        except Exception as e:
            print(e)
            continue
    return content_list


def predict(contents_json):
    """
    predict the label of word of content.
    :param contents_json: The structure of contents json string:
    {
        "inputstring": [
            {"content": "some contents"},
            {"content": "some contents"},
            ......
        ]
    }
    :return: The contents with labels, example:
    {
        "outputstring": [
            {
                "content": "['A', 'graphene', ...]",
                "label": "['O', 'B-Subject', 'B-Verb', ...]"}
            },
            ...
        ]
    }
    """
    content_list = __get_wait_ann_four_data(contents_json)
    # Load saved model
    res = loaded_model.predict(content_list)
    assert len(content_list) == len(res)
    output_json = dict()
    output_json["outputstring"] = list()
    for i in range(len(content_list)):
        temp_item = dict()
        temp_item["content"] = content_list[i]
        temp_item["label"] = res[i]
        temp_item["ori"] = contents_json["inputstring"][i]
        output_json["outputstring"].append(temp_item)
    return json.dumps(output_json)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
