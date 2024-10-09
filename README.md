# EosBot
EosBot is a discord bot / agent designed to facilitate unique and stimulating conversations. 

Write python code based on this pseudocode, splitting by modules 
Updated Pseudocode for EosBot with Chat Saving Functionality

Import Necessary Modules:

	•	Import environment variable loader
	•	Import OS, time, and threading utilities
	•	Import Discord libraries for bot functionality
	•	Import OpenAI API wrapper (updated to use OpenRouter API)
	•	Import logging utilities for debugging and information tracking
	•	Import asyncio for asynchronous operations
	•	Import datetime and pytz for timezone management
	•	Import random and re for randomization and regular expressions
	•	Import sqlite3 and shutil for database management
	•	Import json module for JSON handling

Load Environment Variables:

	1.	Load environment variables from a .env file.
	2.	Try to retrieve the following environment variables:
	•	DISCORD_TOKEN
	•	OPENROUTER_API_KEY
	3.	If any are missing, log an error and exit the program.

Set Up Logging:

	1.	Create a logs directory if it doesn’t exist.
	2.	Initialize a logger named 'eos_bot' with a debug level.
	3.	Configure file handler (RotatingFileHandler) to write logs to 'logs/eos_bot.log', rotating after 5 MB, and keeping up to 5 backup files.
	4.	Configure console handler (StreamHandler) to output logs with an info level.
	5.	Set formatters for both handlers and add them to the logger.

Define Custom Discord Bot Class (EosBot):

	•	Initialize Bot:
	1.	Call the parent class initializer with command prefix 'e!' and intents.
	2.	Initialize instance variables:
	•	conversation_histories as an empty dictionary.
	•	trigger_words with specific keywords to trigger the bot (e.g., "eos", "e!", "eosbot#XXXX").
	•	MAX_HISTORY_LENGTH set to 50.
	•	start_time to track bot uptime.
	•	recent_messages to keep track of recent user messages.
	•	temperature for controlling response randomness.
	•	probabilities to store reply and reaction probabilities per guild/channel.
	•	jsonl_lock as a threading lock for JSONL file access.
	3.	Initialize a thread lock (db_lock) for database operations.
	4.	Set database_file to 'user_preferences.db'.
	5.	Call init_database() to set up the database.
	6.	Initialize OpenRouter API client using the OPENROUTER_API_KEY.
	7.	Define emotional_reactions as a mapping of emotions to emoji lists.
	•	Asynchronous Setup Hook:
	1.	Create background tasks for updating presence and cleaning up conversation histories.
	2.	Add the EosCog cog to the bot.
	•	Database Methods:
	•	Initialize Database (init_database):
	•	Acquire db_lock to ensure thread safety.
	•	Connect to the SQLite database.
	•	Create tables for user_preferences and probabilities if they don’t exist.
	•	Commit changes and close the connection.
	•	Log that the database has been initialized.
	•	Load and Save User Preferences and Probabilities:
	•	Similar to the previous implementation, with methods to load and save user preferences and probabilities, ensuring thread safety with db_lock.
	•	Helper Functions:
	•	Trigger Word Detection (contains_trigger_word):
	•	Check if the message content contains any of the specified trigger words.
	•	Bot Mention Detection (is_bot_mentioned):
	•	Check if the bot is mentioned in the message.
	•	Random Chance Calculation (random_chance):
	•	Return true if a random number is less than the given probability.
	•	Username Replacement with Mentions (replace_usernames_with_mentions):
	•	Replace occurrences of usernames in the content with their Discord mentions.
	•	Ping Placeholder Replacement (replace_ping_with_mention):
	•	Replace occurrences of *ping* with the user’s mention.
	•	Name Exclamation Replacement (replace_name_exclamation_with_mention):
	•	Replace exclamations of the user’s name with their mention.
	•	Generate System Prompt (get_system_prompt):
	•	Use the provided Eos prompt as the system prompt for the bot.
	•	Incorporate the user’s display name, server name, channel name, and current time into the prompt.
	•	Refusal Detection (is_refusal):
	•	Check if the response content contains phrases indicating a refusal to comply.
	•	Prefix Validation (is_valid_prefix):
	•	Validate that the message prefix is acceptable (e.g., not too long).
	•	Generate Reaction System Prompt (get_reaction_system_prompt):
	•	Create a system prompt specifically for generating emoji reactions.
	•	Get Reaction Response (get_reaction_response):
	•	Asynchronously generate an appropriate emoji reaction based on the user’s message.
	•	Use the OpenRouter API and the specified language model.
	•	Get Valid Response (get_valid_response):
	•	Asynchronously generate a valid response to the user’s message.
	•	Use the OpenRouter API with the Cohere Command model (command-light-nightly).
	•	Retry with adjusted parameters if necessary.
	•	Save Conversation to JSONL (save_conversation_to_jsonl):
	•	Purpose:
	•	Save conversation data to a JSONL file for OpenPipe training.
	•	Method:
	1.	Acquire jsonl_lock to ensure thread safety.
	2.	Prepare the conversation data:
	•	Extract messages from the conversation history.
	•	Format messages according to OpenPipe’s required fields.
	•	Exclude any personal or sensitive information.
	3.	Define the file path based on guild_id and channel_id, e.g., 'conversations/{guild_id}_{channel_id}.jsonl'.
	4.	Open the JSONL file in append mode.
	5.	Write each message as a JSON object per line.
	6.	Close the file and release the lock.
	•	Considerations:
	•	Validate the JSON structure before writing.
	•	Handle any exceptions during file operations.
	•	Ensure that the data complies with OpenPipe’s training format.
	•	Background Tasks:
	•	Cleanup Conversation Histories (cleanup_conversation_histories):
	•	Periodically remove conversation histories that have been inactive for over 24 hours.
	•	Update Presence (update_presence):
	•	Periodically update the bot’s Discord presence with various statuses.

Instantiate the Bot:

	•	Create an instance of EosBot with the command prefix 'e!' and the necessary intents for messages, guilds, DMs, and members.

Define EosCog Class:

	•	Initialize Cog:
	•	Set self.bot to the bot instance.
	•	On Ready Event (on_ready):
	•	Log that the bot has connected to Discord.
	•	On Message Event (on_message):
	•	Initial Checks:
	•	Ignore messages sent by the bot itself.
	•	Process commands if the message is a command.
	•	Log the received message content.
	•	Context Setup:
	•	Determine if the message is a DM.
	•	Get guild_id and channel_id.
	•	Load reply and reaction probabilities for the current guild and channel.
	•	Initialize conversation history if not present.
	•	Role and Content Preparation:
	•	Determine the role ('assistant' or 'user') based on the message author.
	•	If the role is 'user', prepend the author’s display name to the content.
	•	User Preference Handling:
	•	Check if the user provided instructions to start messages with a specific prefix.
	•	If valid, save the user’s message prefix preference.
	•	Update Conversation History:
	•	Append the message to the conversation history with a timestamp.
	•	Ensure the conversation history does not exceed MAX_HISTORY_LENGTH.
	•	Recent Messages Tracking:
	•	Track recent messages in the channel for potential bot reply suppression.
	•	Remove messages older than 5 seconds from the tracking list.
	•	Determine if Bot Should Respond:
	•	Set should_respond based on:
	•	Whether the bot is mentioned.
	•	Presence of trigger words.
	•	If the message is a DM.
	•	Random chance based on reply probability.
	•	Bot Response Handling:
	•	If should_respond is true:
	•	Prepare Response:
	•	Build the system prompt using the Eos prompt.
	•	Create messages for context, including the conversation history.
	•	Define tags for logging and tracking.
	•	Generate and Send Response:
	•	Use a typing indicator while processing.
	•	Asynchronously get a valid response using get_valid_response.
	•	Process the response to handle custom names, user mentions, and content length.
	•	Reply to the user without mentioning them.
	•	Update conversation history with the assistant’s response.
	•	Save Conversation:
	•	Call save_conversation_to_jsonl() to save the conversation to a JSONL file.
	•	Backup Database:
	•	Create a backup of the database after responding.
	•	Reaction Handling:
	•	If the role is 'user' and random chance allows:
	•	Prepare Reaction:
	•	Build the system prompt for reactions.
	•	Create messages containing the user’s message.
	•	Generate and Add Reaction:
	•	Use a typing indicator while processing.
	•	Asynchronously get an emoji reaction.
	•	Add the reaction to the user’s message.
	•	Help Command (eos_help):
	•	Create an embedded message containing help information for all available commands.
	•	Send the embedded help message to the user.
	•	Ping User Command (ping_user):
	•	Ping a specified user by mentioning them in a message.
	•	Set Temperature Command (set_temperature):
	•	Allow users to set the bot’s response temperature within the range [0, 1].
	•	Set Reply Probability Command (set_reply_probability):
	•	Allow users to set the bot’s reply probability for the current channel.
	•	Set Reaction Probability Command (set_reaction_probability):
	•	Allow users to set the bot’s reaction probability for the current channel.
	•	Command Error Handler (on_command_error):
	•	Handle common command errors and provide appropriate feedback to the user.
	•	Global Exception Handler (on_error):
	•	Log any unhandled exceptions that occur within the bot.

Run the Bot:

	•	At the end of the script, check if the script is being run directly.
	•	Attempt to run the bot using DISCORD_TOKEN.
	•	If an exception occurs during startup, log a critical error and exit the program.

Additional Functionality: Saving Chats in JSONL Format

	•	Purpose:
	•	Save each conversation by channel and guild into JSONL files following the OpenPipe training format.
	•	Facilitate the training of language models by providing formatted conversation data.
	•	Implementation Details:
	•	Directory Structure:
	•	Create a conversations directory if it doesn’t exist.
	•	Use filenames like {guild_id}_{channel_id}.jsonl to store conversations per channel.
	•	Data Formatting:
	•	For each conversation, structure the data according to OpenPipe’s requirements.
	•	Fields to Include:
	•	role: Specifies if the message is from the user or assistant.
	•	content: The message content.
	•	timestamp: The time the message was sent.
	•	Exclude Personal Information:
	•	Do not include user IDs, real names, or any sensitive data.
	•	Use display names or anonymize if necessary.
	•	Writing to JSONL:
	•	Open the JSONL file in append mode.
	•	For each message, convert the data to JSON format and write it as a line in the file.
	•	Ensure that each line is a valid JSON object.
	•	Error Handling:
	•	Validate JSON before writing.
	•	Catch and log any exceptions during file operations.

Notes and Changes:

	•	Command Prefix Updated:
	•	Changed the command prefix from 's!' to 'e!' to reflect the new bot name.
	•	API Updated to OpenRouter:
	•	Replaced OpenAI API client with OpenRouter API client.
	•	Updated API calls to use OpenRouter’s endpoints.
	•	Language Model Changed:
	•	Updated to use the Cohere Command model (command-light-nightly).
	•	System Prompt Updated:
	•	Replaced the previous system prompt with the provided Eos prompt.
	•	Ensured that the prompt is incorporated into the bot’s responses appropriately.
	•	Trigger Words Updated:
	•	Updated trigger_words to include keywords relevant to Eos, such as "eos", "e!", and the bot’s Discord tag.
	•	Logging Updated:
	•	Logger name changed to 'eos_bot'.
	•	Log file updated to 'logs/eos_bot.log'.
	•	Helper Functions Adjusted:
	•	Ensured that all helper functions accommodate the changes in bot behavior and persona.
	•	Chat Saving Functionality Added:
	•	Implemented methods to save conversations to JSONL files per channel and guild.
	•	Ensured compliance with OpenPipe training format.
	•	Added necessary threading locks for file operations.
	•	Policy Compliance:
	•	Reviewed the Eos prompt to ensure it complies with content policies.
	•	Avoided any disallowed content, ensuring the bot’s responses are appropriate.
	•	Ensured that no personal or sensitive information is included in the saved data.

Summary:

	•	The bot is now named EosBot and responds to the command prefix 'e!'.
	•	It uses the OpenRouter API with the Cohere Command model to generate responses.
	•	The bot embodies the personality and behavior described in the provided Eos prompt.
	•	Conversations are saved per channel and guild into JSONL files following the OpenPipe training format.
	•	All functionalities, such as conversation management, reactions, and commands, have been updated to reflect these changes.
	•	The code structure remains similar, with adjustments made to incorporate the new requirements and the additional chat saving functionality.
