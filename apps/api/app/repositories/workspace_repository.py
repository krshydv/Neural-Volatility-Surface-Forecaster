from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workspace import Workspace


class WorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_owner(self, owner_id: UUID) -> list[Workspace]:
        stmt = select(Workspace).where(Workspace.owner_id == owner_id).order_by(Workspace.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_for_owner(self, workspace_id: UUID, owner_id: UUID) -> Workspace | None:
        stmt = select(Workspace).where(
            Workspace.id == workspace_id, Workspace.owner_id == owner_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, owner_id: UUID, name: str, description: str | None) -> Workspace:
        workspace = Workspace(owner_id=owner_id, name=name, description=description, layout_state={})
        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def update(self, workspace: Workspace, **fields) -> Workspace:
        for key, value in fields.items():
            if value is not None:
                setattr(workspace, key, value)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def delete(self, workspace: Workspace) -> None:
        self.db.delete(workspace)
        self.db.commit()
