from flask import Flask, request, Response
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from converter import convert


app = Flask(__name__)
api = Api(app)


from pymongo import MongoClient
client = MongoClient("mongodb://root:mkps@mongo:27017/")
db = client.mk
collection = db["config"]


parser = reqparse.RequestParser()
parser.add_argument('values', dict, {})
parser.add_argument('values', str, "")


class ApiResource(Resource):
    def post(self):
        try:
            values = request.json
            return convert(collection, values)
        except Exception as e:
            print(e)
            exit()


api.add_resource(ApiResource, "/")
cors = CORS(app, resources={r"/*": {"origins": "*"}})
if __name__ == "__main__":
    app.run(host='0.0.0.0')
