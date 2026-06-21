Maricopa Eviction Agentic RAG Chatbot
Overview

The Maricopa Eviction Agentic RAG Chatbot is an AI-powered analytics platform designed to help users explore, analyze, and investigate eviction filing data from Maricopa County, Arizona.

Unlike a traditional chatbot, this system uses an Agentic Retrieval-Augmented Generation (RAG) architecture that dynamically chooses between structured database queries and document retrieval based on the user's question.

The platform combines:

Natural Language to SQL
Retrieval-Augmented Generation (RAG)
Agentic AI Workflows
Data Analytics
Document Intelligence
Forecasting and Trend Analysis
Problem Statement

Eviction data is often stored across spreadsheets, databases, court records, and legal documents, making analysis difficult for researchers, policymakers, journalists, and housing advocates.

This project provides a conversational AI interface that allows users to ask questions in plain English and receive data-driven answers backed by both structured datasets and supporting legal documents.

Examples:

Which ZIP codes had the highest eviction filings?
Show filing trends over time.
Explain this court order.
Generate an investigation report for a landlord.
Predict future eviction filing volumes.
Features
Structured Data Analytics
Natural language querying of eviction records
Automatic SQL generation
Trend analysis
ZIP code comparisons
Landlord analysis
Filing statistics
Document Intelligence
PDF ingestion
Legal document retrieval
Arizona landlord-tenant law search
Court order analysis
Agentic AI

The system automatically selects the best tool for answering a question.

Available tools:

SQL Query Tool
Vector Search Tool
Chart Generation Tool
PDF Report Tool
Reporting
Automated investigation reports
Landlord summaries
Trend analysis reports
PDF exports
Advanced Analytics
Forecasting future eviction filings
ZIP code clustering
Anomaly detection
Pattern discovery
System Architecture

User Query

↓

React Frontend

↓

FastAPI Backend

↓

AI Agent

↓

(SQL Tool | Vector Search Tool | Analytics Tool | PDF Tool)

↓

Response Generation

Technology Stack
Frontend
React
Vite
JavaScript
Tailwind CSS
Backend
FastAPI
Python
Database
SQLite
PostgreSQL (future enhancement)
Vector Database
ChromaDB
AI and NLP
OpenAI API
LangChain
RAG Pipelines
Data Science
Pandas
NumPy
Scikit-learn
Prophet
Deployment
Docker
Vercel
Railway / Render
Project Structure

maricopa-eviction-agent/

├── backend/

│ ├── api/

│ ├── agents/

│ ├── database/

│ ├── rag/

│ ├── analytics/

│ └── reports/

│

├── frontend/

│ ├── src/

│ ├── components/

│ └── pages/

│

├── data/

│ ├── raw/

│ └── processed/

│

├── docs/

│ ├── legal_documents/

│ └── court_orders/

│

├── chroma_db/

├── notebooks/

├── tests/

└── README.md

Workflow
SQL Workflow

User Question

↓

OpenAI

↓

Generate SQL Query

↓

SQLite Database

↓

Results

↓

Natural Language Explanation

RAG Workflow

User Question

↓

Embedding Generation

↓

ChromaDB Search

↓

Relevant Document Chunks

↓

LLM Response

Example Questions
Data Analytics
Which ZIP codes have the highest eviction filing rates?
Show monthly filing trends.
Compare filings between 2024 and 2025.
Which landlords appear most frequently?
Legal Research
What does Arizona law say about notice periods?
Explain this court order.
Summarize the eviction policy document.
Investigations
Investigate landlord ABC.
Generate a report on ZIP code 85009.
Identify unusual filing spikes.
Future Enhancements
Multi-agent architecture
Real-time court data integration
Interactive dashboards
GIS heat maps
Advanced forecasting models
User authentication
Role-based access control
Learning Outcomes

This project demonstrates:

Full-Stack Development
Data Engineering
Data Analytics
Generative AI
Agentic AI Systems
Retrieval-Augmented Generation (RAG)
Natural Language Processing
Machine Learning
API Development
Author

Poojitha Nuthalapati

Data Science (Business Analytics) Student

Arizona State University

Interested in AI, Data Science, Analytics, and Intelligent Systems.