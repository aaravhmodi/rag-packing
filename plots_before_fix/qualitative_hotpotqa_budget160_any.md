# Qualitative Examples -- hotpotqa (budget=160, mode=any)

## Example 1

**Question:** In what year was the university where Sergei Aleksandrovich Tokarev was a professor founded?

**Gold answer:** 1755

| Method | Prediction | AIC | F1 | EM | Packed context (truncated) |
|---|---|---|---|---|---|
| Top-K | Алекса́ндрович То́карев | 1 | 0.00 | 0 | Sergei Aleksandrovich Tokarev (Russian: Серге́й Алекса́ндрович То́карев , 29 December 1899 – 19 April 1985) was a Russian scholar, ethnographer, historian, researcher of religious beliefs, doctor of historical sciences,... |
| MMR | Алекса́ндрович То́карев | 1 | 0.00 | 0 | Sergei Aleksandrovich Tokarev (Russian: Серге́й Алекса́ндрович То́карев , 29 December 1899 – 19 April 1985) was a Russian scholar, ethnographer, historian, researcher of religious beliefs, doctor of historical sciences,... |
| Focused | Алекса́ндрович То́карев | 1 | 0.00 | 0 | Sergei Aleksandrovich Tokarev (Russian: Серге́й Алекса́ндрович То́карев , 29 December 1899 – 19 April 1985) was a Russian scholar, ethnographer, historian, researcher of religious beliefs, doctor of historical sciences,... |
| AnswerSurvival | Алекса́ндрович То́карев | 0 | 0.00 | 0 | Sergei Aleksandrovich Tokarev (Russian: Серге́й Алекса́ндрович То́карев , 29 December 1899 – 19 April 1985) was a Russian scholar, ethnographer, historian, researcher of religious beliefs, doctor of historical sciences,... |

## Example 2

**Question:** Black Book starred the actress and writer of what heritage?

**Gold answer:** Dutch

| Method | Prediction | AIC | F1 | EM | Packed context (truncated) |
|---|---|---|---|---|---|
| Top-K | writer | 1 | 0.00 | 0 | Halina Reijn (born 10 November 1975) is a Dutch actress and writer. Publishers Weekly", "Booklist", and "Quill & Quire" all gave the book starred reviews. Le Livre Noir du Capitalisme ("The Black Book of Capitalism") is... |
| MMR | writer | 1 | 0.00 | 0 | Halina Reijn (born 10 November 1975) is a Dutch actress and writer. Publishers Weekly", "Booklist", and "Quill & Quire" all gave the book starred reviews. Le Livre Noir du Capitalisme ("The Black Book of Capitalism") is... |
| Focused | writer | 1 | 0.00 | 0 | Halina Reijn (born 10 November 1975) is a Dutch actress and writer. Publishers Weekly", "Booklist", and "Quill & Quire" all gave the book starred reviews. Le Livre Noir du Capitalisme ("The Black Book of Capitalism") is... |
| AnswerSurvival | Black Book | 1 | 0.00 | 0 | It is the novelization of the Dutch film "Black Book" (2006). Halina Reijn (born 10 November 1975) is a Dutch actress and writer. Black Book (Dutch: Zwartboek ) is a 2006 Dutch thriller film co-written and directed by Pa... |
