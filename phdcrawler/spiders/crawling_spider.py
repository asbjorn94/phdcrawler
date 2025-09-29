import scrapy
import json

class CrawlingSpider(scrapy.Spider):
    name = "phdcrawler"
    start_urls = ["https://jobportal.ku.dk/phd/"]
    custom_settings = {
        'FEEDS': {'data.json': {'format': 'json', 'overwrite': True}}
        }    

    def parse(self, response):
        #Check with existing json - anything new?
        newVacancies = []

        with open('data.json', 'r') as file:
            crawledPreviously = json.load(file)

        for vacancy in response.css(".vacancies").css(".vacancy-specs"):
            faculty_place_deadline = vacancy.css("td::text").getall()
            
            
            phd_title = vacancy.css("a::text").get()
            link = vacancy.css("a::attr(href)").extract()
            faculty = faculty_place_deadline[0]
            department = faculty_place_deadline[1]
            deadline = faculty_place_deadline[2]    
          
        #         #Does the present vacancy already exist in the database
            for i, item in enumerate(crawledPreviously):
                if phd_title == item['title']: 
                    break # Go on if phd already exists in db
                if i == len(crawledPreviously) - 1:
                    x = {
                         "title": phd_title,
                         "link": "https://jobportal.ku.dk" + link[0],
                         "department": department,
                         "date": deadline
                    }
                    newVacancies.append(x)

            yield {                
                "title": phd_title
            }
        
        #Send mail for each new vacancy
        if len(newVacancies) > 0:
            sendMail(newVacancies) 

import smtplib, os
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def sendMail(newVacancies):
    
    def email_alert(subject, html_body, to):
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText(html_body, "html"))
        # msg['subject'] = subject
        # msg['to'] = to
        msg['Subject'] = subject
        msg['To'] = to
        user = os.environ.get('from_email')
        msg['From'] = user

        # msg['from'] = user
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, os.environ.get('password'))
        server.sendmail(
            user, to, msg.as_string()
        )
        server.quit()

    html_body = """\
    <html>
    <body>
        <p>
            """
    for i, item in enumerate(newVacancies): 
        html_body = html_body + '<a href="' + item['link'] + '"> '+ item['title'] +'</a> ved '+item['department']+' <br>'

    html_body = html_body + """
        </p>
    </body>
    </html>
    """
    subject_ending = ""
    if len(newVacancies) == 1:
        subject_ending = "ny stilling"
    elif len(newVacancies) > 1:
        subject_ending = "nye stillinger"


    email_alert('KU PhD-agent: ' +str(len(newVacancies)) + ' ' + subject_ending + '.', 
            html_body,
            os.environ.get('to_email'))
    
    #Relevant page for me: https://jobportal.ku.dk/phd/
    #Start shell prompting: scrapy shell [link]
    #Shell promp to get all phd vacanies from KUs jobportal: response.css(".vacancies").css("a::text").getall()   
    #Shell prompt to get the rest of the info associated with position, including deadline for application: response.css(".vacancies").css("td::text").getall()