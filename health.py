import os  # Operating system ke saath interact karne ke liye os module import kar raha hai
import random  # Random values generate karne ke liye random module import kar raha hai
import torch  # PyTorch ko import kar raha hai deep learning tasks ke liye
from flask import Flask, request, jsonify, render_template  # Flask components ko import kar raha hai web application banane ke liye
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification  # Transformers library se tokenizer aur model import kar raha hai
from langdetect import detect  # Language detect karne ke liye langdetect module import kar raha hai

app = Flask(__name__)  # Naya Flask application instance bana raha hai

os.environ['HF_HOME'] = 'D:/huggingface_cache'  # Hugging Face cache ke liye environment variable set kar raha hai

try:
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')  # DistilBERT tokenizer load kar raha hai
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)  # DistilBERT model load kar raha hai
except Exception as e:
    print(f"Error loading tokenizer or model: {e}")  # Agar model ya tokenizer load karne mein error aaye toh print kar raha hai
    exit()  # Program exit kar raha hai

# Illness ko corresponding products ke saath map karne wala dictionary
problem_to_dawai = {
   "cough": ("Marzanjosh", "https://aetmaad.co.in/product/al-marzanjosh", 300), 
    "malaria": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70), 
    "constipation": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70),  
    "peristalsis": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70),  
    "piles": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70),  
    "dysentery": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70), 
    "hepatomegaly": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70),  
    "spleenomegaly": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70), 
    "jaundice": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70),  
    "gouts": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70),  
    "rheumatism": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70),  
    "anaemia": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki", 70),  
    "blood pressure": ("Qalbi Nuska", "https://aetmaad.co.in/product/qalbi-nuska", 600),  
    "joint pain": ("Rumabil", "https://aetmaad.co.in/product/rumabil", 300),  
    "ulcers": ("Al-Rehan", "https://aetmaad.co.in/product/al-rehan", 300), 
    "sore throats": ("Multi Flora Honey", "https://aetmaad.co.in/product/multi-flora-honey", 600), 
    "skin irritations": ("Multi Flora Honey", "https://aetmaad.co.in/product/multi-flora-honey", 600),
    "hair loss": ("Tulsi Honey", "https://aetmaad.co.in/product/tulsi-honey", 600), 
    "infections": ("Tulsi Honey", "https://aetmaad.co.in/product/tulsi-honey", 600),
    "fever": ("Tulsi Honey", "https://aetmaad.co.in/product/tulsi-honey", 600) 
}

@app.route('/')  # Home page ka route
def index():
    return render_template('index.html')  # index.html template render kar raha hai

@app.route('/chatbot')  # Chatbot page ka route
def chatbot():
    name = request.args.get('name', 'User')  # Query parameters se user ka naam le raha hai ya default 'User'
    return render_template('chatbot.html', name=name)  # Chatbot template ko naam ke saath render kar raha hai

@app.route('/get_response', methods=['POST'])  # User response handle karne ka route
def get_response():
    user_message = request.json['message']  # User ke message ko le raha hai
    
    lang = detect(user_message)  # User ke message ki language detect kar raha hai
    
    # Different languages ke liye greeting messages ka dictionary
    greetings = {
        'en': [
            f"Hello {request.args.get('name', 'User')}! How can I assist you today?",  # English greeting
            f"Hi {request.args.get('name', 'User')}! What can I do for you?",  # Another English greeting
        ],
        
    }
    
    greeting_message = random.choice(greetings.get(lang, greetings['en']))  # Detected language ke hisaab se greeting select kar raha hai
    
    dawai_name, dawai_link = predict_dawai(user_message)  # Dawai ka naam aur link predict kar raha hai
    
    if dawai_name == "No specific recommendation":  # Agar koi specific recommendation nahi hai
        response = "I'm sorry, I don't have a recommendation for that."  # Sorry message return kar raha hai
    else:
        response = random.choice([  # Random response select kar raha hai
            f"{greeting_message} You are advised to take '{dawai_name}'. Check here: {dawai_link}",
            f"{greeting_message} I recommend '{dawai_name}'. See more here: {dawai_link}"
        ])
    
    return jsonify({'response': response})  # JSON format mein response return kar raha hai

def predict_dawai(problem):  # Dawai predict karne ka function
    inputs = tokenizer(problem, return_tensors="pt", padding=True, truncation=True, max_length=128)  # Tokenize kar raha hai
    with torch.no_grad():  # Gradient calculation ko disable kar raha hai
        outputs = model(**inputs)  # Model se predictions le raha hai
    predicted_class = torch.argmax(outputs.logits).item()  # Predicted class ko get kar raha hai
    dawai_info = problem_to_dawai.get(problem.lower(), ("No specific recommendation", ""))  # Dawai information le raha hai
    return dawai_info  # Dawai information return kar raha hai

if __name__ == '__main__':  # Agar script directly run ho rahi hai
    app.run(debug=True)  # Flask app ko debug mode mein run kar raha hai
