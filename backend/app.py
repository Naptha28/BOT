from fastapi import FastAPI, Depends, Body, Form
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
from fastapi import Body, Form
from db import get_session  # yields the list of doctors from JSON
from nlp import extract  # language + entity extraction
from fastapi import Request

app = FastAPI(title="MediBot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    text: str


def query_doctors(data: List[Dict], specialty: Optional[str], location: Optional[str]):
    res = data
    if specialty:
        res = [d for d in res if specialty.lower() in d["specialty"].lower()]
    if location:
        res = [d for d in res if location.lower() in d["location"].lower()]
    return res


@app.get("/")
def welcome():
    return {"message": "👋 Hello ! I’m MediBot. How can I assist you today?"}


@app.post("/chat/")
async def chat(
        request: Request,  # Request object to access raw data
        text_json: ChatRequest = Body(...),  # Use Body directly to ensure FastAPI parses the JSON
        doctors=Depends(get_session),  # Get doctors data from the session (or database)
):
    # Print raw request body
    body = await request.body()  # This will give you the raw body of the request
    print(f"Raw request body: {body}")

    # Extract the text from the request
    text = text_json.text
    print(f"Received text: {text}")

    if not text:
        return {"detail": "text parameter is required"}

    # Process the text for intent routing
    info = extract(text.lower())  # Extract info like specialty and location
    low = text.lower()
    print(f"Extracted info: {info}")  # Show the extracted info

    # ---------- Intent Routing ----------
    # Check if the message is related to booking
    if any(k in low for k in ("book", "prendre", "rdv")):  # BOOK
        spec, loc = info["specialty"], info["location"]
        print(f"Specialty: {spec}, Location: {loc}")  # Show the extracted specialty and location
        if not spec and not loc:
            return {"response": "Sure! Which specialty or city are you looking for?"}
        matches = query_doctors(doctors, spec, loc)
        print(f"Found matches: {matches}")  # Check if doctors were found
        if not matches:
            return {"response": "No doctor matches that. Try another specialty or location?"}
        names = ", ".join(d["name"] for d in matches[:5])
        return {"response": f"I found: {names}. Shall I book one for you?"}

    # Check if the message is related to cancellation
    if any(k in low for k in ("cancel", "annuler")):  # CANCEL
        return {"response": "Okay, I can cancel it. What’s your booking reference?"}

    # Check if the message is related to rescheduling
    if any(k in low for k in ("reschedule", "replanifier")):  # RESCHEDULE
        return {"response": "No problem. What new date/time would you like?"}

    # Default fallback message
    return {"response": "I’m not sure I understood. Could you rephrase?"}




