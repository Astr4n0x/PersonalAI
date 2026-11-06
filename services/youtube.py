import webbrowser
from youtube_search import YoutubeSearch


def youtube_search(query: str, browser: str = "firefox"):
    """
    Search YouTube for the given query and open the top result
    in the specified browser (Firefox by default).

    Args:
        query: The search query string
        browser: Browser to use ('firefox', 'chrome', or 'default')

    Returns:
        str: Status message
    """
    # Search YouTube and get the top result
    results = YoutubeSearch(query, max_results=1).to_dict()

    if not results:
        return f"No YouTube results found for: {query}"

    top_video = results[0]
    video_id = top_video.get("id")
    video_title = top_video.get("title", "Unknown title")

    if not video_id:
        return f"Could not extract video ID for: {query}"

    # Build the direct video URL
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Select browser
    if browser.lower() == "firefox":
        try:
            browser_controller = webbrowser.get("firefox")
        except webbrowser.Error:
            browser_controller = webbrowser.get()
    elif browser.lower() == "chrome":
        try:
            browser_controller = webbrowser.get("chrome")
        except webbrowser.Error:
            browser_controller = webbrowser.get()
    else:
        browser_controller = webbrowser.get()

    # Open the top result video
    browser_controller.open(video_url)

    return f"Playing '{video_title}' on YouTube"