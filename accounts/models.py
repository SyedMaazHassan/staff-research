from django.db import models
from .chatgpt import OpenAICall
from .web_scraper import WebScraper


# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver

class ScrapRequest(models.Model):
    request_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return str(self.request_id)

# Create your models here.
class Website(models.Model):
    request = models.ForeignKey(ScrapRequest, on_delete=models.CASCADE, null=True, blank=True)
    url = models.URLField()
    is_success = models.BooleanField(default=False)
    org_id = models.CharField(max_length = 255)


    def scrap_staff(self):
        try:
            web_scraper = WebScraper(self.url)
            web_scraper.scrape_html()

            chatgpt = OpenAICall(web_scraper.content)
            chatgpt.get_ai_response()

            staff_list = chatgpt.staff_list

            if len(staff_list) == 0:
                raise Exception("No Staff member found.")

            for staff in staff_list:
                staff_member = StaffMember.objects.create(
                    name = staff.get('name'),
                    email = staff.get('email'),
                    job_title = staff.get('job_title'),
                    website = self
                )    
                print(staff_member, 'created')
            self.is_success = True

        except Exception as e:
            print(str(e))
            self.is_success = False
        self.save()

    def __str__(self):
        return self.url
    

class StaffMember(models.Model):
    name = models.CharField(max_length = 255, null=True, blank = True)
    email = models.CharField(max_length = 255, null=True, blank = True)
    job_title = models.CharField(max_length = 255, null=True, blank = True)
    website = models.ForeignKey(Website, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.name} {self.email}'