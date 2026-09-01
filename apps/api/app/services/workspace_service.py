from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.workspace_repository import WorkspaceRepository


class WorkspaceNotFoundError(Exception):
    pass


class WorkspaceService:
    def __init__(self, db: Session) -> None:
        self.repo = WorkspaceRepository(db)

    def list_workspaces(self, user: User) -> list[Workspace]:
        return self.repo.list_for_owner(user.id)

    def create_workspace(self, user: User, name: str, description: str | None) -> Workspace:
        return self.repo.create(user.id, name, description)

    def get_workspace(self, user: User, workspace_id: UUID) -> Workspace:
        workspace = self.repo.get_for_owner(workspace_id, user.id)
        if workspace is None:
            raise WorkspaceNotFoundError("Workspace not found")
        return workspace

    def update_workspace(
        self,
        user: User,
        workspace_id: UUID,
        name: str | None,
        description: str | None,
        layout_state: dict | None,
    ) -> Workspace:
        workspace = self.get_workspace(user, workspace_id)
        return self.repo.update(
            workspace, name=name, description=description, layout_state=layout_state
        )

    def delete_workspace(self, user: User, workspace_id: UUID) -> None:
        workspace = self.get_workspace(user, workspace_id)
        self.repo.delete(workspace)
