class CourseNotFound(Exception):
    def __init__(
        self,
        name: str,
        message: str = "Course with such name is not found."
    ):
        self.name = name
        self.message = message

    def __str__(self):
        return f'{self.name} : {self.message}'
