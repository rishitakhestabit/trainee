from dataclasses import dataclass, field
from typing import List, Dict

# Defines all message protocol types for multi-agent communication

@dataclass
class UserTask:
    """Initial task from user to planner."""
    task: str

@dataclass
class TaskPlan:
    """Planner's breakdown of task into subtasks."""
    original_task: str
    subtasks: List[str]
    execution_graph: Dict[str, List[str]]  # DAG structure

@dataclass
class WorkerTask:
    """Task assigned to worker agents."""
    task: str
    subtask_id: str
    previous_results: List[str]          # Results from previous layer
    original_task: str = field(default="")  # Full original query for context

@dataclass
class WorkerResult:
    """Result from worker agent."""
    subtask_id: str
    result: str
    agent_id: str

@dataclass
class ReflectionTask:
    """Task for reflection agent to improve results."""
    original_task: str
    worker_results: List[WorkerResult]

@dataclass
class ReflectionResult:
    """Improved/refined result from reflection."""
    refined_result: str

@dataclass
class ValidationTask:
    """Task for validator to check quality."""
    original_task: str
    reflected_result: str

@dataclass
class ValidationResult:
    """Validation outcome with errors/approval."""
    is_valid: bool
    final_result: str

@dataclass
class FinalAnswer:
    """Final answer to user."""
    result: str
    validation_status: bool