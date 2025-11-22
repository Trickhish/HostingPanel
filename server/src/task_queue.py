import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Callable, Any
from src.database import get_db
from src.models import Task, TaskType, TaskStatus, ActivityLog, ActivityType, ActivityLevel
import traceback


class TaskQueue:
    """Manages background task execution with SSE progress updates"""

    def __init__(self):
        self.running_tasks: Dict[int, asyncio.Task] = {}
        self.task_handlers: Dict[TaskType, Callable] = {}
        self.sse_clients: Dict[int, list] = {}  # user_id -> list of queues

    def register_handler(self, task_type: TaskType, handler: Callable):
        """Register a task handler function"""
        self.task_handlers[task_type] = handler

    async def enqueue_task(
        self,
        user_id: int,
        task_type: TaskType,
        title: str,
        description: str = None,
        website_id: int = None,
        input_data: dict = None
    ) -> Task:

        print(f"➕ New {task_type} task: {title}")

        with get_db() as db:
            task = Task(
                user_id=user_id,
                website_id=website_id,
                task_type=task_type,
                status=TaskStatus.PENDING,
                title=title,
                description=description,
                input_data=json.dumps(input_data) if input_data else None,
                progress=0,
                total_steps=1
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            task_id = task.id

        # Start processing the task in the background
        asyncio.create_task(self._process_task(task_id))

        return task

    async def _process_task(self, task_id: int):
        """Process a task in the background"""
        try:
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    return

                # Update task status to RUNNING
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()
                db.commit()

                # Broadcast task started
                await self._broadcast_task_update(task.user_id, task)

                # Get handler for this task type
                handler = self.task_handlers.get(task.task_type)
                if not handler:
                    raise Exception(f"No handler registered for task type: {task.task_type.value}")

                # Parse input data
                input_data = json.loads(task.input_data) if task.input_data else {}

                # Execute the handler
                result = await handler(task_id, input_data, self._update_progress)

                # Mark task as completed
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.progress = 100
                task.result_data = json.dumps(result) if result else None
                db.commit()

                # Broadcast task completed
                await self._broadcast_task_update(task.user_id, task)

                # Log activity
                activity = ActivityLog(
                    user_id=task.user_id,
                    website_id=task.website_id,
                    activity_type=ActivityType.WEBSITE_CREATE,  # Map based on task_type
                    level=ActivityLevel.INFO,
                    title=f"Task completed: {task.title}",
                    description=task.description
                )
                db.add(activity)
                db.commit()

        except Exception as e:
            # Mark task as failed
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.utcnow()
                    task.error_message = str(e)
                    db.commit()

                    # Broadcast task failed
                    await self._broadcast_task_update(task.user_id, task)

                    # Log error
                    activity = ActivityLog(
                        user_id=task.user_id,
                        website_id=task.website_id,
                        activity_type=ActivityType.WEBSITE_CREATE,
                        level=ActivityLevel.ERROR,
                        title=f"Task failed: {task.title}",
                        description=task.description,
                        error_message=str(e),
                        stack_trace=traceback.format_exc()
                    )
                    db.add(activity)
                    db.commit()

    async def _update_progress(self, task_id: int, progress: int, current_step: str = None):
        """Update task progress and broadcast to SSE clients"""
        with get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.progress = progress
                if current_step:
                    task.current_step = current_step
                db.commit()

                # Broadcast progress update
                await self._broadcast_task_update(task.user_id, task)

    async def _broadcast_task_update(self, user_id: int, task: Task):
        """Broadcast task update to all SSE clients for this user"""
        if user_id in self.sse_clients:
            task_data = task.to_dict()
            message = f"data: {json.dumps(task_data)}\n\n"

            # Send to all connected clients for this user
            for queue in self.sse_clients[user_id]:
                try:
                    await queue.put(message)
                except:
                    pass  # Client disconnected

    def add_sse_client(self, user_id: int, queue: asyncio.Queue):
        """Register an SSE client for a user"""
        if user_id not in self.sse_clients:
            self.sse_clients[user_id] = []
        self.sse_clients[user_id].append(queue)

    def remove_sse_client(self, user_id: int, queue: asyncio.Queue):
        """Remove an SSE client"""
        if user_id in self.sse_clients:
            try:
                self.sse_clients[user_id].remove(queue)
                if not self.sse_clients[user_id]:
                    del self.sse_clients[user_id]
            except ValueError:
                pass


# Global task queue instance
task_queue = TaskQueue()


# Example task handlers

async def create_website_task(task_id: int, data: dict, update_progress: Callable):
    """Task handler for website creation"""
    await update_progress(task_id, 10, "Validating website configuration")
    await asyncio.sleep(1)  # Simulate work

    await update_progress(task_id, 30, "Creating directory structure")
    await asyncio.sleep(1)

    await update_progress(task_id, 50, "Configuring web server")
    await asyncio.sleep(1)

    await update_progress(task_id, 70, "Setting up SSL certificate")
    await asyncio.sleep(1)

    await update_progress(task_id, 90, "Finalizing configuration")
    await asyncio.sleep(1)

    # Update website status in database
    with get_db() as db:
        from src.models import Website, WebsiteStatus
        website = db.query(Website).filter(Website.id == data.get('website_id')).first()
        if website:
            website.status = WebsiteStatus.ACTIVE
            db.commit()

    return {"success": True, "message": "Website created successfully"}


async def create_backup_task(task_id: int, data: dict, update_progress: Callable):
    """Task handler for backup creation"""
    await update_progress(task_id, 10, "Preparing backup")
    await asyncio.sleep(1)

    await update_progress(task_id, 30, "Backing up files")
    await asyncio.sleep(2)

    await update_progress(task_id, 60, "Backing up database")
    await asyncio.sleep(2)

    await update_progress(task_id, 80, "Compressing backup")
    await asyncio.sleep(1)

    await update_progress(task_id, 95, "Storing backup")
    await asyncio.sleep(1)

    return {"success": True, "message": "Backup created successfully"}


async def install_ssl_task(task_id: int, data: dict, update_progress: Callable):
    """Task handler for SSL installation"""
    await update_progress(task_id, 20, "Verifying domain ownership")
    await asyncio.sleep(1)

    await update_progress(task_id, 40, "Generating SSL certificate")
    await asyncio.sleep(2)

    await update_progress(task_id, 70, "Installing certificate")
    await asyncio.sleep(1)

    await update_progress(task_id, 90, "Configuring HTTPS")
    await asyncio.sleep(1)

    return {"success": True, "message": "SSL installed successfully"}


# Register task handlers
task_queue.register_handler(TaskType.WEBSITE_CREATE, create_website_task)
task_queue.register_handler(TaskType.BACKUP_CREATE, create_backup_task)
task_queue.register_handler(TaskType.SSL_INSTALL, install_ssl_task)
