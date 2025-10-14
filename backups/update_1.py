# /main.py

@app.route("/update2", methods=["POST"])
def update2():
    user = get_current_user()
    user_id = user["id"]
    new_username = request.form.get("username")
    new_email = request.form.get("email")
    new_password = request.form.get("password")
    updated_fields = []

    # check for duplicate username
    if new_username:
        if dbh.user_exists(username=new_username, exclude_id=user_id):
            flash("Username unavailable", "error")
            return redirect(url_for("account"))
        dbh.update_user(user_ID=user_id, user_name=new_username)
        updated_fields.append("username")

    # check for duplicate email
    if new_email:
        if dbh.user_exists(email=new_email, exclude_id=user_id):
            flash("Email already in use", "error")
            return redirect(url_for("account"))
        dbh.update_user(user_ID=user_id, user_email=new_email)
        updated_fields.append("email")

    # update password if provided
    if new_password:
        dbh.update_user(user_ID=user_id, user_password=new_password)
        updated_fields.append("password")

    # refresh session with updated info
    updated_user = dbh.get_user_by_id(user_id)
    session["user"] = {
        "id": updated_user[0],
        "name": updated_user[1],
        "email": updated_user[2],
        "role": updated_user[4],
    }

    if updated_fields:
        details = ", ".join(updated_fields)
        flash(f"Account details updated!\n({details})", "success")
    else:
        flash("No changes made", "info")

    return redirect(url_for("account"))