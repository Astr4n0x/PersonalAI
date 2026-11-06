import requests
from urllib.parse import quote


def gdelt_news(query, max_results=5):

    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",

        # Only search recent news
        "timespan": "1d",

        # Keep it small = faster
        "maxrecords": max_results,

        "sort": "datedesc"
    }

    headers = {
        "User-Agent": "Jarvis-Personal-AI/1.0"
    }

    for attempt in range(2):

        try:

            print(
                f"📰 GDELT request "
                f"(attempt {attempt + 1})..."
            )

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=(3, 8)
            )

            print(
                "GDELT status:",
                response.status_code
            )

            if response.status_code == 429:

                print(
                    "GDELT rate limited."
                )

                return {
                    "success": False,
                    "error": "GDELT rate limit reached."
                }

            response.raise_for_status()

            # Make sure it actually returned JSON
            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            if "json" not in content_type.lower():

                print(
                    "GDELT returned:",
                    response.text[:300]
                )

                return {
                    "success": False,
                    "error": "GDELT returned non-JSON data."
                }

            data = response.json()

            articles = data.get(
                "articles",
                []
            )

            results = []

            for article in articles:

                results.append({
                    "title": article.get(
                        "title",
                        ""
                    ),

                    "url": article.get(
                        "url",
                        ""
                    ),

                    "source": article.get(
                        "domain",
                        ""
                    ),

                    "date": article.get(
                        "seendate",
                        ""
                    )
                })

            return {
                "success": True,
                "articles": results
            }

        except requests.exceptions.Timeout:

            print(
                "⏱️ GDELT timed out."
            )

            # Retry once
            if attempt == 0:
                continue

            return {
                "success": False,
                "error": "GDELT timed out after retry."
            }

        except requests.exceptions.ConnectionError as e:

            return {
                "success": False,
                "error": f"GDELT connection error: {e}"
            }

        except requests.exceptions.RequestException as e:

            return {
                "success": False,
                "error": f"GDELT request error: {e}"
            }

        except ValueError:

            return {
                "success": False,
                "error": "GDELT returned invalid JSON."
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }
            
            
result = gdelt_news(
    "Donald Trump",
    3
)

print(result)