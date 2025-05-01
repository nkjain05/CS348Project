from api.app import app, db, User, Company, Status

with app.app_context():
    db.create_all()

    if not User.query.first():
        db.session.add_all([
            User(name='Alice Johnson', email='alice@example.com', major='CS'),
            User(name='Bob Smith', email='bob@example.com', major='Data Science'),
        ])

        db.session.add_all([
            Company(name='Google', industry='Tech', size='Large', headquarters='Mountain View'),
            Company(name='Dropbox', industry='Tech', size='Medium', headquarters='San Francisco'),
        ])

        db.session.add_all([
            Status(status_name='Applied'),
            Status(status_name='Interviewed'),
            Status(status_name='Rejected'),
            Status(status_name='Offer'),
        ])

        db.session.commit()
        print("✅ Dummy data inserted.")
