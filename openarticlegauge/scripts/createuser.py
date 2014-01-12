from openarticlegauge.models import Account

def input_password():
    password = None
    while password is None:
        password = request_password()
    return password

def request_password():
    password = getpass.getpass()
    confirm = getpass.getpass("Confirm Password:")
    if password != confirm:
        print "passwords do not match - try again!"
        return None
    return password

if __name__ == "__main__":
    import argparse, getpass
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-e", "--email", help="email address of user - this will be your username.  Use an existing username to update the password")
    parser.add_argument("-p", "--password", help="password for the new or existing user.  If omitted, you will be prompted for one on the next line")
    
    args = parser.parse_args()
    
    if not args.email:
        print "Please specify an email address with the -e option"
        exit()
    
    email = args.email
    password = None
    
    if args.password:
        password = args.password
    else:
        password = input_password()
    
    acc = Account.pull_by_email(email)
    if not acc:
        acc = Account(email=email)
    acc.set_password(password)
    acc.save()
