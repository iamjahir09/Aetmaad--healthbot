import os  # Operating system ke saath interact karne ke liye os module import kar raha hai
import json  # JSON data handle karne ke liye json module import kar raha hai
from flask import Flask, request, jsonify, render_template  # Flask components ko import kar raha hai web application banane ke liye

app = Flask(__name__)  # Naya Flask application instance bana raha hai

user_data = {}  # User data store karne ke liye ek khaali dictionary initialize kar raha hai

def save_user_data(data):  # User data ko file mein save karne ka function
    with open('user_data.json', 'a') as f:  # 'user_data.json' ko append mode mein khol raha hai
        json.dump(data, f)  # Data ko JSON format mein file mein likh raha hai
        f.write('\n')  # Har entry ke liye ek newline character likh raha hai

# Illness ko corresponding products, links, aur prices ke saath map karne wala dictionary
problem_to_dawai = {
    "cough": ("Marzanjosh", "https://aetmaad.co.in/product/al-marzanjosh/", 300),
    "malaria": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "constipation": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "peristalsis": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "piles": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "dysentery": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "hepatomegaly": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "spleenomegaly": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "jaundice": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "gouts": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "rheumatism": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "anaemia": ("Sanna Makki", "https://aetmaad.co.in/product/sanna-makki/", 70),
    "blood pressure": ("Qalbi Nuska", "https://aetmaad.co.in/product/qalbi-nuska/", 600),
    "joint pain": ("Rumabil", "https://aetmaad.co.in/product/rumabil/", 300),
    "ulcers": ("Al-Rehan", "https://aetmaad.co.in/product/al-rehan/", 300),
    "sore throats": ("Multi Flora Honey", "https://aetmaad.co.in/product/multi-flora-honey/", 600),
    "skin irritations": ("Multi Flora Honey", "https://aetmaad.co.in/product/multi-flora-honey/", 600),
    "hair loss": ("Tulsi Honey", "https://aetmaad.co.in/product/tulsi-honey/", 600),
    "infections": ("Tulsi Honey", "https://aetmaad.co.in/product/tulsi-honey/", 600),
    "fever": ("Tulsi Honey", "https://aetmaad.co.in/product/tulsi-honey/", 600)
}

os.environ['HF_HOME'] = 'D:/huggingface_cache'  # Hugging Face cache ke liye environment variable set kar raha hai
current_question_index = 0  # Current question track karne ke liye index
current_illness = None  # Detected illness store karne ke liye variable

# Detected illness ke liye poochhe jaane wale sawalon ka dictionary
questions = {illness: [
    "How long have you been experiencing this issue?",  # Issue ke duration ke baare mein sawal
    "Are you currently taking any medication? (Yes/No)",  # Current medication ke baare mein sawal
    "Which medication are you taking?",  # Medication specify karne ka sawal
    "Do you have any allergies? (Yes/No)",  # Allergies ke baare mein sawal
    "What are you allergic to?",  # Allergies specify karne ka sawal
    "Tell me about your lifestyle. What is your diet like? Do you eat junk food? (Yes/No)",  # Lifestyle aur diet ke baare mein sawal
] for illness in problem_to_dawai.keys()}  # Saari illnesses ke liye dictionary comprehension

@app.route('/')  # Home page ka route
def index():
    return render_template('index.html')  # index.html template render kar raha hai

@app.route('/chatbot')  # Chatbot page ka route
def chatbot():
    name = request.args.get('name', 'User')  # Query parameters se user ka naam le raha hai ya default 'User'
    greeting_message = f"Hi {name}! How can I assist you today?"  # Greeting message bana raha hai
    return render_template('chatbot.html', name=name, greeting=greeting_message)  # Chatbot template ko naam aur message ke saath render kar raha hai

@app.route('/submit_form', methods=['POST'])  # Form submission handle karne ka route
def submit_form():
    global user_data  # user_data ko modify karne ke liye global declare kar raha hai
    user_data = request.json  # Request se JSON data le raha hai
    save_user_data(user_data)  # User data ko file mein save kar raha hai
    return jsonify({'message': "Form submitted successfully!"})  # Success message ko JSON format mein return kar raha hai

@app.route('/get_response', methods=['POST'])  # Chatbot responses handle karne ka route
def get_response():
    global current_question_index, current_illness  # Modify karne ke liye global variables declare kar raha hai
    user_message = request.json['message'].lower().strip()  # User ke message ko le raha hai aur normalize kar raha hai

    if "thank you" in user_message or "thanks" in user_message:  # Agar user shukriya keh raha hai
        return jsonify({'response': "You're welcome! If you need further assistance, feel free to ask!"})  # Response return kar raha hai

    if user_message in ["hi", "hello", "hey"]:  # Greetings check kar raha hai
        return jsonify({'response': "Hi! How can I assist you today?"})  # Greeting response return kar raha hai

    detected_illness = next((illness for illness in questions.keys() if illness in user_message), None)  # Message se illness detect kar raha hai

    if detected_illness:  # Agar illness detect hoti hai
        current_illness = detected_illness  # Current illness set kar raha hai
        current_question_index = 0  # Question index reset kar raha hai
        return jsonify({'response': questions[current_illness][current_question_index]})  # Illness ke liye pehla sawal return kar raha hai

    if current_illness:  # Agar ongoing illness discussion hai
        return handle_existing_case(user_message)  # Existing case ka response handle kar raha hai

    return jsonify({'response': "I'm sorry, but I don't have information about that illness 😞."})  # Unknown illness ke liye default response

def handle_existing_case(user_message):  # Ongoing case ke responses handle karne ka function
    global current_question_index, current_illness  # Modify karne ke liye global variables declare kar raha hai

    if current_question_index == 0:  # Agar pehla sawal hai
        current_question_index += 1  # Agle sawal par move kar raha hai
        return jsonify({'response': questions[current_illness][current_question_index]})  # Agla sawal return kar raha hai

    elif current_question_index == 1:  # Agar doosra sawal hai
        if "yes" in user_message:  # Agar jawab haan hai
            current_question_index += 1  # Agle sawal par move kar raha hai
        elif "no" in user_message:  # Agar jawab nahi hai
            current_question_index += 2  # Agle relevant sawal par move kar raha hai
        else:
            return jsonify({'response': questions[current_illness][current_question_index]})  # Valid response ke liye dobara pooch raha hai

    elif current_question_index == 2:  # Agar teesra sawal hai
        current_question_index += 1  # Agle sawal par move kar raha hai

    elif current_question_index == 3:  # Agar choutha sawal hai
        if "yes" in user_message:  # Agar jawab haan hai
            current_question_index += 1  # Agle sawal par move kar raha hai
        elif "no" in user_message:  # Agar jawab nahi hai
            current_question_index += 2  # Agle relevant sawal par move kar raha hai
        else:
            return jsonify({'response': questions[current_illness][current_question_index]})  # Valid response ke liye dobara pooch raha hai

    elif current_question_index == 4:  # Agar paanchwa sawal hai
        current_question_index += 1  # Agle sawal par move kar raha hai

    elif current_question_index == 5:  # Agar chhata sawal hai
        if "yes" in user_message:  # Agar jawab haan hai
            junk_food_response = "You should avoid junk food."  # Junk food se bachne ka response
            current_question_index += 1  # Agle sawal par move kar raha hai
            return jsonify({'response': junk_food_response})  # Junk food response return kar raha hai
        elif "no" in user_message:  # Agar jawab nahi hai
            current_question_index += 1  # Agle sawal par move kar raha hai

    if current_question_index >= len(questions[current_illness]):  # Agar sab sawal pooch liye gaye
        return jsonify({'response': generate_recommendation(current_illness)})  # Recommendation generate kar raha hai

    return jsonify({'response': questions[current_illness][current_question_index]})  # Current sawal ka response return kar raha hai

def generate_recommendation(illness):  # Recommendation generate karne ka function
    global current_question_index, current_illness  # Modify karne ke liye global variables declare kar raha hai

    product_name, link, price = problem_to_dawai[illness]  # Illness se product, link, aur price le raha hai
    response = (
        f"For relief from your problem, you might consider trying '{product_name}'. "  # Product ka naam batana
        f"It is known to help reduce {illness} and improve overall health. "  # Illness mein relief dene ki baat kar raha hai
        f"You can purchase it at a price of ₹{price} from here: {link}.\n\n"  # Purchase link aur price provide kar raha hai
        "**How to use:**\n"  # Use instructions shuru kar raha hai
        "1. Follow the instructions provided on the product page.\n"  # Product page par diye gaye instructions follow karne ko keh raha hai
        "2. Ensure to consult a healthcare professional if needed.\n\n"  # Healthcare professional se consult karne ki salah de raha hai
        "Take care and feel better soon! 😊"  # User ko care karne aur jaldi theek hone ki dua de raha hai
    )

    current_question_index = 0  # Question index reset kar raha hai
    current_illness = None  # Current illness reset kar raha hai
    return response  # Recommendation return kar raha hai

if __name__ == '__main__':  # Agar script directly run ho rahi hai
    app.run(debug=True)  # Flask app ko debug mode mein run kar raha hai
