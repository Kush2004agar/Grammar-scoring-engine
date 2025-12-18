# Feature Importance

## Top Features by Coefficient

Features are standardized, so coefficients represent the expected change in predicted score for a one-standard-deviation increase in the feature, holding others constant.

| Rank | Feature | Coefficient | Interpretation |
|------|---------|-------------|---------------|
| 9 | num_agreement_errors_per_100_tokens | 0.2500 | Higher values -> higher predicted score |
| 13 | num_tokens | 0.2225 | Higher values -> higher predicted score |
| 20 | subordinate_clause_ratio | 0.1743 | Higher values -> higher predicted score |
| 14 | num_sentences | 0.1616 | Higher values -> higher predicted score |
| 21 | verb_token_ratio | 0.0787 | Higher values -> higher predicted score |
| 10 | num_article_errors_per_100_tokens | 0.0395 | Higher values -> higher predicted score |
| 16 | num_clauses | 0.0299 | Higher values -> higher predicted score |
| 5 | num_preposition_errors | 0.0193 | Higher values -> higher predicted score |
| 15 | avg_sentence_length_tokens | 0.0123 | Higher values -> higher predicted score |
| 22 | fragment_ratio | 0.0122 | Higher values -> higher predicted score |
| 8 | num_verb_tense_errors_per_100_tokens | 0.0026 | Higher values -> higher predicted score |
| 12 | num_word_order_errors_per_100_tokens | 0.0000 | Lower values -> lower predicted score |
| 6 | num_word_order_errors | 0.0000 | Lower values -> lower predicted score |
| 11 | num_preposition_errors_per_100_tokens | -0.0315 | Lower values -> lower predicted score |
| 18 | num_coord_conj | -0.0488 | Lower values -> lower predicted score |
| 23 | pronoun_subject_ratio | -0.0489 | Lower values -> lower predicted score |
| 7 | num_grammar_errors_per_100_tokens | -0.0653 | Lower values -> lower predicted score |
| 1 | num_grammar_errors | -0.0673 | Lower values -> lower predicted score |
| 17 | num_subordinate_clauses | -0.0676 | Lower values -> lower predicted score |
| 2 | num_verb_tense_errors | -0.0756 | Lower values -> lower predicted score |


## Summary

- **Total features**: 23
- **Positive coefficients**: 11 (associated with higher scores)
- **Negative coefficients**: 10 (associated with lower scores)
- **Most important feature**: num_agreement_errors_per_100_tokens (coefficient: 0.2500)
