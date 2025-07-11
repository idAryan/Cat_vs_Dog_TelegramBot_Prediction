# Cat vs Dog Prediction Telegram Bot

Implemented a convolutional neural network (2 Convo + 2 Dense Layer) trained on catvsdog dataset. Extracted tflite format, and used python-telegram-bot for realtime integration with telegram bot.

---

## 🔍 Project Overview

Simple Cat vs Dog Classification. Whenever user sends a Photo to the telegram, it predicts using trained model and replies back

##  Model Architecture

The model is a **Convolutional Neural Network (CNN)** trained from scratch using the [Dogs vs Cats dataset](https://www.microsoft.com/en-us/download/details.aspx?id=54765).  
Frameworks used:
- TensorFlow / Keras
- NumPy, Matplotlib for EDA
- OpenCV for preprocessing

```python
<img width="670" height="462" alt="image" src="https://github.com/user-attachments/assets/7f0ec93a-ddad-495f-8a1d-0afc73bdcb7e" />

