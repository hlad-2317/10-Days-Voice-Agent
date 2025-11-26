# Day 6 – Fraud Alert Voice Agent

## 🌐 Overview

This project implements a **Fraud Alert Voice Agent** for a fictional bank, designed to contact customers about suspicious transactions, verify their identity, and determine if the transaction is legitimate or fraudulent. The agent is built to handle a single fraud case pulled from a database and update the case status based on the customer's response.

*This agent was built as part of the Murf AI Voice Agent Challenge.*

## ✨ Implementation Details

### Database Setup

To simulate real-world data, a database was created to store customer and transaction details.

* **Data Source:** An external **JSON file** was created to act as the sample database source.
* **Entries:** **20 distinct fraud case entries** have been added to the database for testing various scenarios (`confirmed_safe`, `confirmed_fraud`, and `verification_failed`).
* **Key Fields in Database Entries:**
    * `userName`
    * `securityIdentifier`
    * `cardEnding` (Masked card number, e.g., `**** 1234`)
    * `transactionAmount`
    * `merchantName`
    * `location`
    * `timestamp`
    * `securityQuestion` (for basic verification)
    * `currentStatus` (e.g., `pending_review`)

### Agent Persona

The voice agent is configured to act as a **Fraud Detection Representative** for a fictional bank.

* **Tone:** Calm, professional, and reassuring.
* **Safety:** The agent is explicitly instructed **not** to ask for sensitive information like full card numbers, PINs, or passwords. Verification relies only on non-sensitive, pre-stored data (like a security question).

## 🎯 Primary Goal (MVP) – Call Flow

The primary goal was to build a voice agent that executes a clear, minimal fraud verification sequence for a single suspicious transaction loaded from the database.

### Call Flow Sequence

1.  **Start & Introduction:** Greet the user and introduce itself as the bank's fraud department, explaining the purpose of the call.
2.  **Load Case:** Prompt the user for a username to load the corresponding fraud case from the database.
3.  **Basic Verification:** Ask a non-sensitive verification question (e.g., security question from the database).
    * *If verification fails, the agent politely ends the call.*
4.  **Transaction Details:** Read out the suspicious transaction details (merchant, amount, masked card, time, and location) from the loaded case.
5.  **Confirmation:** Ask the user if they made the transaction (Yes/No). [cite: uploaded:murf-ai/ten-days-of-voice