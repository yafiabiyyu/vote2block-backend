# from flask.cli import FlaskGroup
# from project import create_app

# app = create_app()


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
from project import factory
import project

if __name__ == '__main__':
    app = factory.create_app(celery=project.celery)
    app.run()