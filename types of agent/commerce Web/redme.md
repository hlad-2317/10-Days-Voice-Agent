
# 🛒 Day 9: E-commerce Voice Agent - Diablo

## Project Overview
This project successfully implements a **Voice-Driven Shopping Assistant**, named **Aryan**, for Day 9 of the Murf AI Voice Agent Challenge. The agent is built following a structured architecture inspired by the **Agentic Commerce Protocol (ACP)** principles, separating the conversational AI from the core commerce logic (catalog and orders).

The core function is to allow users to browse products, collect multiple items, and place a final, consolidated order entirely via voice interaction.

## ✨ Advanced Implementation: Multi-Item Cart & Checkout (Advanced Goal 3)

While the base requirement was simple order placement, this solution was refactored to incorporate a full multi-step e-commerce flow, resolving the real-world issue of handling complex, multi-item purchases.

| Feature | Description | Technical Implementation |
| :--- | :--- | :--- |
| **Product Browsing** | Users can search the internal product catalog (`PRODUCTS`) using natural language filters (category, price, color). | `list_products` tool with enhanced category mapping (`_map_category_alias`) to handle conversational synonyms (e.g., "electronics" -> "tech"). |
| **Multi-Item Cart** | The agent maintains a global, in-memory `CART` for the session, enabling users to add items continuously. | `add_item_to_cart` tool. This function appends to the cart state but **does not** finalize the order. |
| **Consolidated Checkout** | Only when the user confirms ("checkout," "place order," etc.) does the system process the purchase. | `checkout_cart` tool. This function calculates the total, moves all line items from `CART` to `ORDERS`, and clears the cart. |
| **JSON Order Proof** | Crucial for persistence and challenge verification. | The `_finalize_order_logic` function generates a single JSON object containing **all line items** and logs it to the console using `logger.info()`. |

## 🛠️ Technical Architecture

The architecture rigorously separates the AI layer from the commerce layer:

1.  **AI Layer (The Agent):** The `Assistant` class handles user input, determines intent, and selects the appropriate tool call (`list_products`, `add_item_to_cart`, `checkout_cart`).
2.  **Commerce Layer (The Backend):** Dedicated Python functions (`_list_products_logic`, `_finalize_order_logic`) manage the actual product data (`PRODUCTS`), session cart (`CART`), and order history (`ORDERS`), ensuring clean, testable business logic.

## 🗣️ Demo Flow (How to Test Multi-Item Checkout)

To test the multi-item flow and demonstrate the final JSON output, follow this conversational sequence:

1.  **Browse:** "Hello Diablo, show me your **tech** items."
2.  **Add Item 1:** "I want to add **one Play Station 5** to my cart." (Agent confirms PS5 is added and prompts for next step/checkout).
3.  **Add Item 2:** "I'll also add an **Agent Challenge Hoodie**, size **Large**." (Agent confirms Hoodie is added).
4.  **Checkout:** "**Place order for both.**" (Agent finalizes the single, consolidated order).
5.  **Verify JSON:** The **terminal console immediately prints the full JSON log** showing a single order ID containing both the PS5 and the Hoodie as line items.

## 💻 Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Voice/TTS** | **Murf AI Falcon** | Provides the fastest, most natural real-time voice delivery. |
| **AI Brain/LLM** | Google Gemini 2.5 Flash | Handles intent recognition and tool selection. |
| **Voice Platform** | LiveKit Agents SDK | Manages the full voice pipeline (STT, VAD, LLM, TTS). |
| **Backend/Logic** | Python & Function Tools | Implements catalog/cart/order management. |
