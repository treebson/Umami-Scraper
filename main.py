from recipe_scrapers import scrape_me
from google.cloud import firestore
from google.cloud import storage
from PIL import Image
from uuid import uuid4
import requests

def scrape(request):
    request_json = request.get_json()
    if request_json and 'url' in request_json:
        recipe_url = request_json['url']
    scraper = RecipeScraper(recipe_url)
    data = scraper.results
    recipe_id = upload_recipe_to_firestore(data)
    upload_image_to_storage(scraper.image_url, recipe_id)
    return recipe_id

def upload_recipe_to_firestore(data):
  db = firestore.Client()
  doc_ref = db.collection('recipes').document()
  data['image_path'] = f'images/recipes/{doc_ref.id}'
  doc_ref.set(data)
  return doc_ref.id

def upload_image_to_storage(image_url, recipe_id):
    save_image_to_tmp(image_url)
    client = storage.Client()
    bucket = client.get_bucket('umami-backend.appspot.com')
    blob = bucket.blob(f'images/recipes/{recipe_id}')
    blob.metadata = {"firebaseStorageDownloadTokens": uuid4()}
    blob.upload_from_filename('/tmp/image.jpg')
    blob.make_public()

def save_image_to_tmp(image_url):
    image = Image.open(requests.get(image_url, stream=True).raw)
    if not image.mode == 'RGB':
        image = image.convert('RGB')
    image.save('/tmp/image.jpg', format='JPEG')

class RecipeScraper:
    def __init__(self, url):
        self.scraper = scrape_me(url, wild_mode=True)
        self.results = {
          'url': url,
          'host': self.host(),
          'title': self.title(),
          'total_time': self.total_time(),
          'yields': self.yields(),
          'ingredients': self.ingredients(),
          'instructions': self.instructions(),
        }
        self.image_url = self.image_url()
        
    def host(self):
        return self.safe_get(self.scraper.host)
    
    def title(self):
        return self.safe_get(self.scraper.title)
    
    def total_time(self):
        return self.safe_get(self.scraper.total_time)
    
    def yields(self):
        return self.safe_get(self.scraper.yields)
    
    def ingredients(self):
        return self.safe_get(self.scraper.ingredients)
    
    def instructions(self):
        instructions = self.safe_get(self.scraper.instructions)
        if instructions != None:
            instructions = instructions.split("\n")
            instructions = [x.strip() for x in instructions]
        return instructions

    def image_url(self):
        return self.safe_get(self.scraper.image)
    
    def safe_get(self, f):
        try:
            return f()
        except:
            return None