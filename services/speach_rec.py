from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os


def listen():

    chrome_options = Options()

    # Auto allow microphone
    chrome_options.add_experimental_option(
        "prefs",
        {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
        },
    )

    chrome_options.add_argument("--use-fake-ui-for-media-stream")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    # HTML page
    html_code = """
    <html>
    <body>

    <h2>Listening...</h2>

    <script>

    window.finalTranscript = "";

    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {

        let transcript =
            event.results[event.results.length - 1][0].transcript;

        window.finalTranscript = transcript;
    };

    recognition.onerror = (event) => {
        console.log(event.error);
    };

    recognition.start();

    </script>

    </body>
    </html>
    """

    # Save temporary HTML file
    with open("voice.html", "w", encoding="utf-8") as f:
        f.write(html_code)

    file_path = "file:///" + os.path.abspath("voice.html")

    driver.get(file_path)

    print("Listening...")

    last_text = ""

    while True:

        text = driver.execute_script(
            "return window.finalTranscript"
        )

        if text is None:
            text = ""

        if text != last_text and text.strip() != "":
            last_text = text

            driver.quit()

            return text

        time.sleep(0.2)


# Example
while True:
    result = listen()
    print("You Said:", result)