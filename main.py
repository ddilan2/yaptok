from fastapi import FastAPI, HTTPException
import uvicorn
import httpx
import re
import os 
from dotenv import load_dotenv
from google import genai

app = FastAPI()
load_dotenv()
api_key = os.getenv("SCRAPE_CREATORS_KEY")

@app.get("/summary")
def get_summary(tiktok_url: str) -> str:
    # Check validity of string
    if not re.match(r'^https://www\.tiktok\.com/t/[\w-]+/?$', tiktok_url):
        # todo: make this an error
        return "URL not valid"
    
    transcript = ""
    # Get transcript of video
    external_url = f"https://api.scrapecreators.com/v1/tiktok/video/transcript"
    headers = {
        "x-api-key": api_key
    }
    params = {'url' : tiktok_url}

    try: 
        response = httpx.get(external_url, headers=headers, params=params)
        response.raise_for_status()
        transcript = response.json()["transcript"]
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Scrape Creator Exception")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Scrape Creator Unavailable")

    # Get summary of transcript
    client = genai.Client()
    contents = "Summarize the key points from the following transcript and make sure to relay the most important/interesting points. Use 1-3 sentences, if a complete summary only requires one sentence, use one. Otherwise, use 2 or 3. \n" + transcript
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=contents)
    
    # Return the summary
    return response.text


if __name__ == "__main__":
    # Use the port assigned by the cloud provider, default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)