import speech_recognition as sr
import pyttsx3
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import psutil
import logging
import threading
import queue

# Load AI model for decision making
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")

# Speech engine initialization
tts_engine = pyttsx3.init()

# Queue for handling speech commands
speech_queue = queue.Queue()


# Non-blocking speaking function
def speak_text(text):
    speech_queue.put(text)  # Add the text to the queue


# Function to handle speech queue processing
def speech_worker():
    while True:
        text = speech_queue.get()  # Get the next text from the queue
        if text:
            tts_engine.say(text)
            tts_engine.runAndWait()
        speech_queue.task_done()  # Mark the task as done


# Listening function with shorter timeout and phrase limit
def listen_for_commands():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for system commands...")
        try:
            audio = recognizer.listen(
                source, timeout=3, phrase_time_limit=5
            )  # Reduced timeout and phrase limit for faster response
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError as e:
            return f"Could not request results: {e}"
        except Exception as e:
            return "Listening error."


# Generate a response based on the user's input
def generate_response(input_text):
    input_text = input_text.lower()

    # Predefined responses for common interactions
    if "hello" in input_text or "hi" in input_text:
        response = "Hello! I am Iris, here to enhance your AR/VR experience."
    elif "what are you" in input_text or "who are you" in input_text:
        response = "I am Iris, designed to assist you with your AR/VR glasses. I'm still in development, continuously improving."
    elif "can you" in input_text and not is_capable(input_text):
        response = "I'm still evolving as part of AI OS. While I can't do that yet, future updates will include more capabilities."
    elif "how do you work" in input_text or "what can you do" in input_text:
        response = "I am designed to optimize resources and enhance your experience with Codin's MR glasses. As I'm still in development, I learn from interactions to get better over time."
    else:
        # Use the model to generate a response only for more complex queries
        inputs = tokenizer(input_text, return_tensors="pt")
        outputs = model.generate(
            inputs["input_ids"], max_length=100, num_beams=2, early_stopping=True
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return response


# Placeholder for checking capabilities (can be expanded later)
def is_capable(command):
    return False


# Monitoring functions for CPU and memory usage
def manage_cpu_usage():
    cpu_usage = psutil.cpu_percent()
    print(f"CPU Usage: {cpu_usage}%")
    if cpu_usage > 80:
        logging.warning("High CPU usage detected. AI optimizing tasks...")


def manage_memory_usage():
    memory_info = psutil.virtual_memory()
    print(f"Memory Usage: {memory_info.percent}%")
    if memory_info.percent > 85:
        logging.warning(
            "High memory usage detected. AI optimizing memory allocation..."
        )


# Main AI interaction function
def ai_interaction():
    while True:
        user_command = listen_for_commands()  # Keeps listening for new commands
        print(f"You said: {user_command}")

        response = generate_response(user_command)
        print(f"AI Response: {response}")
        speak_text(response)  # Add response to speech queue

        if "cpu usage" in user_command:
            manage_cpu_usage()
        elif "memory usage" in user_command:
            manage_memory_usage()


# Main AI loop using threading for real-time response
def ai_loop():
    print("AI module active. Voice command control enabled.")
    speak_text("System is now AI-powered and voice-controlled.")

    # Start the speech worker thread to process the speech queue
    speech_thread = threading.Thread(target=speech_worker)
    speech_thread.daemon = True
    speech_thread.start()

    # Run the interaction on a separate thread so it doesn't block
    interaction_thread = threading.Thread(target=ai_interaction)
    interaction_thread.daemon = True  # Set as daemon so it ends with the main program
    interaction_thread.start()


if __name__ == "__main__":
    ai_loop()

    # Keep the main thread alive so the program doesn't exit
    while True:
        pass  # Keeps the program running while the AI interaction runs in a separate thread
