#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from __future__ import print_function

import datetime

from atom.api import Atom, Str, Range, Bool, Value, Int, Tuple, observe
import enaml
import firebase_authentication_api
from enaml.qt.qt_application import QtApplication

console = Console()

auth = UserAuthentication()

class Person(Atom):
    """ A simple class representing a person object.

    """
    last_name = Str()

    first_name = Str()

    age = Range(low=0)

    dob = Value(datetime.date(1970, 1, 1))

    debug = Bool(False)

    @observe('age')
    def debug_print(self, change):
        """ Prints out a debug message whenever the person's age changes.

        """
        if self.debug:
            templ = "{first} {last} is {age} years old."
            s = templ.format(
                first=self.first_name, last=self.last_name, age=self.age,
            )
            print(s)

    @observe('dob')
    def update_age(self, change):
        """ Update the person's age whenever their date of birth changes

        """
        # grab the current date time
        now = datetime.datetime.utcnow()
        # estimate the person's age within one year accuracy
        age = now.year - self.dob.year
        # check to see if the current date is before their birthday and
        # subtract a year from their age if it is
        if ((now.month == self.dob.month and now.day < self.dob.day)
            or now.month < self.dob.month):
                age -= 1
        # set the persons age
        self.age = age


class Employer(Person):
    """ An employer is a person who runs a company.

    """
    # The name of the company
    company_name = Str()


class Employee(Person):
    """ An employee is person with a boss and a phone number.

    """
    # The employee's boss
    boss = Value(Employer)

    # The employee's phone number as a tuple of 3 ints
    phone = Tuple(Int())

    # This method will be called automatically by atom when the
    # employee's phone number changes
    def _observe_phone(self, val):
        print('received new phone number for %s: %s' % (self.first_name, val))

class Console(Atom):
    """A place to hold textual messages.
    """

    text = Str()

class UserAuthentication(Atom):
    email = Str()
    password = Str()
    result = Str()

    def new_user(self):
        if (self.email == "" or self.password == ""):
            self.result = "Please enter username and password"
        else:
            resultjson = firebase_authentication_api.new_user(self.email,self.password)

            log(str(resultjson))

            text = Str()

            status = str(resultjson['status'])


            if  status == 'error':
                text = "Error:"

            elif status == 'success':
                text = "Success!"

            if  'message' in resultjson.keys():

                message = str(resultjson['message'])
                
                if  message == 'INVALID_EMAIL':
                    text += " invalid email"
                if message == 'EMAIL_EXISTS':
                    text += " email already in use"
                if 'WEAK_PASSWORD' in message:
                    text += " Password should be at least 6 characters"

            self.result = text
    
    def sign_in(self):
        if (self.email == "" or self.password == ""):
            self.result = "Please enter username and password"    
        else:
            resultjson = firebase_authentication_api.sign_in(self.email,self.password)

            log(str(resultjson))

            text = Str()

            status = str(resultjson['status'])




            if  status == 'error':
                text = "Error:"

            elif status == 'success':
                text = "Success!"
            
            if  'message' in resultjson.keys():
                
                message = str(resultjson['message'])
                
                if  message == 'INVALID_EMAIL':
                    text += " invalid email"
            
                elif message == 'EMAIL_NOT_FOUND':
                    text += " email not found please sign up"

                elif message == 'INVALID_PASSWORD':
                    text += " invalid password"
            self.result = text

def log(s):
    console.text += str(s)
    console.text += '\n'



"""def main():


    # Import our Enaml EmployeeView
    with enaml.imports():
        from login_view import LoginView

    app = QtApplication()

    # Create a view and show it.
    view = LoginView(user_auth=auth, console_text=console)
    view.show()

    app.start()

if __name__ == '__main__':
    main()"""

        #title << "ADAPT login page"
'''Container:
        GroupBox: login_box:
            share_layout = True
            title = "Login Details"
            Container: 
                event sign_in_clicked
                Label: 
                    text << user_auth.result
                Form:
                    Label:
                        text = "Username"

                    Field: username:
                        placeholder = "Email"
                        text := user_auth.email

                    Label:
                        text = "Password"

                    Field: password:
                        placeholder = "Password"
                        text := user_auth.password
                        submit_triggers = ['lost_focus', 'return_pressed']
                    
                Container: log_buttons:

                    PushButton: login:
                        text = "Login"
                        clicked :: sign_in_clicked()

                    PushButton: newuser:
                        text = "Create Account"
                        clicked :: user_auth.new_user()
                Container:
                    MultilineField:
                        read_only = True
                        text << console_text.text'''