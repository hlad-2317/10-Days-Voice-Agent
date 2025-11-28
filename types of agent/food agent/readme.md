# 🛒 Arvi: Food & Grocery Ordering Voice Agent 🗣️

Arvi is an intelligent, voice-activated assistant designed for quick-commerce and grocery ordering platforms. It allows users to place complex orders, request ingredients for custom recipes (using simple core IDs like `paneer` and `onion`), manage a dynamic cart, and track their order status—all through natural speech.

This project successfully implements the **Primary Goal** and **Advanced Goals 1 (Mock Tracking) & 2 (Order History)** of the **Murf AI Voice Agent Challenge (Day 7)**.

---

## ✨ Features and Capabilities

### 🛍️ Core Ordering & Cart Management (MVP)
* **Intelligent Bundling:** Recognizes high-level recipe requests (e.g., `"dal makhani"`, `"fruit salad"`) and translates them into multiple items in the custom Indian Veg catalog via the `add_recipe_ingredients` tool.
* **Simple Item IDs:** The agent uses simple, core product names as IDs (e.g., `garlic`, `paneer`, `aloo_bhujia`) to ensure fast and accurate tool calling.
* **Dynamic Cart:** Supports adding, removing, and viewing cart contents with real-time price calculation (`add_to_cart`, `remove_from_cart`, `view_cart`).
* **Order Persistence:** Finalized orders are saved to `orders.json` via `place_order()`.

---

### 🚀 Advanced Features (Mock Tracking & History)
* **Mock Order Tracking:** Automatic status progression:  
  `received` → `being_prepared` → `out_for_delivery` → `delivered`
* **Order History:** Stored in `orders.json` and accessed via `track_orders()`.

---

## 🤖 Agent Persona & Tools

| Detail | Description |
|-------|-------------|
| **Agent Name** | **Arvi** 🌙 |
| **Greeting** | "Hi! Welcome to Arvi. I can help you order groceries. What do you need today?" |
| **LLM** | Google Gemini 2.5 Flash |
| **TTS** | Murf Falcon |

---

### 🧰 Available Tools

| Tool Name | Purpose |
|-----------|---------|
| `add_to_cart(item_name, quantity)` | Add an item using simple ID |
| `add_recipe_ingredients(recipe_name)` | Add all items for a recipe |
| `remove_from_cart(item_name, quantity)` | Remove or decrease quantity |
| `view_cart()` | Show cart + total price |
| `place_order()` | Save order + clear cart |
| `track_orders()` | View latest order status |

---

## ⚙️ Setup and Execution

### 📁 Project Structure

