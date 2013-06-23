def SendEmail():
   import subprocess
   import smtplib
   import socket
   from email.mime.text import MIMEText
   import datetime
   # Change to your own account information
   to = 'efinkg@gmail.com'
   gmail_user = 'autocoffeemaker@gmail.com'
   gmail_password = 'Caffeine'
   smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
   smtpserver.ehlo()
   smtpserver.starttls()
   smtpserver.ehlo
   smtpserver.login(gmail_user, gmail_password)
   today = datetime.date.today()
   # Very Linux Specific
   arg='ip route list'
   p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
   data = p.communicate()
   split_data = data[0].split()
   ipaddr = split_data[split_data.index('src')+1]
   my_ip = 'Your Coffee Is Ready'
   msg = MIMEText(my_ip)
   msg['Subject'] = 'Coffee Time'
   msg['From'] = gmail_user
   msg['To'] = to
   smtpserver.sendmail(gmail_user, [to], msg.as_string())
   smtpserver.quit()
