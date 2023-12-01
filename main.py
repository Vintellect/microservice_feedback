# [START app]
import logging

# [START imports]
from flask import Flask, request, jsonify, make_response
from google.cloud import spanner
import google.oauth2.id_token
import google.auth.transport.requests
import os
import requests


# [END imports]

# [START create_app]
app = Flask(__name__)
HTTP_REQUEST = google.auth.transport.requests.Request()
# [END create_app]

# [START create_spanner]
spanner_client = spanner.Client()
user_microservices = os.getenv("USER_MICROSERVICES")
instance_id = os.getenv("SPANNER_INSTANCE")
database_id = os.getenv("SPANNER_DATABASE")
# [END create_spanner]


def is_admin(token):
    response = requests.get(user_microservices +"/isAdmin", params={'token': token})
    if response.status_code == 200:
        print(response.json())
        return response.json().get('is_admin', False)
    else:
        print(f"Failed to check admin status. Status code: {response.status_code}")
        return False



@app.route("/get_feedback/<int:wine_id>")
def get_Feedback(wine_id):
    database = spanner_client.instance(instance_id).database(database_id)
    with database.snapshot() as snapshot:
        cursor = snapshot.execute_sql(
            "SELECT * FROM feedback WHERE wine_id = @wine_id;",
            params = { 'wine_id': wine_id },
            param_types = { 'wine_id': spanner.param_types.INT64 }
        )
    results = list(cursor)
    return jsonify(results)


@app.route("/add_feedback", methods=['POST'])
def add_feedback():
    feedback_data = request.get_json()

    if feedback_exists(feedback_data["user_id"], feedback_data["wine_id"]):
        return make_response(jsonify({"error": "Conflict: User already submitted feedback for this wine"}), 409)
    
    database = spanner_client.instance(instance_id).database(database_id)
    with database.batch() as batch:
        batch.insert(
            table = "feedback",
            columns=["user_id", "wine_id", "note", "comment"],
            values=[(feedback_data["user_id"], feedback_data["wine_id"], feedback_data["note"], feedback_data["comment"])]
        )
    
    return jsonify({"success": "Feedback successfully added"})

def feedback_exists(user_id, wine_id):
    database = spanner_client.instance(instance_id).database(database_id)
    with database.snapshot() as snapshot:
        result = snapshot.execute_sql(
            "SELECT COUNT(*) FROM feedback WHERE user_id = @user_id AND wine_id = @wine_id",
            params={"user_id": user_id, "wine_id": wine_id},
            param_types={"user_id": spanner.param_types.STRING, "wine_id": spanner.param_types.INT64}
        )
        for row in result:
            count_value = row[0]
        print(f"Row count: {count_value}")

    return count_value > 0


@app.route("/delete_feedback/<string:user_id>/<int:wine_id>", methods=['DELETE'])
def delete_feedback(user_id, wine_id):
    user_token = request.args.get('token')
    print(f"Test: {user_id}, {user_token} -> {user_token == user_id}")

    if is_admin(user_token) or (user_id == user_token):
        database = spanner_client.instance(instance_id).database(database_id)
        with database.batch() as batch:
            key_set = spanner.KeySet(keys=[(user_id, wine_id)])
            batch.delete("feedback", key_set)

        return jsonify({"success": "Feedback successfully deleted"})
    else:
        return make_response(jsonify({"error": "Forbidden: User does not have permission to delete this feedback"}), 403)


@app.route("/update_feedback/<string:user_id>/<int:wine_id>", methods=['PUT'])
def update_feedback(user_id, wine_id):
    user_token = request.args.get('token')
    new_feedback_data = request.get_json()

    
    if (user_id == user_token):
        database = spanner_client.instance(instance_id).database(database_id)
        with database.batch() as batch:
            batch.update(
                "feedback",
                columns=["user_id", "wine_id", "note", "comment"],
                values=[(user_id, wine_id, new_feedback_data["note"], new_feedback_data["comment"])]
            )

        return jsonify({"success": "Feedback successfully updated"})
    else:
        return make_response(jsonify({"error": "Forbidden: User does not have permission to update this feedback"}), 403)


# [END app]