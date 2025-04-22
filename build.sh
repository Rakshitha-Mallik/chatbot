#!/bin/bash
pip install -r requirements.txt
guardrails hub install hub://guardrails/logic_check
guardrails hub install hub://guardrails/competitor_check   
guardrails hub install hub://guardrails/responsiveness_check 
guardrails hub install hub://guardrails/response_evaluator
guardrails hub install hub://guardrails/qa_relevance_llm_eval
guardrails hub install hub://guardrails/toxic_language 