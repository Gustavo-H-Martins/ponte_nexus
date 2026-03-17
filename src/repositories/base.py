from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, session: Session, owner_id: int | None = None) -> None:
        self.session = session
        self.owner_id = owner_id

    def _owner_filter(self, stmt, model_cls):
        """Adiciona filtro por owner_id ao statement quando definido."""
        if self.owner_id is not None:
            return stmt.where(model_cls.owner_id == self.owner_id)
        return stmt
