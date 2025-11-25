📅 Day 3: Health & Wellness Voice Companion (Luna)

This repository update details the solution for Day 3 of the Murf AI Voice Agent Challenge. The goal was to transform the agent into a supportive, stateful Health & Wellness Companion that uses Function Calling to persist conversation data.

🌟 Primary Goal Achieved: Stateful Check-ins

The agent, named Luna, is now capable of conducting daily check-ins, using historical data to inform the conversation, and persisting the results to the file system via dedicated tools.

Key Features Implemented:

Grounded Persona: The agent maintains a supportive, non-diagnostic persona focused on mood, energy, and daily objectives.

Stateful Conversation: The agent retrieves a summary of the last check-in at the start of every session to ensure conversational context.

JSON Persistence (Function Calling): Two new Python tools were implemented to manage session history:

get_past_checkin_summary: Reads the wellness_log.json file on session start.

save_checkin_data: Writes the final session summary (mood, energy, objectives) to the JSON file once the check-in is confirmed by the user.

Low-Latency Performance: The entire pipeline leverages the ultra-fast Murf Falcon TTS and LiveKit for a seamless, real-time voice experience.

💾 Data Persistence Proof

The core requirement of Day 3 was to successfully log data. The agent now creates/updates wellness_log.json in the backend directory.




<img width="1121" height="659" alt="image" src="https://github.com/user-attachments/assets/a23fd3c4-1b0c-44c1-b8d3-a3f863522a78" />
