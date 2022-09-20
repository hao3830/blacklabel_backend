from typing import overload
from multipledispatch import dispatch

code_601 = "Face Not Found"
code_602 = "Can Not Recognize Face"
code_603 = "Can Not Connect Micro-Service"
code_604 = "Login Failed"
code_605 = "Login Successful"
code_606 = "Permission Denied"
code_607 = "SignatureExpired"
code_608 = "BadSignature"
code_609 = "Wrong Input"
code_610 = "UserName Not Found"
code_611 = "No Matching Found"
code_612 = "Mode Not Found"
code_613 = "Out Of The Range"
code_614 = "Not Found"
code_615 = "TraceID not Found"
code_616 = "Matching Found"
code_617 = "ID not Found"
code_701 = "Register Error"
code_702 = "Encoded Image Error"
code_703 = "Face Search Error"
code_704 = "Score Too Slow"
code_705 = "Database SQL Process Error"
code_706 = "Data Already In Dataset"
code_707 = "You Have Nothing To Delete"
code_708 = "Exist Info"
code_709 = "Face Already In Register"
code_710 = "Door Access Denied"
code_711 = "Door Lost Connection"
code_801 = "Student Not Found"
code_900 = "SQL Execute Error"
code_901 = "A Foreign Key Constraint Fails"
code_902 = "Incorrect string value"
code_903 = "SQL Data Exists"
code_904 = "ImageSet Engine Error"
code_905 = "Today Augmented"
code_906 = "Person Not Found In Data SQL"
code_907 = "Data not Unified"
code_908 = "Name Already Exist"
code_909 = "Name Not Found"
code_1000 = "Done"
code_1001 = "Server Got Undetermined Error"
code_1100 = "Maintaining Time"
code_1110 = "Resource Exceeded"
code_1201 = "File Not Found"


class ErrorCode(object):
    def __init__(self, int_code, str_code, message):

        self.int_code = int_code
        self.str_code = str_code
        self.message = message

    def get_print(self):
        return {
            "code": self.int_code,
            "str_code": self.str_code,
            "message": self.message,
        }


class ErrorList(object):
    def __init__(self):
        self.int_list = {}
        self.str_list = {}

    def add_error(self, new_error):
        self.int_list[new_error.int_code] = new_error
        self.str_list[new_error.str_code] = new_error

    @dispatch(int)
    def __call__(self, code):
        return self.int_list[code].get_print()

    @dispatch(str)
    def __call__(self, code):
        return self.str_list[code].get_print()


rcode = ErrorList()

c609 = ErrorCode(int_code=609, str_code="WrongInput", message="Wrong Input")
rcode.add_error(c609)

c614 = ErrorCode(int_code=614, str_code="NotFound", message="Not Found")
rcode.add_error(c614)


c908 = ErrorCode(int_code=908, str_code="NameAlreadyExist", message="Name Already Exist")
rcode.add_error(c908)

c909 = ErrorCode(int_code=909, str_code="NameNotFound", message="Name Not Found")
rcode.add_error(c909)

c900 = ErrorCode(int_code=900, str_code="SQLError", message="SQL Execute Error")
rcode.add_error(c900)

c901 = ErrorCode(
    int_code=901,
    str_code="ForeignConstraintFails",
    message="A Foreign Key Constraint Fails",
)
rcode.add_error(c901)

c1000 = ErrorCode(int_code=1000, str_code="Done", message="Done")
rcode.add_error(c1000)

c1001 = ErrorCode(int_code=1001, str_code="ServerGotUndeterminedError", message="Server Got Undetermined Error")
rcode.add_error(c1001)

c1201 = ErrorCode(int_code=1201, str_code="FileNotFound", message="File Not Found")
rcode.add_error(c1201)

c4001 = ErrorCode(int_code=4001, str_code="DataNotAnalyse", message="Data Not Analyse")
rcode.add_error(c4001)

if __name__ == "__main__":
    print(rcode(609))
    print(rcode("WrongInput"))
