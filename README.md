# Documentation for Woodxel and Lignum Chatbot API

This document provides comprehensive instructions for deploying, installing, and modifying the Woodxel and Lignum Chatbot API. The API is built using Flask and provides endpoints for interacting with two chatbot instances: `WoodxelChatbot` and `LignumChatbot`. The API is secured using JWT (JSON Web Tokens) for authentication.

---

## Table of Contents
1. [Installation](#installation)
2. [Deployment](#deployment)
3. [API Endpoints](#api-endpoints)
4. [Authentication](#authentication)
5. [Environment Variables](#environment-variables)
6. [Modifications](#modifications)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites
- Python 3.11 or higher
- `pip` (Python package manager)
- A `.env` file for environment variables (see [Environment Variables](#environment-variables))

### Steps
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set up a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Create environment**:
   ```bash
      python3 -m venv venv
      source venv/bin/activate    # For Linux/Mac
      # or
      venv\Scripts\activate       # For Windows
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   Create a `.env` file in the root directory and populate it with the required variables (see [Environment Variables](#environment-variables)).

5. **Run the application**:
   ```bash
   python app.py
   ```
   The API will be accessible at `http://0.0.0.0:5000`.

---

## Deployment

 `python app.py`


### Security Considerations
- Ensure the `JWT_SECRET_KEY` is securely generated and stored.
- Use HTTPS in production to secure data in transit.
- Regularly rotate the `JWT_SECRET_KEY` and admin credentials.

---

## API Endpoints

### 1. **Login Endpoint**
- **URL**: `/login`
- **Method**: `POST`
- **Description**: Authenticates the admin user and returns a JWT token.
- **Request Body**:
  ```json
  {
    "username": "admin_username",
    "password": "admin_password"
  }
  ```
- **Success Response**:
  ```json
  {
    "access_token": "<JWT_TOKEN>"
  }
  ```

### 2. **Woodxel Chatbot Endpoint**
- **URL**: `/woodxel_chatbot`
- **Method**: `POST`
- **Description**: Interacts with the Woodxel chatbot. Requires a valid JWT token.
- **Request Body**:
  ```json
  {
    "input": "User input text",
    "history": [
      ["Previous user message", "Bot response"],
      ["Another message", "Another response"]
    ]
  }
  ```
- **Success Response**:
  ```json
  {
    "response": "Chatbot response"
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "Internal server error: ..."
  }
  ```
  
### 3. **Lignum Chatbot Endpoint**
- **URL**: `/lignum_chatbot`
- **Method**: `POST`
- **Description**: Interacts with the Lignum chatbot. Requires a valid JWT token.
- **Request Body**:
  ```json
  {
    "input": "User input text",
    "history": [
      ["Previous user message", "Bot response"],
      ["Another message", "Another response"]
    ]
  }
  ```
- **Success Response**:
  ```json
  {
    "response": "Chatbot response"
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "Internal server error: ..."
  }
  ```

---

## Authentication

The API uses JWT for authentication. To access protected endpoints (`/woodxel_chatbot` and `/lignum_chatbot`), you must:
1. Obtain a JWT token by calling the `/login` endpoint with valid admin credentials.
2. Include the token in the `Authorization` header of subsequent requests:
   ```
   Authorization: Bearer <JWT_TOKEN>
   ```

---

## Environment Variables

The following environment variables must be set in a `.env` file:

| Variable Name         | Description                          |
|-----------------------|--------------------------------------|
| `PINECONE_API_KEY`    | Pinecone vector DB access key        |
| `GOOGLE_API_KEY`      | Google Generative AI API key         |
| `JWT_SECRET_KEY`      | Secret key for JWT token generation  | 
| `ADMIN_USER`          | Admin username for authentication    | 
| `ADMIN_PASSWORD`      | Admin password for authentication    | 

---

## Modifications

### 1. **Modifying Chatbot Behavior**
The `WoodxelChatbot` and `LignumChatbot` classes inherit from the `Chatbot` base class. You can modify the following parameters:
- **Model Name**: Change the `model_name` parameter in the `Chatbot` constructor to use a different Gemini LLM model.
- **Temperature**: Adjust the `temperature` parameter to control the randomness of the chatbot's responses.


### 2. **Customizing Error Handling**
Modify the `chat_with_history` method in the chatbot classes to customize error handling or retry logic.

---

## Troubleshooting

### Common Issues
1. **Invalid Credentials**:
   - Ensure the `ADMIN_USER` and `ADMIN_PASSWORD` environment variables are correctly set.
   - Verify that the password is hashed correctly during deployment.

2. **JWT Token Expiry**:
   - The default token expiry is 1 hour. Adjust `JWT_ACCESS_TOKEN_EXPIRES` in `app.py` if needed.

3. **LLM Invocation Errors**:
   - Check the logs for details on LLM invocation errors.
   - Ensure the model name and API keys (if applicable) are correct.

4. **Missing Environment Variables**:
   - Ensure all required environment variables are set in the `.env` file.

---

## Deployment

### Production Setup

streamlit run src/streamlit_app.py --server.port=5000 --server.headless=true


## Customization


