# Technical Documentation

## **Project Title:** Add Login and Signup Functionality to Intelligent Document Finder Project

### Requirements:

1) Signup and Login (JWT Authentication) 
Enhance the existing Intelligent Document Finder project by adding user signup and login functionality using FastAPI.
    - Develop API endpoint for user signup, allowing new users to create an account.
    - Implement password hashing to securely store user passwords.
    - Create API endpoint for user login, verifying user credentials.
     - Generate and return JWT tokens upon successful login.
     - Test the API endpoints using tools like Swagger UI or Postman to ensure correct behaviour. 

2) User-Defined Search Folder:
    - Allow users to add a folder link from their Google Drive.
    - Limit search functionality to only the specified folder.
    - Implement search functionality restricted to the user's specified Drive folder.

3) Bonus Task - OneDrive Integration:
     - Extend the functionality of the project to support OneDrive.


### Approaches/Solutions:

1) Signup and Login (JWT Authentication)

    - Task 1: Building the Login and SignUp API endpoints using FastAPI by using JWT Authentication
        - Explore JWT Authentication
        - Explore JWT Token
        - Implement the JWT Authentication System using FastAPI
        - Create the API Endpoints for Login and SignUp:
            - SignUp
                - **Method**: `POST`
                - **URL**: `/register`
                - **Parameters**: `user: schemas.UserCreate` for sending the user details and `session: Session = Depends(get_session)` for sending the database session
                - Output: For successful registration of users -  `user created successfully` is returned. Along with it Access Token is generated.  If email id already exists then `Email already registered` is returned.
                - Description: Takes up user details and database session as input and stores the details to the database, generates the access token and provides an output if the user is registered.
            - Login
                - **Method**: `POST`
                - **URL**: `/login`
                - **Parameters**: `request: schemas.Logindetails` for sending the user login details as email id and password and `db: Session = Depends(get_session)` for connecting to the database session
                - **Output**: For successful login of users -  Login Successful is returned. If email id already exists then exception Incorrect mail id or incorrect password exception is raised
                - **Description**: Takes up user login details and database session as input and stores the details to the database and provides login successful message

        - Creating the Pydantic models and Schema for Login and SignUp System

        **Progress of Task 1 = 90%**

    - Task 2: Building the frontend and storing the user data in Database
        - Store the SignUp information in the postgresql database
        - Database Design:
            ![Database Design](/logos/loginsignup%20(1).png)
 
        - On successful login, the JWT Tokens will be generated and stored in postgresql database
        - Start implementing the frontend with Login and SignUp page
        - Connecting the frontend to the API endpoint for SignUp and Login

        **Progress of Task 2 - 60%**

2) User-Defined Search Folder:

    - Task 3: Adding user specific drive folder link
        - Implement an input parameter where the user will provide the link of their google drive folder which contains the files.
        - After this event, the files will be loaded from the Google Drive


    - Task 4: Integrating and Testing the Authentication System with the Updated Intelligent Document Finder App
        - Connect the Authentication System with the Intelligent Document Finder App and the user should be logged in even if we refresh the page.
        - Test the application after the interaction.


3) Bonus Task - OneDrive Integration:

	- Task 5: Implement the OneDrive Access
        - Implement the Microsoft OneDrive Loader of Llama-Index along with the Google Drive Loder using a different link input parameter of Microsoft Onedrive folder to read the files and process in a similar way to that of Google Drive Loader and give an output of the query. 
