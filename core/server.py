from flask import jsonify, request
from marshmallow.exceptions import ValidationError
from core import app
from core.apis.assignments import student_assignments_resources, teacher_assignments_resources
from core.libs import helpers
from core.libs.exceptions import FyleError
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from core.models.assignments import AssignmentStateEnum
from core.error_handlers import handle_error


app.register_blueprint(student_assignments_resources, url_prefix='/student')
app.register_blueprint(teacher_assignments_resources, url_prefix='/teacher')

import json

def get_principal_from_header():
    try:
        header = request.headers.get('X-Principal')
        if header:
            principal = json.loads(header)
            return principal.get('principal_id')
        else:
            raise Exception("Principal header missing")
    except Exception as e:
        print(f"Error in getting principal from header: {str(e)}")
        raise e


@app.route('/')
def ready():
    response = jsonify({
        'status': 'ready',
        'time': helpers.get_utc_now()
    })
    return response

@app.errorhandler(Exception)
def error_handler(err):
    return handle_error(err)



@app.route('/principal/assignments/grade', methods=['POST'])
def regrade_assignment():
    principal_id = get_principal_from_header()
    if not principal_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    
    # Validate input data
    if not data or 'id' not in data or 'grade' not in data:
        return jsonify({"error": "Invalid input data"}), 400

    assignment_id = data['id']
    new_grade = data['grade']

    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    assignment.grade = new_grade

    try:
        db.session.commit()
    except IntegrityError as e:
        print(f"Database integrity error: {str(e)}")
        return jsonify({"error": "Database Error"}), 400
    except Exception as e:  # Additional exception handling
        print(f"Error committing changes: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

    return jsonify({"data": assignment_schema.dump(assignment)}), 200


@app.route('/principal/assignments', methods=['GET'])
def get_all_assignments():
    principal_id = get_principal_from_header()
    print(f"Principal ID: {principal_id}")  # Debug statement

    if not principal_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Fetch assignments with state SUBMITTED or GRADED
        assignments = Assignment.query.filter(
            Assignment.state.in_([AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED])
        ).all()
        
        if not assignments:
            print("No assignments found.")  # Debug statement
        else:
            print(f"Assignments: {assignments}")  # Debug statement

        result = [{
            'id': a.id,
            'content': a.content,
            'state': a.state,
            'grade': a.grade,
            'student_id': a.student_id,
            'teacher_id': a.teacher_id,
            'created_at': a.created_at,
            'updated_at': a.updated_at
        } for a in assignments]

        return jsonify({"data": result}), 200

    except Exception as e:
        print(f"Error querying assignments: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/principal/teachers', methods=['GET'])
def get_all_teachers():
    principal_id = get_principal_from_header()
    if not principal_id:
        return jsonify({"error": "Unauthorized"}), 401

    teachers = Teacher.query.all()
    result = [{
        'id': t.id,
        'user_id': t.user_id,
        'created_at': t.created_at,
        'updated_at': t.updated_at
    } for t in teachers]

    return jsonify({"data": result}), 200


@app.errorhandler(Exception)
def handle_error(err):
    if isinstance(err, FyleError):
        return jsonify(
            error=err.__class__.__name__, message=err.message
        ), err.status_code
    elif isinstance(err, ValidationError):
        return jsonify(
            error=err.__class__.__name__, message=err.messages
        ), 400
    elif isinstance(err, IntegrityError):
        return jsonify(
            error=err.__class__.__name__, message=str(err.orig)
        ), 400
    elif isinstance(err, HTTPException):
        return jsonify(
            error=err.__class__.__name__, message=str(err)
        ), err.code

    return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500
