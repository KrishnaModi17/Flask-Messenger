Flask Messenger

Flask Messenger is a real-time messaging web application developed using Flask, WebSocket, and a database like SQLite or PostgreSQL. This application allows users to register, log in, and send messages to each other in real-time.

Key Features

User Registration and Authentication:- Users can register with their email and password.
Real-Time Messaging: Implement real-time messaging using Flask-SocketIO to allow users to send and receive messages instantly.
Support for one-on-one conversations.
Display the status (online/offline) of users.
Message History: Store and display message history for users so they can view previous conversations.
Friend Requests: Allow users to send and accept friend requests. Users should be able to manage their contacts.
Group Chats: Implement the option to create group chats where multiple users can chat together.
Responsive Design: Ensure that the web application is responsive and works well on both desktop and mobile devices.

Additional (Stretch Goals):
Enable users to customize their chat themes.
Implement a search functionality for finding and adding friends.

Installation
Clone or download the repository.
Install the required dependencies using the command pip install -r requirements.txt.
Run the application using the command python app.py.
Usage
Navigate to the URL provided by the application (typically http://localhost:5000).
Register a new account or log in with an existing account.
Use the application to send and receive messages, manage friends, and create group chats.