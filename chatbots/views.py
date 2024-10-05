import os
import torch
from django.http import JsonResponse
from django.shortcuts import render
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

os.environ['HF_HOME'] = 'D:/huggingface_cache'  # Change this to your path if needed
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=5)

problem_to_dawai = {
    "cough": ("Marzanjosh", "https://aetmaad.co.in/product/al-marzanjosh/"),
    "malaria": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/"),
    "blood pressure": ("Qalbi Nuska", "https://aetmaad.co.in/product/qalbi-nuska/"),
    "joint pain": ("Rumabil", "https://aetmaad.co.in/product/rumabil/"),
    "ulcers": ("Al-Rehan", "https://aetmaad.co.in/product/al-rehan/")
}

user_messages = []
current_question_index = 0
current_illness = None

def index(request):
    return render(request, 'index.html')

def chatbot_view(request):
    name = request.GET.get('name', 'User')
    greeting_message = f"Hi {name}! How can I assist you today?"
    return render(request, 'chatbot.html', {'greeting': greeting_message})

def get_response(request):
    global current_question_index, current_illness

    user_message = request.POST.get('message', '').lower().strip()
    user_messages.append(user_message)

    if current_illness is None:  # Detect illness first
        keywords_to_conditions = {
            "cough": "cough",
            "malaria": "malaria",
            "joint pain": "joint pain",
            "ulcers": "ulcers",
            "blood pressure": "blood pressure"
        }

        detected_illness = next((keyword for keyword in keywords_to_conditions if keyword in user_message), None)

        if detected_illness:
            current_illness = detected_illness
            response = "Ye samasya kab se hai?"
            current_question_index = 1
        else:
            response = "Aapko kya samasya hai? Agar aapko kisi bimari ke bare mein batana ho, toh mujhe zaroor batayein!"
    else:
        # Sequential questioning based on current question index
        if current_question_index == 1:  # Duration
            if any(char.isdigit() for char in user_message):  # Check for numeric values
                response = "Kya aapne iske liye koi dawai li hai?"
                current_question_index += 1
            else:
                response = "Aapka jawab samajh nahi aaya. Kya aap mujhe bata sakte hain ki aapko ye bimari kab se hai?"
        elif current_question_index == 2:  # Medication
            if "haan" in user_message:
                response = "Aapne kaunsi dawai li hai?"
            else:
                response = "Kya aapke parivaar mein kisi ko ye bimari hai?"
            current_question_index += 1
        elif current_question_index == 3:  # Family history
            dawai_name, dawai_link = problem_to_dawai[current_illness]
            response = f"For your condition '{current_illness}', I recommend taking '{dawai_name}'. Check here: {dawai_link}"
            current_question_index = 0  # Reset for next conversation
            current_illness = None  # Reset illness

    return JsonResponse({'response': response})
