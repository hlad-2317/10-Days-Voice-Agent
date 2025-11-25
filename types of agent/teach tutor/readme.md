
# 🤖 Day 4: Teach-the-Tutor: Active Recall Coach

This repository contains the solution for Day 4 of the **Murf AI Voice Agent Challenge**.

The goal was to transform the base voice agent into an **Active Recall Coach** that guides a user through learning concepts using a "Teach-the-Tutor" methodology. The agent utilizes three distinct learning modes and changes its voice (persona) based on the current mode, providing dynamic context to the user.

## ✨ Core Features

The agent supports seamless switching between the three required modes and uses specified Murf Falcon voices for immediate persona changes:

| Mode | Purpose | Murf Falcon Voice | Role/Persona |
| :--- | :--- | :--- | :--- |
| `learn` | Explains a concept summary. | **Matthew** | The Teacher |
| `quiz` | Asks a question to test recall. | **Alicia** | The Quizmaster |
| `teach_back` | Asks the user to explain the concept. | **Ken** | The Tutor |

## 🛠️ Implementation Details

All required changes were confined to the `backend/src/agent.py` file.

### 1. Hardcoded Course Content

Instead of an external JSON file, the course content was hardcoded into a global list of dictionaries named `COURSE_CONTENT` within `agent.py`. This includes the original concepts plus the additional topics requested:

* `variables`
* `loops`
* `function`
* `if_else`
* `data_types`
* `operators`
* `oop`

### 2. The `set_learning_mode` Tool

A `@function_tool` named `set_learning_mode` was implemented to manage the state of the learning session.

* It dynamically calls `context.agent_session.tts.update_options(voice=voice_id)` to switch the Murf voice *before* the LLM's response is generated.
* It includes robust logic to normalize the `concept` argument (e.g., handling "functions" as "function") to prevent the agent from defaulting to the wrong topic.
* It constructs the response text (`summary` or `sample_question`) based on the selected mode and concept.

### 3. Agent Instructions

The `Tutor` agent's instructions were updated to ensure it always calls the `set_learning_mode` tool when a mode or concept change is requested, making the tool the single source of truth for the session state and voice setting.

