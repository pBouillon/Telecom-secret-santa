"""
    :author: pbouillon  [https:/pbouillon.github.io/]
    :license: Unlicense [See LICENSE.txt]
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Student:
    """A TNCY student belonging to the 2019-2021 promotion

    Attributes:
        fullname    First and last name of the student
        mail        Student's mail address (___@telecomnancy.net)
    """
    fullname: str
    mail: str

    def first_name(self) -> str:
        """Get the first name of the student
        :return: The student's first name
        """
        return self.fullname.split()[0]
