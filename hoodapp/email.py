from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_signup_email_admin(name,receiver):
    # Creating message subject and sender
    subject = 'Welcome to HoodMap'
    sender = 'collindevtests@gmail.com'

    #passing in the context vairables
    text_content = render_to_string('email/email-admin.txt',{"name": name})
    html_content = render_to_string('email/email-admin.html',{"name": name})

    msg = EmailMultiAlternatives(subject,text_content,sender,[receiver])
    msg.attach_alternative(html_content,'text/html')
    msg.send()


def send_signup_email_resident(name,username,password,admin,hood,receiver):
    # Creating message subject and sender
    subject = 'Your HoodMap account'
    sender = 'collindevtests@gmail.com'

    #passing in the context vairables
    text_content = render_to_string('email/email-resident.txt',{"name": name, "username":username, "password":password, "admin":admin, "hood":hood})
    html_content = render_to_string('email/email-resident.html',{"name": name, "username":username, "password":password, "admin":admin, "hood":hood})

    msg = EmailMultiAlternatives(subject,text_content,sender,[receiver])
    msg.attach_alternative(html_content,'text/html')
    msg.send()