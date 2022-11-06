import uuid as uuid_class
import json
import inspect


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif isinstance(obj, dict):
            return obj
        elif isinstance(obj, uuid_class.UUID):
            return str(obj)
        elif isinstance(obj, object) or hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("_")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj


class CodeSequence:
    __slots__ = ('list', '_current_line_id')

    class _CodeString:
        __slots__ = ('uuid', 'code_string')

        def __init__(self, code_string: str = None, uuid: str = None):
            if uuid is None:
                self.uuid = str(uuid_class.uuid4())
            else:
                self.uuid = uuid
            self.code_string = code_string

        def __str__(self):
            return self.code_string

    def __init__(self):
        self._current_line_id = None
        self.list = []

    def add_code(self, code_string: str = None, uuid: str = None):
        self.list.append(self._CodeString(uuid=uuid, code_string=code_string))

    def next(self):
        response = False
        if self._current_line_id is None:
            if len(self.list) != 0:
                self._current_line_id = 0
                response = True
        else:
            if len(self.list) > (self._current_line_id + 1):
                self._current_line_id += 1
                response = True
            else:
                response = None
        return response

    def is_initialed(self):
        if self._current_line_id is None:
            return False
        else:
            return True

    def get_code(self):
        if self.is_initialed():
            return self.list[self._current_line_id]
        else:
            return None, "Code sequence not initialised"


# class Testing:
#     __slots__ = ("test_cases", "_project_location")
#
#     def __init__(self):
#         self.test_cases = []
#
#     def add_test_case(self, uuid: str, name: str, type_case: str):
#         self.test_cases.append(TestCases(uuid, name, type_case))
#
#
# class TestCases:
#     __slots__ = ('uuid', 'name', 'type_case', 'executing_code')
#
#     def __init__(self, uuid, name, type_case):
#         self.uuid = uuid
#         self.name = name
#         self.type_case = type_case
#         self.executing_code = ExecutingCode()

class LibrariesUses:
    __slots__ = ('list', )

    class _Library:
        __slots__ = ('from_path', 'element_name')

        def __init__(self, from_path, element_name):
            self.from_path = from_path
            self.element_name = element_name

    def __init__(self):
        self.list = []

    def append_library(self, from_path: str, element_name: str):
        self.list.append(self._Library(from_path=from_path, element_name=element_name))


class ExecutingCode:
    __slots__ = ('code_sequence', 'libraries', '_line_executed', '_project_location')

    def __init__(self):
        self.code_sequence = CodeSequence()
        self.libraries = LibrariesUses()
        self._line_executed = None
        self._project_location = '/home/vector/PullgerProject/pullgerLinkeIN_FULL/pullgerReflection/com_linkedin/tests/end_to_end/search.json'

    def append_code(self, code_string: str = None, uuid: str = None):
        self.code_sequence.add_code(uuid=uuid, code_string=code_string)

    def append_library(self, from_path: str, element_name: str):
        self.libraries.append_library(from_path=from_path, element_name=element_name)

    def next_line(self):
        if self._line_executed is True or self._line_executed is None:
            result_next_operation = self.code_sequence.next()
            if result_next_operation is True:
                self._line_executed = False
                return True, ""
            elif result_next_operation is False:
                return False, "Operation sequence is empy."
            elif result_next_operation is None:
                return False, "No next element"
        else:
            return False, "Current code not executed"

    def set_executed(self):
        self._line_executed = True

    def get_code_string(self):
        code = self.code_sequence.get_code()
        return str(code)

    def load_json(self):
        with open(self._project_location) as json_file:
            data = json.load(json_file)
            for cur_code_sequence in data["code_sequence"]["list"]:
                self.append_code(uuid=cur_code_sequence["uuid"], code_string=cur_code_sequence["code_string"])

    def save_json(self):
        with open(self._project_location, 'w', encoding='utf-8') as json_file:
            json_file.write(json.dumps(self, cls=ObjectEncoder, indent=2, sort_keys=True))
