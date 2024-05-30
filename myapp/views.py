from django.shortcuts import render, redirect
from .forms import ImageForm  # Import ImageForm from forms.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from google.cloud import vision
import google.generativeai as genai
import requests
import os
import uuid
import PIL.Image
from django.http import JsonResponse
from io import BytesIO

from .forms import WordForm
from .models import WordModel
from .models import ImageModel


import base64

UPLOAD_FOLDER = 'static'


# Function to configure the Google API key
def configure_google_api(api_key):
    genai.configure(api_key=api_key)


# Load the environment variables
# Configure the Google API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set")
configure_google_api(api_key)


# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
UPLOAD_FOLDER = 'static'

model = genai.GenerativeModel('gemini-1.5-flash')

def fetch_from_knowledge_graph(query):
    # api_key = GOOGLE_API_KEY
    api_endpoint = "https://kgsearch.googleapis.com/v1/entities:search"
    params = {
        "query": query,
        "key": api_key
    }
    response = requests.get(api_endpoint, params=params)
    data = response.json()
    return data

def display_knowledge_graph_data(data, query, upimage):
    results = []
    unique_names = set()  # Maintain a set of unique names
    
    if "itemListElement" in data:
        for item in data["itemListElement"]:
            name = item["result"]["name"]
            if name.lower() == query.lower() and name not in unique_names:  # Check if the name is unique
                item_image = item["result"].get("image", {}).get("contentUrl", "No image available")
                if item_image != "No image available":
                    description = item["result"].get("detailedDescription", {}).get("articleBody", "No detailed description available")
                    detailed_description = item["result"].get("detailedDescription", {}).get("url", "No detailed description available")
                    result_dict = {
                        "Name": name,
                        "Description": description,
                        "Detailed Description": detailed_description,
                        "item_image": item_image
                    }
                    results.append(result_dict)
                    unique_names.add(name)
                else:
                    model1 = genai.GenerativeModel('gemini-pro')
                    query="Give me a description of 60 words about" + name
                    response = model1.generate_content(query)
                    description=response.text
                    detailed_description = item["result"].get("detailedDescription", {}).get("url", "No detailed description available")
                    item_image=upimage
                    result_dict = {
                        "Name": name,
                        "Description": description,
                        "Detailed Description": detailed_description,
                        "item_image": item_image
                    }
                    results.append(result_dict)
    
                    unique_names.add(name)
    print(unique_names)
    return results


def display_knowledge_graph_data1(data, query):
    results = []
    unique_names = set()  # Maintain a set of unique names
    
    if "itemListElement" in data:
        for item in data["itemListElement"]:
            name = item["result"]["name"]
            print(name)
            if name.lower() == query.lower() and name not in unique_names:  # Check if the name is unique
                item_image = item["result"].get("image", {}).get("contentUrl", "No image available")
                description = item["result"].get("detailedDescription", {}).get("articleBody", "No detailed description available")

                detailed_description = item["result"].get("detailedDescription", {}).get("url", "No detailed description available")

                result_dict = {
                        "Name": name,
                        "Description": description,
                        "Detailed Description": detailed_description,
                        "item_image": item_image
                    }
                results.append(result_dict)
                unique_names.add(name)
               
    print(unique_names)

    return results


def home(request):
    return render(request, 'home.html')


def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            filename = str(uuid.uuid4()) + os.path.splitext(image_file.name)[-1]
            save_path = os.path.join(UPLOAD_FOLDER, filename)

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            with open(save_path, "wb") as image:
                content = image_file.read()
                image.write(content)

            img = PIL.Image.open(save_path)

            # Your image processing code here
            response = model.generate_content(["Identify the only some important things that are in the image.I should have the response only consist of names of all the objects name in a single word for each one without any stopwords in the object names separated by comma in the image", img], stream=True)
            response.resolve()

            res = response.text.split(',')
            res = [word.strip() for word in res if word.strip()]

            object_results = []
            for obj in res:
                data = fetch_from_knowledge_graph(obj)
                object_data = display_knowledge_graph_data(data, obj, save_path)
                object_results.extend(object_data)

            return JsonResponse({
                "res": res,
                "object_results": object_results,
            })
    else:
        form = ImageForm()
    return render(request, 'upload.html', {'form': form})




def input_word(request):
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            word_instance = form.save()
            search_word = word_instance.word
            object_results = []

            # Fetch data from the knowledge graph
            data = fetch_from_knowledge_graph(search_word)
            object_data = display_knowledge_graph_data1(data, search_word)
            object_results.extend(object_data)

            return JsonResponse({
                "object_results": object_results
            })
    else:
        form = WordForm()
    return render(request, 'search.html', {'form': form})



def camera_view(request):
    return render(request, 'camera.html')



def capture_image(request):
    if request.method == 'POST':
        # Get the uploaded image file
        image_file = request.FILES.get('image_file')

        # Save the image to a file
        with open(os.path.join(UPLOAD_FOLDER, 'captured_image.jpg'), 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # Open the image using PIL
        img = PIL.Image.open(os.path.join(UPLOAD_FOLDER, 'captured_image.jpg'))

        # Your image processing code here
        response = model.generate_content(["Identify the only some important things that are in the image.I should have the response only consist of names of all the objects name in a single word for each one without any stopwords in the object names separated by comma in the image", img], stream=True)
        response.resolve()

        res = response.text.split(',')
        res = [word.strip() for word in res if word.strip()]

        object_results = []
        for obj in res:
            data = fetch_from_knowledge_graph(obj)
            object_data = display_knowledge_graph_data(data, obj, os.path.join(UPLOAD_FOLDER, 'captured_image.jpg'))
            object_results.extend(object_data)

        # Save the image path to the database
        image_instance = ImageModel.objects.create(image='captured_image.jpg')
         
        # print(res)
        # print(object_results)
        # print(os.path.join(UPLOAD_FOLDER, 'captured_image.jpg'))

        return JsonResponse({
            "res": res,
            "object_results": object_results,
        })


    else:
        return JsonResponse({'error': 'POST request expected.'})
