from flask import Blueprint
from flask_restx import Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp, title="API", version="1.0", description="TMS Auto Plan")
