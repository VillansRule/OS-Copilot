import os
import platform
import requests
import subprocess
import random
import wikipedia
import webbrowser
from bs4 import BeautifulSoup
import atexit

# Define a simple memory for user interests
user_memory = {}

# Common sense knowledge base (example entries)
common_sense_knowledge = {
    "water": "Water is essential for life. It is a transparent, tasteless, odorless, and nearly colorless chemical substance.",
    "fire": "Fire is the result of a chemical reaction called combustion, which occurs when fuel combines with oxygen.",
}

# Temporary image file path
temp_image_path = os.path.join(os.getcwd(), 'temp_image.jpg')

# Function to delete the temporary image file
def cleanup():
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)
        print("Temporary image file deleted.")

# Register the cleanup function to be called at exit
atexit.register(cleanup)

# Function to open applications
def open_application(app_name):
    applications = {
        "prusaslicer": "prusa-slicer",
        "spotify": "spotify",
        "terminal": "gnome-terminal",
        "notepad": "notepad",
        "calculator": "gnome-calculator",
        "visualstudio": "code",
        "settings": "gnome-control-center",
        "microsoft edge": "microsoft-edge"
    }

    app_command = applications.get(app_name.lower())
    if app_command:
        try:
            if platform.system() == "Windows":
                os.startfile(app_command)
            elif platform.system() == "Darwin":
                subprocess.call(["open", "-a", app_command])
            else:
                subprocess.call([app_command])
            return f"Opening {app_name}..."
        except FileNotFoundError:
            return f"{app_name} is not installed. Please install it first."
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"
    else:
        return f"I don't know how to open {app_name}. Please specify a valid application."

# Function to fetch summary from Wikipedia
def fetch_wikipedia_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except Exception as e:
        return f"Sorry, I couldn't find any information on {query}."

# Function to fetch relevant information from Google search results
def fetch_google_info(query):
    """Fetches a relevant answer from Google search results."""
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try different possible classes for Google snippet
        snippet_classes = [
            'BNeawe iBp4i AP7Wnd',    # Main snippet text class
            'BNeawe s3v9rd AP7Wnd',   # Fallback for more detailed snippet
            'VwiC3b',                 # Class used for answer boxes
        ]

        for cls in snippet_classes:
            snippet = soup.find('div', class_=cls)
            if snippet:
                # Clean up snippet text
                text = snippet.get_text(separator=' ').strip()
                # Ensure it doesn't cut off mid-sentence
                if len(text) > 100:  # Choose an appropriate length
                    return text.split('.')[0] + '.'  # Return a complete thought
                return text

        return "Sorry, I couldn't find a direct answer via Google search."
    
    except Exception as e:
        return f"Error while fetching from Google: {str(e)}"

# Function to search for images on Google and open the image
def search_image(query):
    search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"
    try:
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for all image tags in the result page
        image_elements = soup.find_all('img')

        # Filter for images that have valid src attributes
        valid_images = [img['src'] for img in image_elements if 'src' in img.attrs and img['src'].startswith(('http://', 'https://'))]

        if valid_images:
            image_url = valid_images[0]  # Use the first valid image URL

            # Download the image
            image_response = requests.get(image_url)
            with open(temp_image_path, 'wb') as f:
                f.write(image_response.content)

            # Open the image in the default viewer
            if platform.system() == "Windows":
                os.startfile(temp_image_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", temp_image_path])
            else:
                subprocess.call(["xdg-open", temp_image_path])
            return f"Here’s the image for {query}, opening in viewer..."
        else:
            return "Sorry, I couldn't find any valid images for that query."
    except Exception as e:
        return f"Error while searching for images: {str(e)}"


# Function to perform Google search
def google_search(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)  # Open Google search in the default browser
    return f"Searching Google for: {query}"

# Function to perform YouTube search
def youtube_search(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)  # Open YouTube search in the default browser
    return f"Searching YouTube for: {query}"


# Function to respond to user queries
def respond_to_query(user_input):
    user_input = user_input.strip().lower()

    # Handle Linux-related queries by Googling the answer first
    linux_keywords = ["linux", "ubuntu", "debian", "linux mint"]
    if any(keyword in user_input for keyword in linux_keywords):
        return fetch_google_info(user_input)

    # Check for greetings
    if user_input in ["hello", "hi", "hey", "greet me"]:
        return "Hello! How can I assist you today?"

    # Check for Google or YouTube searches
    if user_input.startswith("google "):
        query = user_input[len("google "):].strip()
        return google_search(query)
    elif user_input.startswith("youtube "):
        query = user_input[len("youtube "):].strip()
        return youtube_search(query)

    # Check for image generation
    if user_input.startswith("image of "):
        description = user_input[len("image of "):].strip()
        return search_image(description)

    # Common sense topics
    for keyword in common_sense_knowledge:
        if keyword in user_input:
            return common_sense_knowledge[keyword]

    # Open applications
    if "open" in user_input:
        app_name = user_input.split("open", 1)[1].strip()
        return open_application(app_name)

    # Try fetching from Wikipedia
    wiki_response = fetch_wikipedia_summary(user_input)
    if "Sorry" not in wiki_response:
        return wiki_response

    # Default response if no condition is met
    return "Sorry, I didn't understand your query."

# Main function to run the chatbot
def main():
    print("OS Copilot! Ask me anything.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = respond_to_query(user_input)
        print("Bot:", response)

if __name__ == "__main__":
    main()
