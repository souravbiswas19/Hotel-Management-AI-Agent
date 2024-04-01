# Hotel Management AI Agent

## Objective
Build an AI Agent for a Hotel Management System that will have the power to answer the
queries of the customers about the hotel, room availability, contact number and the facilities
provided by the hotel.

## Features of AI Agent
1. Room Availability Check:
    - Allow users to get information about the number of rooms available in the Hotel.
2. Price Listing:
    - Allow users to know the prices of the hotel rooms of different categories.
3. Guest Services:
    - Provide information about hotel amenities, nearby attractions.
    - Facilitate room service requests, housekeeping, or maintenance queries.
4. Check-in/Check-out:
    - Support seamless check-in and check-out processes and timings
5. Feedback and Support:
    - Gather feedback from guests and handle support inquiries efficiently.

## Techstack
Python - Python language is supported by Langchain to build the Agent, FastAPI to build
the Backend and Chroma db as database, Python has been chosen.

## Knowledge Base
The knowledge base will contain information in a Directory of PDFs or a Word Documents which will be
queried for information retrieval.
The knowledge base will contain information like room availability details, check-in and
check-out details, facilities provided by the hotel, and different services for the guests.

## AI Models(LLMs)
Google Gemini-pro LLM model has been used as this model is free to use.

## Embedding Model
The embedding model used is Google's GenerativeAI Embeddinggs.

## API Endpoints
