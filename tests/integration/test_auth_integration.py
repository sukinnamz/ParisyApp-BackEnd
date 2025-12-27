def test_register_login_profile_logout_integration(client, init_database):
    # REGISTER USER WARGA
    register = client.post("/auth/register", json={
        "name": "User Test",
        "email": "user@test.com",
        "password": "user123",
        "role": "user",
        "sub_role": "warga",
        "address": "Jl Test",
        "phone": "08111111111"
    })
    assert register.status_code == 201

    # LOGIN USER
    login = client.post("/auth/login", json={
        "email": "user@test.com",
        "password": "user123"
    })
    assert login.status_code == 200

    token = login.json["token"]
    user_id = login.json["user"]["id"]

    # PROFILE (WAJIB PAKE ID)
    profile = client.get(
        f"/auth/profile/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile.status_code == 200
    assert profile.json["email"] == "user@test.com"

    # LOGOUT
    logout = client.get(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout.status_code == 200
    assert logout.json["message"] == "Logout berhasil"


def test_admin_delete_user_integration(client, init_database):
    # LOGIN ADMIN (DARI CONFTES)
    admin_login = client.post("/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    assert admin_login.status_code == 200

    admin_token = admin_login.json["token"]

    # REGISTER USER TARGET
    register = client.post("/auth/register", json={
        "name": "Target User",
        "email": "target@test.com",
        "password": "target123",
        "role": "user",
        "sub_role": "warga",
        "address": "Jl Target",
        "phone": "08222222222"
    })
    assert register.status_code == 201

    # AMBIL ID TARGET
    target_login = client.post("/auth/login", json={
        "email": "target@test.com",
        "password": "target123"
    })
    target_id = target_login.json["user"]["id"]

    # DELETE OLEH ADMIN
    delete = client.delete(
        f"/auth/delete/{target_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert delete.status_code == 200
    assert delete.json["message"] == "Akun berhasil dihapus"
