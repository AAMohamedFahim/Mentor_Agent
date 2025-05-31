import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification

# Enable oneDNN optimization
torch.backends.mkldnn.enabled = True

# Load a pretrained RoBERTa model fine-tuned for emotion detection
tokenizer = RobertaTokenizer.from_pretrained('bhadresh-savani/roberta-base-emotion')
model = RobertaForSequenceClassification.from_pretrained('bhadresh-savani/roberta-base-emotion')

# Example text
text = "I'm feeling really happy about my performance today!"

# Tokenize input
inputs = tokenizer(text, return_tensors="pt")

# Use the model to predict emotions
with torch.no_grad():
    outputs = model(**inputs)

# Get predicted label
predicted_emotion = torch.argmax(outputs.logits, dim=-1)
print("Predicted emotion label:", predicted_emotion)