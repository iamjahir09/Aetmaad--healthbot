import os  # Operating system ke functions ko import karna
import json  # JSON data handling ke liye import karna
import re  # Regular expressions ke liye import karna
from flask import Flask, request, jsonify, render_template  # Flask framework se zaroori functions ko import karna
import sqlite3  # SQLite database ke liye import karna

app = Flask(__name__)  # Flask app ka instance banana

user_data = {}  # User data ko store karne ke liye dictionary
current_question_index = 0  # Current question ka index track karne ke liye
current_illness = None  # Current illness ko track karne ke liye

def save_conversation(user_message, bot_response):
    conn = sqlite3.connect('healthbot_conversations.db')  # Database se connect karna
    cursor = conn.cursor()  # Cursor object banana
    cursor.execute(''' 
        INSERT INTO conversations (user_message, bot_response, timestamp) 
        VALUES (?, ?, CURRENT_TIMESTAMP) 
    ''', (user_message, bot_response))  # Data ko insert karna
    conn.commit()  # Changes ko commit karna
    conn.close()  # Database connection band karna

def save_user_data(data):  # Function jo user data ko JSON file mein save karta hai
    with open('user_data.json', 'a') as f:  # JSON file ko append mode mein kholna
        json.dump(data, f)  # Data ko JSON format mein write karna
        f.write('\n') 

def get_chat_history(client_name):
    conn = sqlite3.connect('healthbot_conversations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_message, bot_response, timestamp FROM conversations ORDER BY timestamp DESC')
    conversations = cursor.fetchall()
    conn.close()

    # Filter conversations for the specific user
    chat_history = [{'user_message': row[0], 'bot_response': row[1], 'timestamp': row[2]} for row in conversations]
    return chat_history

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
    "skin irritations": ("Multi Flora Honey ", "https://aetmaad.co.in/product/multi-flora-honey", 600),
    "hair loss": ("Tulsi Honey", "https://aetmaad.co.in/product/tulsi-honey", 600), 
    "infections": ("Tulsi Honey", "https://aetmaad.co.in/product/tulsi-honey", 600),
    "fever": ("Tulsi Honey", "https://aetmaad.co.in/product/tulsi-honey", 600) 
}

questions = {
    illness: [
        "How long have you been experiencing this issue?",  
        "Are you currently taking any medication? ( Yes/No)",  
        "If yes, which medication are you taking?",  
        "Do you have any allergies? (Yes/No)",  
        "If yes, what are you allergic to?",  
        "Tell me about your lifestyle. Do you eat junk food? (Yes/No)",  
        "Do you have a family history of any medical conditions? (Yes/No)",  
        "Do you smoke? (Yes/No)",  
        "Do you consume alcohol? (Yes/No)", 
        "How often do you exercise? (Daily/Weekly/Rarely/Never)", 
        "Do you have any chronic illnesses? (Yes/No)",  
        "If yes, please specify.", 
        "Are you currently following any specific diet? (Yes/No)", 
        "If yes, please describe."  
    ] for illness in problem_to_dawai.keys()
}

def analyze_sleep_and_weight(user_data):  # Function jo sleep aur weight ka analysis karta hai
    sleep_time = user_data.get('sleepTime')  # User ke sleep time ko lena
    wake_time = user_data.get('wakeTime')  # User ke wake time ko lena
    age = user_data.get('age')  # User ki age lena
    weight = user_data.get('weight')  # User ka weight lena

    try:
        age = float(age)  # Age ko float mein convert karna
        weight = float(weight)  # Weight ko float mein convert karna
    except (ValueError, TypeError):  # Agar conversion mein error aaye toh
        age = None  # Age ko None set karna
        weight = None  # Weight ko None set karna

    recommended_sleep_time = "10:00 PM"  # Recommended sleep time
    recommended_wake_time = "06:00 AM"  # Recommended wake time

    sleep_quality = "not good"  # Default sleep quality
    if sleep_time and wake_time:  # Agar sleep time aur wake time hain
        if sleep_time <= recommended_sleep_time and wake_time <= recommended_wake_time:  # Agar dono recommended se kam ya barabar hain
            sleep_quality = "good"  # Sleep quality achi hai

    age_weight_ratio = None  # Age to weight ratio ko initialize karna
    ratio_quality = "not good"  # Default ratio quality
    if age is not None and weight is not None:  # Agar age aur weight dono hain
        age_weight_ratio = weight / age  # Ratio calculate karna
        ratio_quality = "good" if age_weight_ratio < 2.5 else "not good"  # Ratio quality check karna
    
    return sleep_quality, recommended_sleep_time, recommended_wake_time, age_weight_ratio, ratio_quality  # Results return karna

@app.route('/')  # Home route
def index():  # Function jo index page render karta hai
    return render_template('index.html')  # index.html template ko render karna

@app.route('/submit_form', methods=['POST'])  # Form submission route
def submit_form():  # Function jo user data ko handle karta hai
    global user_data  # Global user_data variable ka use
    user_data = request.json  # User data ko request se lena
    save_user_data(user_data)  # User data ko save karna
    return jsonify({'status': 'success', 'message': 'User    data saved successfully!'})  # Success response

@app.route('/chatbot')  # Chatbot route
def chatbot():  # Function jo chatbot page render karta hai
    name = user_data.get('clientName', 'User  ')  # Client ka naam lena
    greeting_message = f"Hi {name}! How can I assist you today?"  # Greeting message tayar karna

    chat_history = get_chat_history(name)
    if chat_history:
        history_summary = "You have a conversation history with us. Here's a summary: "
        for conversation in chat_history:
            history_summary += f":User  {conversation['user_message']}\nBot: {conversation['bot_response']}\n"
    else:
        history_summary = "You have no previous conversations. How can I assist you today?"

    return render_template('chatbot.html', name=name, greeting=greeting_message, history=history_summary)  # Chatbot template render karna

@app.route('/get_response', methods=['POST'])  # Response generation route
def get_response():  # Function jo user ke message ka response generate karta hai
    global current_illness, current_question_index  # Global variables ka use

    user_message = request.json['message'].lower().strip()  # User message ko process karna

    if "ok thanks" in user_message:  # Agar user "ok thanks" keh raha hai
        response = "You're welcome! If you need further assistance, feel free to ask!"  # Thank you ka response
        save_conversation(user_message, response)  # Conversation ko save karna
        return jsonify({'response': response})  # Response return karna

    if "how are you" in user_message:  # Agar user "how are you" poochta hai
        response = "I'm here to assist you with your health inquiries!"  # Response dena
        save_conversation(user_message, response)  # Conversation ko save karna
        return jsonify({'response': response})  # Response return karna

    if "hi" in user_message:  # Agar user "hi" keh raha hai
        name = user_data.get('clientName', "Client Name")  # Client ka naam lena
        response = f"Hi {name}! I am Aetmaad, your friendly health bot. How can I assist you today?"  # Greeting response
        save_conversation(user_message, response)  # Conversation ko save karna
        return jsonify({'response': response})  # Response return karna

    if "help" in user_message:  # Agar user "help" maang raha hai
        response = "I can help you with medical recommendations based on your symptoms."  # Help ka response
        save_conversation(user_message, response)  # Conversation ko save karna
        return jsonify({'response': response})  # Response return karna

    detected_illness = next((illness for illness in questions.keys() if illness in user_message), None)  # Illness detect karna

    if detected_illness:  # Agar illness detect hui
        current_illness = detected_illness  # Current illness ko set karna
        current_question_index = 0  # Question index ko reset karna
        response = questions[current_illness][current_question_index]  # Pehla question return karna
        save_conversation(user_message, response)  # Conversation ko save karna
        return jsonify({'response': response})  # Response return karna

    if current_illness:  # Agar current illness set hai
        if "thanks" in user_message:  # Agar user "thanks" keh raha hai
            response = "You're welcome! Have a great day! 😊"  # Response dena
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna
        return handle_existing_case(user_message)  # Existing case ko handle karna

    response = "I'm sorry, but I don't have information about that illness 😞."  # Agar illness nahi hai
    save_conversation(user_message, response)  # Conversation ko save karna
    return jsonify({'response': response})  # Response return karna

def handle_existing_case(user_message):  # Function jo existing case ko handle karta hai
    global current_question_index, current_illness  # Global variables ka use

    if current_question_index == 0:  # Duration question
        if re.match(r'^\d+\s+(to\s+\d+\s+)?(days?|weeks?|months?|years?)$', user_message):  # Agar format sahi hai
            current_question_index += 1  # Index ko badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna
        else:
            response = "Please answer in the format 'X days', 'X weeks', 'X months', 'X years', or 'X to Y days/weeks/months/years'."  # Format error message
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna

    elif current_question_index == 1:  # Medication question
        if "yes" in user_message:  # Agar user "yes" keh raha hai
            current_question_index += 1  # Next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna
        else:
            current_question_index += 2  # Agar "no" hai, toh next do prashn skip karna
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save k arna
            return jsonify({'response': response})  # Response return karna

    elif current_question_index == 2:  # Medication details
        current_question_index += 1  # Next question index badhana
        response = questions[current_illness][current_question_index]  # Next question return karna
        save_conversation(user_message, response)  # Conversation ko save karna
        return jsonify({'response': response})  # Response return karna

    elif current_question_index == 3:  # Allergy question
        if "yes" in user_message:  # Agar user "yes" keh raha hai
            current_question_index += 1  # Next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna
        else:
            current_question_index += 2  # Agar "no" hai, toh next do prashn skip karna
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna

    elif current_question_index == 4:  # Allergy details
        current_question_index += 1  # Next question index badhana
        response = questions[current_illness][current_question_index]  # Next question return karna
        save_conversation(user_message, response)  # Conversation ko save karna
        return jsonify({'response': response})  # Response return karna

    elif current_question_index == 5:  # Lifestyle question
        if "yes" in user_message:  # Agar user "yes" keh raha hai
            current_question_index += 1  # Next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna
        else:
            current_question_index += 1  # Agar "no" hai, toh next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna

    elif current_question_index == 6:  # Family history question
        if "yes" in user_message:  # Agar user "yes" keh raha hai
            response = "Please describe."  # Detail description ka prashn
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna
        else:
            current_question_index += 1  # Agar "no" hai, toh next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna

    elif current_question_index == 7:  # Alcohol consumption question
        if "yes" in user_message:  # Agar user "yes" keh raha hai
            current_question_index += 1  # Next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna
        else:
            current_question_index += 1  # Agar "no" hai, toh next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna

    elif current_question_index == 8:  # Exercise frequency question
        current_question_index += 1  # Next question index badhana
        response = questions[current_illness][current_question_index]  # Next question return karna
        save_conversation(user_message, response)  # Conversation ko save karna
        return jsonify({'response': response})  # Response return karna

    elif current_question_index == 9:  # Chronic illness question
        if "yes" in user_message:  # Agar user "yes" keh raha hai
            current_question_index += 1  # Next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save k arna
            return jsonify({'response': response})  # Response return karna
        else:
            current_question_index += 1  # Agar "no" hai, toh next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna

    elif current_question_index == 10:  # Chronic illness details
        current_question_index += 1  # Next question index badhana
        response = questions[current_illness][current_question_index]  # Next question return karna
        save_conversation(user_message, response)  # Conversation ko save karna
        return jsonify({'response': response})  # Response return karna

    elif current_question_index == 11:  # Diet question
        if "yes" in user_message:  # Agar user "yes" keh raha hai
            current_question_index += 1  # Next question index badhana
            response = questions[current_illness][current_question_index]  # Next question return karna
            save_conversation(user_message, response)  # Conversation ko save karna
            return jsonify({'response': response})  # Response return karna
        else:
            return finalize_response()  # Agar "no" hai, toh response finalize karna

    elif current_question_index == 12:  # Diet details
        return finalize_response()  # Finalize response dena

    return finalize_response()  # Final response dena

def finalize_response():  # Function jo final response generate karta hai
    global current_illness  # Current illness ko global declare karna
    recommendations = generate_recommendations(current_illness)  # Recommendations generate karna

    sleep_quality, recommended_sleep_time, recommended_wake_time, age_weight_ratio, ratio_quality = analyze_sleep_and_weight(user_data)  # Sleep aur weight analysis

    # Age weight ratio ko handle karna agar None hai
    if age_weight_ratio is None:
        age_weight_ratio_message = "not available"  # Ratio nahi hai
    else:
        age_weight_ratio_message = f"{age_weight_ratio:.2f}"  # Ratio ko format karna

    sleep_analysis = (  # Sleep analysis message tayar karna
                      f"Recommended sleep time is {recommended_sleep_time} and wake time is {recommended_wake_time}. "
                      f"Your age to weight ratio is {age_weight_ratio_message}, which is considered {ratio_quality}.")
    
    current_illness = None  # Next session ke liye illness ko reset karna
    return jsonify({'response': recommendations + sleep_analysis})  # Recommendations aur sleep analysis return karna

def generate_recommendations(current_illness):  # Function jo recommendations generate karta hai
    if current_illness in problem_to_dawai:  # Agar current illness ka dawai hai
        dawa_info = problem_to_dawai[current_illness]  # Dawai information lena
        return f"Thanks for information !😊 Based on your symptoms, I recommend {dawa_info[0]} for {current_illness}. You can find it here: {dawa_info[1]} at the cost of {dawa_info[2]}.Take care 😊"  # Recommendation message
    return "I'm sorry, I couldn't find a recommendation for that illness."  # Agar recommendation nahi mil raha

if __name__ == '__main__':  # Main function
    app.run(debug=True)  # Flask app ko run karna