# LINE Voice Summary Bot

A voice summarization chatbot that leverages OpenAI's Whisper for speech-to-text conversion and ChatGPT for summarization, integrated with LINE's messaging API. This bot allows users to send audio files through LINE and receive both the transcribed text and a concise summary in response.

## Features

- **Voice Transcription**: Converts audio files into text using Whisper.
- **Text Summarization**: Summarizes the transcribed text into key points using ChatGPT.
- **LINE Bot Integration**: Receives audio files and sends back summaries via LINE messaging.
- **Handles Large Files**: Automatically splits large audio files into smaller segments to comply with Whisper's file size limitations.
- **Deployable on Render**: Uses `render.yaml` for straightforward deployment on Render.

## Project Structure

- **`app.py`**: The main Flask application handling LINE webhook events, Whisper transcriptions, and ChatGPT summarizations.
- **`requirements.txt`**: Lists the dependencies needed to run the app.
- **`render.yaml`**: Render deployment configuration file for building and running the application.
