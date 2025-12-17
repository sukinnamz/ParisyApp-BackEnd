class MockUser:
    def __init__(
        self,
        id=1,
        role="user",
        sub_role="warga"
    ):
        self.id = id
        self.name = "Test User"
        self.email = "test@mail.com"
        self.password = "hashed"
        self.role = role
        self.sub_role = sub_role
        self.address = "Test Address"
        self.phone = "08123"
        self.created_at = "2024-01-01"
        self.updated_at = "2024-01-01"
