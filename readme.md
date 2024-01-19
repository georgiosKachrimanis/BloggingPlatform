# FlaskBloggingPlatform

This project is a blogging platform built with Flask, a micro web framework written in Python. It features user authentication, blog post creation, editing, deletion, and comments.

## Features

- User registration and login
- Admin-only access for creating, editing, and deleting blog posts
- Posting blog articles with titles, subtitles, images, and body text
- Commenting on blog posts for registered users
- Responsive design using Flask-Bootstrap

## Technologies

- **Flask**: A lightweight WSGI web application framework
- **Flask-Login**: For handling user authentication
- **Flask-WTF & Flask-CKEditor**: For form handling and rich text editing
- **Flask-SQLAlchemy**: For database interactions
- **Flask-Bootstrap5**: For styling and responsive design
- **Flask-Gravatar**: For user profile images

## Setup and Installation

1. **Clone the Repository**

   `git clone https://github.com/georgiosKachrimanis/FlaskBloggingPlatform`

2. **Create and Activate Virtual Environment**

   `python -m venv venv`
   `source venv/bin/activate`  # On Windows use `venv\Scripts\activate`

3. **Install Dependencies**

   `pip install -r requirements.txt`

4. **Set Environment Variables**

   `export FLASK_APP=main.py`
   `export FLASK_ENV=development`
   `export SECRET_KEY='YourSecretKey'`

5. **Initialize Database**

   `flask db upgrade`

6. **Run the Application**

   `flask run`

## Usage

After starting the server, navigate to `http://127.0.0.1:5000/` in your web browser to use the application.

## Contributing

Contributions to this project are welcome! If you have suggestions for improvements or encounter any issues, please feel free to open an issue or submit a pull request.

### Steps for Contributing:

1. **Fork the Repository**

   Start by forking the repository to your GitHub account.

2. **Clone the Forked Repository**

   Clone the forked repository to your local machine.

    `git clone https://github.com/georgiosKachrimanis/FlaskBloggingPlatform`

3. **Create a New Branch**

   Create a new branch for your feature or bug fix.

   `git checkout -b [branch-name]`

4. **Make Your Changes**

   Implement your changes or fixes in your branch and commit them.

5. **Push Changes to Your Fork**

   Push your changes to your forked repository.

   `git push origin [branch-name]` 

6. **Create a Pull Request**

   Go to the original repository on GitHub, and you'll see a prompt to create a pull request from your new branch.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

Special thanks to all contributors and maintainers of the Flask framework and its extensions.

---

For any additional information or queries, feel free to contact the repository maintainer.

Happy blogging!