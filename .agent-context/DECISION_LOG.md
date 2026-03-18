# Architectural Decision Log

## ADR-001: Use Streamlit Instead of React
**Date:** 2026-03-17
**Context:** Need heavy data visualization, 24-hour timeline, team may not have JS expertise.
**Decision:** Streamlit for rapid Python-based dashboards with Plotly integration.
**Consequences:** + Fast development, - Limited custom UI, but acceptable for MVP.

## ADR-002: NetworkX Instead of Neo4j
**Date:** 2026-03-17
**Context:** Knowledge graph for 50 hotels doesn't need full graph DB.
**Decision:** NetworkX in-memory with JSON persistence.
**Consequences:** Simpler deployment, no separate database service.

## ADR-003: Whisper + Gemini for Expert Insights
**Date:** 2026-03-17
**Context:** Need to extract structured predictions from video transcripts.
**Decision:** yt-dlp for download, Whisper API (free tier) for transcription, Gemini 2.5 Flash for extraction.
**Consequences:** ~$0.006 per minute of audio, 10 videos = ~$3, acceptable for hackathon.

## ADR-004: LSTM + XGBoost Hybrid
**Date:** 2026-03-17
**Context:** Time series forecasting needs both sequential and tabular feature handling.
**Decision:** LSTM for temporal patterns, XGBoost for event features, weighted ensemble.
**Consequences:** Better accuracy, moderate complexity.

## ADR-005: Visualization-First Design
**Date:** 2026-03-17
**Context:** User demanded "heavy visual, not just say show them what we did with every little piece".
**Decision:** Every component must have visualization: causal DAG, time series with markers, expert agreement bars, shortage heatmap.
**Consequences:** More frontend work, but meets core requirement.
