import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)

from dashboard.auth import login_required
from dashboard.db import get_db

bp = Blueprint('dashboard', __name__)


config_labels = {
    "name": "Name",
    "on_ec_level": "Pump ON",
    "on_light_level": "UV light ON",
    "off_light_level": "UV light OFF",
    "temp_setpoint": "Temp. setpoint",
    "temp_max": "Temp. warning"
}


@bp.route('/')
def index():
    db = get_db()
    try:
        config_profiles = db.execute("SELECT * FROM config").fetchall()
        selected_config = db.execute("SELECT config_name FROM selected_config").fetchone()
        selected_config = selected_config["config_name"]
        print(f"SERVER: Selected config: {selected_config}")
    except db.Error as e:
        print(f"SERVER: DB error: {e}")
        return make_response({"error": "Could not fetch data."}, 400)
    return render_template('dashboard/index.html', config_profiles=config_profiles, selected_config=selected_config)


@bp.route('/config')
def config():
    with open("./dashboard/static/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

# region: config profiles

def validate_inputs(data, names):
    # old_name = data["old_name"]
    # name = data["name"]
    # on_ec_level = data["on_ec_level"]
    # on_light_level = data["on_light_level"]
    # off_light_level = data["off_light_level"]
    # temp_setpoint = data["temp_setpoint"]
    # temp_max = data["temp_max"]

    expected_keys = ["old_name", "name", "on_ec_level", "on_light_level", "off_light_level", "temp_setpoint", "temp_max"]
    if not all(key in data.keys() for key in expected_keys):
        return False, "Not enough data."

    for key,value in data.items():
        if key != "old_name":
            if value == "" or value is None:
                return False, f"{config_labels[key]} cannot be empty."
            if key != "name":
                try:
                    value = float(value)
                except ValueError:
                    return False, f"{config_labels[key]} must be a number."
                if value < 0:
                    return False, f"{config_labels[key]} must be a positive number."
                # set constraints
                if key == "on_ec_level" and 0 < value > 1000: return False, f'{config_labels[key]} value out of range.'
                if key == "on_light_level" and 0 < value > 100_000: return False, f'{config_labels[key]} value out of range.'
                if key == "off_light_level" and 0 < value > 100_000: return False, f'{config_labels[key]} value out of range.'
                if key == "temp_setpoint": None
                if key == "temp_max": None

            continue


        if value is None: # create new
            if data["name"] in names:
                return False, f"{data['name']} already exists." # duplicate name
        else:             # update existing
            if value not in names:
                return False, f"{data['old_name']} not found."  # cannot update non-existent profile
            if data["name"] != value and data["name"] in names:
                return False, f"{data['name']} already exists." # duplicate name

    return True, None

@bp.route('/edit', methods=['POST'])
@login_required
def create_config():
    db = get_db()

    data = request.json

    old_name = data["old_name"]
    data["name"] = data["name"].strip().lower()
    try:
        names = db.execute("SELECT config_name FROM config").fetchall()
        names = [name["config_name"] for name in names]
        ok, error = validate_inputs(data, names)
        if not ok:
            print(f"SERVER: Config error: {error}")
            return make_response({"error": error}, 400)

        if old_name is None: # create new
            db.execute("INSERT INTO config (config_name, on_ec_level, on_light_level, off_light_level, temp_setpoint, temp_max) VALUES (?, ?, ?, ?, ?, ?)",
                      (data["name"], data["on_ec_level"], data["on_light_level"], data["off_light_level"], data["temp_setpoint"], data["temp_max"]))
        else: # update existing
            db.execute("UPDATE config SET config_name = ?, on_ec_level = ?, on_light_level = ?, off_light_level = ?, temp_setpoint = ?, temp_max = ? WHERE config_name = ?",
                      (data["name"], data["on_ec_level"], data["on_light_level"], data["off_light_level"], data["temp_setpoint"], data["temp_max"], old_name))
        db.commit()
    except db.IntegrityError:
        error = f"{old_name} could not be updated."
        return make_response({"error": error}, 400)

    return make_response('', 204)


@bp.route('/delete', methods=['POST'])
@login_required
def delete_config():
    db = get_db()
    selected_config = db.execute("SELECT config_name FROM selected_config").fetchone()
    selected_config = selected_config["config_name"]
    data = request.json
    name = data["name"]

    if name == selected_config:
        return make_response({"error": "Cannot delete selected profile."}, 400)

    try:
        db.execute("DELETE FROM config WHERE config_name = ?", (name,))
        db.commit()
    except db.Error as e:
        print(f"SERVER: DB error: {e}")
        return make_response({"error": "Could not delete profile."}, 400)

    return make_response('', 204)


@bp.route('/update')
@login_required
def update_config_selection():
    db = get_db()
    name = request.args.get("name")
    print(f'SERVER: Selected config: {name}')
    # TODO: integrate with sensors
    # store selected config in DB
    try:
        db.execute("UPDATE selected_config SET config_name = ?", (name,))
        db.commit()
    except db.Error as e:
        print(f"SERVER: DB error: {e}")
        return make_response({"error": "Could not update selected config."}, 400)

    return make_response('', 204)

# endregion: config profiles


# TODO: wifi SSID and password input
# TODO: admin account management