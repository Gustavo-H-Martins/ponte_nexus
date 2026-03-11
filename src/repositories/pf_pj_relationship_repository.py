from sqlalchemy import select

from src.models.db_models import PfPjRelationshipModel
from src.repositories.base import BaseRepository


class PfPjRelationshipRepository(BaseRepository):
    def exists(self, pf_entity_id: int, pj_entity_id: int) -> bool:
        stmt = select(PfPjRelationshipModel).where(
            PfPjRelationshipModel.pf_entity_id == pf_entity_id,
            PfPjRelationshipModel.pj_entity_id == pj_entity_id,
        )
        return self.session.scalar(stmt) is not None

    def ensure(self, pf_entity_id: int, pj_entity_id: int) -> PfPjRelationshipModel:
        stmt = select(PfPjRelationshipModel).where(
            PfPjRelationshipModel.pf_entity_id == pf_entity_id,
            PfPjRelationshipModel.pj_entity_id == pj_entity_id,
        )
        existing = self.session.scalar(stmt)
        if existing:
            return existing
        rel = PfPjRelationshipModel(pf_entity_id=pf_entity_id, pj_entity_id=pj_entity_id)
        self.session.add(rel)
        return rel
