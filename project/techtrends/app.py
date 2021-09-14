import sqlite3
import logging
import sys

from flask import Flask, json, render_template, request, url_for, redirect, flash



# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    app.config['connection_counter'] += 1
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'archangel'
# Count database connections
app.config['connection_counter'] = 0


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    logger = logging.getLogger("logger")
    post = get_post(post_id)
    if post is None:
        logger.info("The article was not found on this server!")
        return render_template('404.html'), 404
    else:
        logger.info("The article with title '{}' has been retrieved!".format(post['title']))
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    logger = logging.getLogger("logger")
    logger.info("About Us page retrieved!")
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    logger = logging.getLogger("logger")
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            logger.info("A new article with title '{}' has been created.".format(title))
            return redirect(url_for('index'))

    return render_template('create.html')


# Define a function to return all posts
def get_posts():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    app.config['connection_counter'] += 1
    connection.close()
    return posts


# Define the /healthz endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result": "OK - Healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response


# Define the /metrics endpoint
@app.route('/metrics')
def metrics():
    post_count = len(get_posts())
    response = app.response_class(
        status=200,
        response=json.dumps({"db_connection_count": app.config['connection_counter'], "post_count": post_count}),
        mimetype='application/json'
    )

    return response


# start the application on port 3111
if __name__ == "__main__":
    # Configure logger with handlers
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(levelname)s: [%(asctime)s] %(message)s")
    stderr_handler.setFormatter(formatter)
    stdout_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s: [%(asctime)s] %(message)s"
    )

    logger = logging.getLogger("logger")
    logger.addHandler(stderr_handler)
    logger.addHandler(stdout_handler)

    app.run(host='0.0.0.0', port=3111)
