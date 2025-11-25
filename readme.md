# 🤖 Day 5: Simple FAQ SDR + Lead Capture Agent

[![Challenge Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)](https://github.com/[YOUR_GITHUB_USER]/[YOUR_REPO_NAME])
[![Challenge](https://img.shields.io/badge/Murf%20AI-Voice%20Agent%20Challenge-blue.svg)](https://murf.ai/)

This project represents the solution for Day 5 of the **Murf AI Voice Agent Challenge**, which focuses on building a functional Sales Development Representative (SDR) to handle initial inquiries and capture qualified leads. The agent is built for the Indian super-app **Tata Neu**.

## ✨ Primary Goal Completion

The agent successfully meets all primary requirements by integrating conversational flow with essential data capture logic:

1.  **SDR Persona:** Clearly defined LLM instructions set the agent's persona as a helpful, focused SDR for Tata Neu.
2.  **FAQ Handling:** The agent answers product and pricing questions by querying an internal `FAQ_CONTENT` knowledge base, ensuring factual accuracy.
3.  **Lead Qualification:** The agent utilizes the `capture_lead_data` function to systematically collect and store seven key lead fields (Name, Email, Company, Role, Use case, Team size, Timeline).
4.  **Call Summary & Storage:** The `end_call_summary` tool generates a polite verbal summary for the user and writes all collected data to a JSON file (`captured_lead_data.json`) for backend integration.

## 🛠️ Technical Deep Dive: Robust Lead Capture

The most critical challenge was ensuring data integrity, especially when capturing sensitive information like email addresses via Speech-to-Text (ASR).

### 1. Robust Email Cleaning Utility

A dedicated utility function (`clean_email_input`) was implemented to mitigate ASR transcription errors:

* It automatically replaces common speech patterns ("dot," "at," "space") with their corresponding punctuation (`.`, `@`).
* **Smart Fallback:** It applies a fallback logic to construct a valid email (e.g., appending `@gmail.com` if a domain is missing, using the collected Name field for context).

### 2. Systematic Lead Collection

The `capture_lead_data` function ensures no field is missed by:
* Checking the `SDRSessionState` for missing fields.
* Generating a highly contextual, dedicated question for the next missing field in the queue.
* Storing data robustly, handling edge cases like email cleaning upon capture.
