class Error:
    def __init__(self, err_id, err_msg):
        self.err_id = err_id
        self.err_msg = err_msg
        
    def to_dict(self):
        return {
            'err_id': self.err_id,
            'err_msg': self.err_msg
        }
        
ERROR_USERNAME = Error("MBA-01", "Invalid input for username")
ERROR_EMAIL = Error("MBA-02", "Invalid email address")
ERROR_PASS = Error("MBA-03", "Password needs to be at least 8 characters")
ERROR_NAME_TAKEN = Error("MBA-04", "Username already in use")
ERROR_MISSING_INFO = Error("MBA-05", "Information is missing from the register form")