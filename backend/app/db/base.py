# Import all models here for Alembic/init_db
from app.db.base_class import Base  # noqa
# Import models once they are moved
# from app.models.user import User  # noqa
# from app.models.document import Document  # noqa
# from app.models.module import Module  # noqa
# from app.models.quiz import Quiz  # noqa
# from app.models.output import Output  # noqa
from app.models.user_preferences import UserPreferences  # noqa
