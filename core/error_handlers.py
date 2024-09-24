import logging
from flask import jsonify
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

# Initialize logging
logging.basicConfig(level=logging.ERROR)

def handle_error(err):
    logging.error(f"Error occurred: {str(err)}")  # Log the error message

    # Handle specific exceptions
    if isinstance(err, FyleError):
        return jsonify(error=err.__class__.__name__, message=err.message), err.status_code
    elif isinstance(err, ValidationError):
        return jsonify(error=err.__class__.__name__, message=err.messages), 400
    elif isinstance(err, IntegrityError):
        return jsonify(error=err.__class__.__name__, message=str(err.orig)), 400
    elif isinstance(err, HTTPException):
        return jsonify(error=err.__class__.__name__, message=str(err)), err.code

    # Generic error response
    return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500
