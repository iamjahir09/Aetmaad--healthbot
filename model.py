from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset #Datasets ko manage karne ke liye.
import pandas as pd #Data manipulation ke liye.
from sklearn.model_selection import train_test_split # Model evaluation aur dataset splitting ke liye.

# CSV file se data load karega. Yeh file symptoms_diseases.csv ke path par hai, jisme problem aur label columns hain.
file_path = "D:/symptoms_diseases.csv"
data = pd.read_csv(file_path)

# Pandas DataFrame ko datasets library ke Dataset format mein convert karega. Yeh format Hugging Face ke models ke saath compatible hai.
dataset = Dataset.from_pandas(data[['problem', 'label']])

# DistilBERT tokenizer ko load kiya gaya hai.

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

#  Is function mein symptoms ko tokenize karenge. padding="max_length" aur truncation=True ka matlab hai ki input ko fixed length par pad karna aur agar input length zyada hai to truncate karna.
def tokenize_function(examples):
    return tokenizer(examples['problem'], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Dataset ko train aur evaluation sets mein split karega. Yahaan test_size=0.2 ka matlab hai ki 20% data evaluation ke liye aur 80% training ke liye use hoga.
train_dataset, eval_dataset = train_test_split(tokenized_datasets, test_size=0.2, stratify=data['label'])


training_args = TrainingArguments(
    output_dir='./results',#Training ke results ko store karne ke liye directory.
    evaluation_strategy="epoch",#Evaluation ke liye strategy set ki gayi hai; yahaan epoch ka matlab hai ki har epoch ke baad evaluation kiya jayega.
    learning_rate=2e-5,#Training ke dauran learning rate set kiya gaya hai
    per_device_train_batch_size=8,# Training aur evaluation ke dauran kitne samples ek sath process honge.
    per_device_eval_batch_size=8,
    num_train_epochs=3,#Model ko kitni baar training data par train hoga
    weight_decay=0.01,#Regularization ke liye weight decay set kiya gaya hai.
)

#  Hugging Face ka Trainer class model training aur evaluation ke liye use hota hai. Yahaan model, training arguments, aur datasets ko pass kiya gaya hai.
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# train() function call karne se model training process start hota hai. Ismein model ko training dataset par fit kiya jata hai.
trainer.train()

# Training ke baad model aur tokenizer ko specified directory mein save kiya jata hai taaki future mein use kiya ja sake.
model.save_pretrained("distilbert-base-uncased")
tokenizer.save_pretrained('distilbert-base-uncased')
