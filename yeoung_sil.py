import speech_recognition as sr
from googlesearch import search
import pyttsx3
import requests
from bs4 import BeautifulSoup
import threading

stop_flag = False  # Flag to stop the bot when set to True

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def search_google(query):
    search_results = list(search(query, num_results=3))
    return search_results

def get_page_summary(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([paragraph.text for paragraph in paragraphs[:2]])  # Limit to the first 3 paragraphs
        return content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return "Error fetching content."

def speak(text):
    global stop_flag
    stop_flag = False  # Reset the stop flag
    engine = pyttsx3.init()

    def on_end(name, completed):
        global stop_flag
        if not completed:
            stop_flag = True  # Set the stop flag if the speech is manually interrupted
        engine.endLoop()

    engine.connect('finished-utterance', on_end)
    engine.say(text)
    engine.startLoop()

def stop_listening():
    global stop_flag
    print("Stopping...")
    stop_flag = True  # Set the stop flag

if __name__ == "__main__":
    while True:
        user_input = recognize_speech()

        if user_input:
            if "stop" in user_input.lower():
                stop_listening()

            search_results = search_google(user_input)
            if search_results:
                response = "I found some results. Here is a summary of the content:\n"
                for result in search_results:
                    content = get_page_summary(result)
                    response += f"{content}\n\n"

                    if stop_flag:
                        break  # Break out of the loop if stop_flag is set during speech

                print(response)
                speak(response)
            else:
                response = "I couldn't find any relevant results."
                print(response)
                speak(response)
