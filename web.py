import re
from flask import render_template, request, redirect
from db_tables import BlogPost, User, Like, db, app


@app.route('/')
def index():
    """
    :return: redirect to Guest main page
    """
    return redirect('/posts/newsfeed/0')


@app.route('/posts/newsfeed/<int:user_id>')
def posts(user_id):
    """
    News feed page for user.
    :param user_id: user id number on User DB
    :return: redirect to newsfeed
    """
    # In case it post we want to update db
    all_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
    user = User.query.get(user_id)
    user_id_likes = []

    if User is not None:
        for post in BlogPost.query.all():
            for filtered_like in Like.query.filter_by(user_id=user_id):
                if filtered_like is not None and filtered_like.post_id == post.id:
                    user_id_likes.append(post.id)

    return render_template('posts.html', posts=all_posts, user=user, type=0, user_id_likes=user_id_likes)


@app.route('/posts/profile/<int:user_id>')
def my_profile(user_id):
    """
    Showing the posts of a specific user
    :param user_id: user id number on User DB
    :return: my profile page
    """
    user = User.query.get(user_id)
    return render_template('posts.html', posts=user.posts, user=user, type=1)


@app.route('/posts/like/<int:post_id>/<int:user_id>')
def like(post_id, user_id):
    """

    :param post_id: post_id which user clicked like on
    :param user_id: user_id of the user which clicked on the like button
    :return: redirect to newsfeed
    """
    if user_id == 0:
        return redirect('/signup'.format(user_id))

    user_id = user_id
    post_id = post_id
    new_like = Like(user_id=user_id, post_id=post_id)
    like_already_exist = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

    if like_already_exist is None:
        db.session.add(new_like)

    else:
        db.session.delete(Like.query.get(like_already_exist.id))
    db.session.commit()
    return redirect('/posts/newsfeed/{}'.format(user_id))


@app.route('/posts/delete/<int:post_id>/<int:user_id>')
def delete(post_id, user_id):
    """
    Delete post
    :param post_id: post_id which user clicked delete on
    :param user_id: user_id of the user which clicked on the delete button
    :return: redirect newsfeed
    """
    post = BlogPost.query.get_or_404(post_id)

    for like in Like.query.filter(Like.post_id == post.id).all():
        db.session.delete(like)
    # db.session.delete(Like.query.filter(Like.post_id==post.id).all())
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts/newsfeed/{}'.format(user_id))


# POST required for editing
@app.route('/posts/edit/<int:post_id>/<int:user_id>', methods=['GET', 'POST'])
def edit(post_id, user_id):
    """
    Editing an existing post.
    :param post_id: post_id of the post which is edited
    :param user_id: user_id of the user which clicked edit
    :return: redirect to newsfeed
    """
    post = BlogPost.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/posts/newsfeed/{}'.format(user_id))
    else:
        return render_template('edit.html', post=post, user=User.query.get(user_id))


@app.route('/posts/new/<int:user_id>', methods=['GET', 'POST'])
def post_new_blog(user_id):
    """
    Creating new post for specific user
    :param user_id: The user_id of the user who creates new post
    :return: redirect to newsfeed
    """
    if user_id == 0:
        return redirect('/signup')
    user = User.query.get(user_id)
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_user_id = user_id
        new_post = BlogPost(title=post_title, content=post_content, user_id=post_user_id)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts/newsfeed/{}'.format(user_id))
    # GET - just getting data from website
    else:
        return render_template('new_post.html', user=user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Registering as a new user and entering the details into the database
    :return: In case user details are valid - newsfeed else - Signup page again.
    """
    if request.method == 'POST':
        user_fname = request.form['fname']
        user_lname = request.form['lname']
        user_password = request.form['password']

        user_date_birth = request.form['birth_date']
        user_email = request.form['email']
        user_gender = request.form['gender']
        new_user = User(fname=user_fname, lname=user_lname, password=user_password, date_birth=user_date_birth,
                        email=user_email, gender=user_gender)

        user_check = fields_check(new_user)
        print(user_check)
        if not all(user_check.values()):
            return render_template('signup.html', user_check=user_check)

        db.session.add(new_user)
        db.session.commit()
        return redirect('/posts/newsfeed/{}'.format(get_user_id(user_email)))
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login to account of an existing user.
    :return: If details match db user - newsfeed else - Login page again.
    """
    if request.method == 'POST':
        user_password = request.form['password']
        user_email = request.form['email']
        user = User.query.filter_by(email=user_email, password=user_password).first()
        if user is None:
            return render_template('login.html', is_wrong_password=True)
        else:
            return redirect('/posts/newsfeed/{}'.format(user.id))

    else:
        return render_template('login.html')


def get_user_id(user_email):
    """
    Get user_id by email address
    :param user_email: email address
    :return: user_id which matches the given email
    """
    return User.query.filter_by(email=user_email).all()[0].id


def fields_check(user):
    """
    Performs standard checks on the correctness of User's fields :param user: :return: dict which consists of keys :
    ['fname', 'lname', 'password', 'email']. value of each key is true iff field is valid.
    """
    check = dict.fromkeys(['fname', 'lname', 'password', 'email'], False)
    if 2 <= len(user.fname) <= 10 and user.fname.isalpha():
        check['fname'] = True
    if 2 <= len(user.lname) <= 20 and user.lname.isalpha():
        check['lname'] = True

    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)
    check['password'] = bool(re.search(pat, user.password))

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, user.email):
        if User.query.filter_by(email=user.email).first() is None:
            check['email'] = True

    return check


if __name__ == "__main__":
    app.run(debug=True)
