from flask import jsonify
from marshmallow.exceptions import ValidationError
from core import app
from core.apis.assignments import student_assignments_resources, teacher_assignments_resources
from core.libs import helpers
from core.libs.exceptions import FyleError
from werkzeug.exceptions import HTTPException

from sqlalchemy.exc import IntegrityError

app.register_blueprint(student_assignments_resources, url_prefix='/student')
app.register_blueprint(teacher_assignments_resources, url_prefix='/teacher')



@app.route('/')
def ready():
    response = jsonify({
        'status': 'ready',
        'time': helpers.get_utc_now()
    })

    return response


@app.route('/principal/assignments', methods=['GET'])
def get_all_assignments():
    # Principal authentication logic here
    principal_id = get_principal_from_header()
    if not principal_id:
        return jsonify({"error": "Unauthorized"}), 401

    assignments = Assignment.query.all()
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

@app.route('/principal/teachers', methods=['GET'])
def get_all_teachers():
    # Principal authentication logic
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

@app.route('/principal/assignments/grade', methods=['POST'])
def regrade_assignment():
    # Principal authentication logic
    principal_id = get_principal_from_header()
    if not principal_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    assignment_id = data['id']
    new_grade = data['grade']

    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    assignment.grade = new_grade
    db.session.commit()

    return jsonify({"data": assignment_schema.dump(assignment)}), 200



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

    raise err
