# Scrappy Market Agentic AI – System Architecture

## Overview

The Scrappy Market Agentic AI platform enables business users to investigate retail performance using natural language questions. The system uses a multi-agent architecture powered by LangGraph, a FastAPI backend that provides controlled access to the data layer, and a SQL Server database containing synthetic retail datasets and analytical views.

This architecture is designed to support explainable AI investigations while ensuring safe, structured interaction with the database.

---

# High-Level System Flow

User → Streamlit UI → LangGraph Agents → FastAPI API Layer → SQL Server → Response Agent → Streamlit UI

---

## System Architecture Diagram

```mermaid
flowchart LR

User["Business User"]
UI["Streamlit UI"]

Orchestrator["LangGraph Brain\n(Investigation State)"]

Intent["Intent Agent"]
Planner["Investigation Planner Agent"]
Lineage["Lineage / Context Agent"]
QueryBuilder["Query Builder Agent"]
Validator["Data Validation Agent"]
Response["Response Agent"]

API["FastAPI Backend API"]

Meta["Metadata Endpoints\n/meta/views\n/meta/columns"]
Exec["Query Execution Endpoint\n/query/execute"]

DB["SQL Server\nScrappyMarket Database"]
Views["Analytical Views\nvw_sales_enriched\nvw_promotions_enriched"]

User --> UI
UI --> Orchestrator

Orchestrator --> Intent
Intent --> Planner
Planner --> Lineage
Lineage --> QueryBuilder
QueryBuilder --> Validator

Validator --> API

API --> Meta
API --> Exec

Exec --> DB
DB --> Views

DB --> Response
Response --> UI