import requests

apikey='AIzaSyDtpDief37bbxBATCc9BUZmDuZXku1dpTg'# the web api key


def new_user(email,password):
        details={
            'email':email,
            'password':password,
           'returnSecureToken': True
        }
        # send post request
        r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(apikey),data=details)
        #check for errors in result
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        #if the registration succeeded
        if 'idToken' in r.json().keys() :
            return {'status':'success','idToken':r.json()['idToken']}

def sign_in(email,password):
        details={
            'email':email,
            'password':password,
            'returnSecureToken': True
        }
        #Post request
        r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(apikey),data=details)
        #check for errors
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        #success
        if 'idToken' in r.json().keys() :
            return {'status':'success','idToken':r.json()['idToken']}
    

def VerifyEmail(idToken):
        headers = {
            'Content-Type': 'application/json',
        }
        data='{"requestType":"VERIFY_EMAIL","idToken":"'+idToken+'"}'
        r = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={}'.format(apikey), headers=headers, data=data)
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        if 'email' in r.json().keys():
            return {'status':'success','email':r.json()['email']}

def SendResetEmail(email):
        headers = {
            'Content-Type': 'application/json',
        }   
        data={"requestType":"PASSWORD_RESET","email":email}
        r = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={}'.format(apikey), data=data)
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        if 'email' in r.json().keys():
            return {'status':'success','email':r.json()['email']}

def SignInAnonymously():
        headers = {
            'Content-Type': 'application/json',
        }
        data='{"returnSecureToken":"true"}'
        r = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(apikey), headers=headers, data=data)
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        if 'idToken' in r.json().keys():
            return {'status':'success','idToken':r.json()['idToken']}

def GetData(idToken):
        details={
            'idToken':idToken
        }
        r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={}'.format(apikey),data=details)
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        if 'users' in r.json():
            return {'status':'success','data':r.json()['users']}

def DeleteAccount(idToken):
        details={
            'idToken':idToken
        }
        r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:delete?key={}'.format(apikey),data=details)
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
    
        return {'status':'success','data':r.json()}