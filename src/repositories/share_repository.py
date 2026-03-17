from sqlalchemy import select

from src.models.db_models import ShareModel
from src.repositories.base import BaseRepository


class ShareRepository(BaseRepository):
    """Acesso à tabela de compartilhamentos."""

    def exists(self, owner_id: int, reader_id: int) -> bool:
        stmt = select(ShareModel).where(
            ShareModel.owner_id == owner_id,
            ShareModel.reader_id == reader_id,
        )
        return self.session.scalar(stmt) is not None

    def create(self, owner_id: int, reader_id: int) -> ShareModel:
        share = ShareModel(owner_id=owner_id, reader_id=reader_id)
        self.session.add(share)
        self.session.flush()
        return share

    def delete(self, owner_id: int, reader_id: int) -> None:
        stmt = select(ShareModel).where(
            ShareModel.owner_id == owner_id,
            ShareModel.reader_id == reader_id,
        )
        share = self.session.scalar(stmt)
        if share:
            self.session.delete(share)
            self.session.flush()

    def list_readers_for_owner(self, owner_id: int) -> list[ShareModel]:
        stmt = select(ShareModel).where(ShareModel.owner_id == owner_id)
        return list(self.session.scalars(stmt))

    def list_owners_for_reader(self, reader_id: int) -> list[ShareModel]:
        stmt = select(ShareModel).where(ShareModel.reader_id == reader_id)
        return list(self.session.scalars(stmt))
