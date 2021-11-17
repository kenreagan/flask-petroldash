from flask import Blueprint, jsonify


error = Blueprint('error', __name__, template_folder='../templates')


@error.errorhandler(404)
def error_404(e):
    return jsonify({'message': 'page not found ensure you enter the correct endpoint'}), 404

@error.errorhandler(403)
def error_403(e):
    return jsonify({'message': 'you are forbidden to access this route'}), 403

@error.errorhandler(500)
def errot_500(e):
    return jsonify({'message': 'There was an internal error please contact the administrator'}), 500

