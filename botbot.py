import logging
import os
from typing import Final
import numpy as np
from PIL import Image
import tensorflow as tf
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from bot_name import bot

BOT_USERNAME: Final = bot
with open("token.txt", "r") as f:
    TOKEN: Final = f.read().strip()

# Load your trained model
MODEL_PATH = "model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Image preprocessing parameters (adjust these based on your model's requirements)
IMG_SIZE = 224  # Common size for many models, adjust if needed
CLASS_NAMES = ['Cat', 'Dog']  # Adjust based on your model's output

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess the image for model prediction
    Adjust this function based on your model's requirements
    """
    try:
        # Load and resize image
        img = Image.open(image_path)
        img = img.convert('RGB')  # Ensure RGB format
        img = img.resize((IMG_SIZE, IMG_SIZE))
        
        # Convert to numpy array and normalize
        img_array = np.array(img)
        img_array = img_array.astype('float32') / 255.0  # Normalize to [0,1]
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        logging.error(f"Error preprocessing image: {e}")
        return None

def predict_image(image_path: str) -> str:
    """
    Make prediction using the loaded model
    """
    try:
        # Preprocess the image
        processed_image = preprocess_image(image_path)
        if processed_image is None:
            return "Error processing image"
        
        # Make prediction
        predictions = model.predict(processed_image)
        
        # Get the predicted class
        if len(predictions[0]) > 1:
            # Multi-class classification
            predicted_class_idx = np.argmax(predictions[0])
            confidence = predictions[0][predicted_class_idx]
            predicted_class = CLASS_NAMES[predicted_class_idx]
        else:
            # Binary classification
            confidence = predictions[0][0]
            predicted_class = CLASS_NAMES[1] if confidence > 0.5 else CLASS_NAMES[0]
            confidence = confidence if confidence > 0.5 else 1 - confidence
        
        return f"I think this is a **{predicted_class}** with {confidence:.2%} confidence!"
        
    except Exception as e:
        logging.error(f"Error making prediction: {e}")
        return "Sorry, I couldn't analyze the image. Please try again."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="🐱🐶 Welcome to the Dog vs Cat Classifier Bot!\n\n"
             "Send me a photo and I'll tell you whether it's a dog or cat!\n"
             "You can also use /custom for instructions."
    )

async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="📸 Send me a photo and I'll classify it as a dog or cat!\n\n"
             "Just upload an image and I'll analyze it for you."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle photo messages
    """
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔍 Analyzing your photo... Please wait!"
        )
        
        # Get the photo file
        photo_file = await update.message.photo[-1].get_file()
        
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Download the photo
        photo_path = f"temp/photo_{update.message.chat.id}_{update.message.message_id}.jpg"
        await photo_file.download_to_drive(photo_path)
        
        # Make prediction
        result = predict_image(photo_path)
        
        # Send result
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result,
            parse_mode='Markdown'
        )
        
        # Clean up - remove the temporary file
        try:
            os.remove(photo_path)
        except:
            pass
            
    except Exception as e:
        logging.error(f"Error handling photo: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, something went wrong while processing your photo. Please try again!"
        )

def handle_response(text: str) -> str:
    processed: str = text.lower().strip()
    if "hello" in processed:
        return "Hello! There, write /start"
    if "i love python" in processed:
        return "Python is great!"
    if any(word in processed for word in ["photo", "image", "picture", "pic"]):
        return "Please send me a photo directly (not as text). Just upload an image and I'll classify it!"
    return "I didn't understand. Send me a photo to classify it as dog or cat!"

async def handle_message(update: Update, context):
    message_type = update.message.chat.type
    text: str = update.message.text
    print(f"User {update.message.chat.id} sent a message: {text}")
    
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print(response)
    await update.message.reply_text(response)

if __name__ == '__main__':
    try:
        # Check if model file exists
        if not os.path.exists(MODEL_PATH):
            print(f"Error: Model file '{MODEL_PATH}' not found!")
            exit(1)
        
        print("Loading model...")
        # Model is already loaded at the top
        print("Model loaded successfully!")
        
        application = ApplicationBuilder().token(TOKEN).build()
        print("Bot starting...")
        
        # Add handlers
        start_handler = CommandHandler('start', start)
        custom_handler = CommandHandler('custom', custom)
        photo_handler = MessageHandler(filters.PHOTO, handle_photo)
        message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        
        application.add_handler(start_handler)
        application.add_handler(custom_handler)
        application.add_handler(photo_handler)
        application.add_handler(message_handler)
        
        print("Starting polling...")
        application.run_polling()
        
    except Exception as e:
        logging.error(f"Error starting bot: {e}")
        print(f"Failed to start bot: {e}")