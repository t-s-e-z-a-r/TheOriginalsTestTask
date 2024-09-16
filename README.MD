# Task Management Application
This is a simple Task Management Application that allows users to manage tasks and assign executors. The application supports real-time task status updates and includes email notifications for task updates.

## Running the Application
To start the application, run the following command:

```
docker-compose up -d
```

After that, you can open your browser and navigate to `http://localhost/docs` to see all the available APIs.

## Email Setup
To enable email notifications for task status changes, make sure you update the following environment variables in the .env file:

SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"

Note: You must generate an App Password to use your Gmail account. You can follow [this tutorial](https://support.google.com/mail/answer/185833?hl=en) to create an App Password for your Gmail account.