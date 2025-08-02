from typing import List
from pydantic import BaseModel, Field


# Pydantic models for Test case execution result generation
class TestCaseResult(BaseModel):
    test_case_id: str
    description: str
    status: str  # Pass or Fail


class TestExecutionResults(BaseModel):
    results: List[TestCaseResult]


# Pydantic models for FRD Generation
class FunctionalRequirement(BaseModel):
    id: str = Field(..., description="FR identifier like FR-1")
    description: str


class NonFunctionalRequirement(BaseModel):
    id: str = Field(..., description="NFR identifier like NFR-1")
    description: str


class UseCase(BaseModel):
    id: str = Field(..., description="Use case ID like UC-1")
    description: str


class FunctionalOverviewItem(BaseModel):
    description: str


class FRDModel(BaseModel):
    app_name: List[str]
    purpose: List[str]
    functional_overview: List[FunctionalOverviewItem]
    functional_requirements: List[FunctionalRequirement]
    error_handling_requirements: List[FunctionalRequirement]
    non_functional_requirements: List[NonFunctionalRequirement]
    use_cases: List[UseCase]

#Pydantic models for Feedback Generation (Critique Agent)
class CriticFeedback(BaseModel):
    FR_id: str = Field(..., description="FR identifier like FR-1")
    requirement_summary: str
    fulfillment: str  # Fulfilled, Partially Fulfilled, Not Fulfilled
    critique: str
    suggestions: str


class CriticEvaluationResults(BaseModel):
    results: List[CriticFeedback]
