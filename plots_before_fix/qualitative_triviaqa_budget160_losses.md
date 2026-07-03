# Qualitative Examples -- triviaqa (budget=160, mode=losses)

## Example 1

**Question:** Who wrote the 1951 novel ‘From here to Eternity’?

**Gold answer:** James Jones

| Method | Prediction | AIC | F1 | EM | Packed context (truncated) |
|---|---|---|---|---|---|
| Top-K | From Here to Eternity is the debut novel of American author James Jones, published by Scribner's in 1951. | 1 | 0.21 | 0 | From Here to Eternity is the debut novel of American author James Jones, published by Scribner's in 1951. From Here to Eternity is a 1953 drama film directed by Fred Zinnemann and based on the novel of the same name by J... |
| MMR | From Here to Eternity is the debut novel of American author James Jones, published by Scribner's in 1951. | 1 | 0.21 | 0 | From Here to Eternity is the debut novel of American author James Jones, published by Scribner's in 1951. Director Zinnemann later complained that the scene where Holmes is reprimanded was "the worst moment in the film,... |
| Focused | From Here to Eternity is the debut novel of American author James Jones, published by Scribner's in 1951. | 1 | 0.21 | 0 | From Here to Eternity is the debut novel of American author James Jones, published by Scribner's in 1951. From Here to Eternity is a 1953 drama film directed by Fred Zinnemann and based on the novel of the same name by J... |
| AnswerSurvival | From Here to Eternity features First Sergeant Milton Warden, Private Robert Prewitt, and Mess Sergeant Maylon Stark. | 1 | 0.00 | 0 | From Here to Eternity is the debut novel of American author James Jones, published by Scribner's in 1951. From Here to Eternity is a 1953 drama film directed by Fred Zinnemann and based on the novel of the same name by J... |

## Example 2

**Question:** Psychoanalyst A A Brill described what as ‘Torches of Freedom’ in the 1920’s, as symbols of equality for women?

**Gold answer:** Cigarettes

| Method | Prediction | AIC | F1 | EM | Packed context (truncated) |
|---|---|---|---|---|---|
| Top-K | ”Brandt, Allan M. Tobacco companies advertise to women around the world, showing cigarettes as symbols of upward mobility, gender equality and freedom. | 1 | 0.09 | 0 | Cigarettes were described as symbols of emancipation and equality with men. Cigarettes, which are equated with men, become torches of freedom.”Brandt, Allan M. Tobacco companies advertise to women around the world, showi... |
| MMR | Cigarettes were described as symbols of emancipation and equality with men. | 1 | 0.17 | 0 | Cigarettes were described as symbols of emancipation and equality with men. The term was first used by psychoanalyst A. In 1929 Bernays decided to pay women to smoke their “torches of freedom” as they walked in the Easte... |
| Focused | ”Brandt, Allan M. Tobacco companies advertise to women around the world, showing cigarettes as symbols of upward mobility, gender equality and freedom. | 1 | 0.09 | 0 | Brill stated that it was normal for women to smoke because of oral fixation and said, “Today the emancipation of women has suppressed many of their feminine desires. Brill when describing the natural desire for women to... |
| AnswerSurvival | He gained advice from psychoanalyst A. Tobacco companies advertise to women around the world, showing cigarettes as symbols of upward mobility, gender equality and freedom. | 1 | 0.08 | 0 | Cigarettes were described as symbols of emancipation and equality with men. Brill stated that it was normal for women to smoke because of oral fixation and said, “Today the emancipation of women has suppressed many of th... |

## Example 3

**Question:** Madame de Pompadour and Madame du Barry were mistresses of which French King?

**Gold answer:** Louis XV

| Method | Prediction | AIC | F1 | EM | Packed context (truncated) |
|---|---|---|---|---|---|
| Top-K | A king might have numerous mistresses but have a single "favourite mistress" or "official mistress" (in French, "maîtresse en titre"), as with Louis XV and Madame de Pompadour. | 1 | 0.14 | 0 | * Vatel, Charles, Histoire de madame du Barry, L. * The Pompadour hairstyle was named after Madame de Pompadour. * Saint-André, Claude, A King's favourite, Madame du Barry, and her times from hitherto unpublished documen... |
| MMR | A king might have numerous mistresses but have a single "favourite mistress" or "official mistress" (in French, "maîtresse en titre"), as with Louis XV and Madame de Pompadour. | 1 | 0.14 | 0 | * Saint-André, Claude, A King's favourite, Madame du Barry, and her times from hitherto unpublished documents, with an introduction by Pierre de Nolhac, New York, Mc Bride, Nast & Company, 1915; translated from the Frenc... |
| Focused | A king might have numerous mistresses but have a single "favourite mistress" or "official mistress" (in French, "maîtresse en titre"), as with Louis XV and Madame de Pompadour. | 1 | 0.14 | 0 | * Vatel, Charles, Histoire de madame du Barry, L. * Saint-André, Claude, A King's favourite, Madame du Barry, and her times from hitherto unpublished documents, with an introduction by Pierre de Nolhac, New York, Mc Brid... |
| AnswerSurvival | * Vatel, Charles, Histoire de madame du Barry, L. A king might have numerous mistresses but have a single "favourite mistress" or "official mistress" (in French, "maîtresse en titre"), as with Louis XV and Madame de Pompadour. | 1 | 0.11 | 0 | * Vatel, Charles, Histoire de madame du Barry, L. A king might have numerous mistresses but have a single "favourite mistress" or "official mistress" (in French, "maîtresse en titre"), as with Louis XV and Madame de Pomp... |

## Example 4

**Question:** "Who wrote numerous short stories and plays and the novels ""Of Human Bondage"", ""The Moon And Sixpence"" and ""Cakes And Ale""?"

**Gold answer:** Somerset Maugham

| Method | Prediction | AIC | F1 | EM | Packed context (truncated) |
|---|---|---|---|---|---|
| Top-K | Maugham | 0 | 0.67 | 0 | That book is The Moon and Sixpence. Based on four of his short stories. A third collection of Maugham short stories. Another collection based on short stories. But the book I like best is Cakes and Ale ... Maugham drew h... |
| MMR | Of Human Bondage (1915) is a novel by W. Maugham drew his title from the remark of Sir Toby Belch to Malvolio in William Shakespeare's Twelfth Night: "Dost thou think, because thou art virtuous, there shall be no more cakes and ale?"  Cakes and ale are also the emblems of the good life in the moral of the fable attributed to Aesop, "The Town Mouse and the Country Mouse": "Better beans and bacon in peace than cakes and ale in fear. | 0 | 0.03 | 0 | That book is The Moon and Sixpence. Based on four of his short stories. Of Human Bondage (1915) is a novel by W. Maugham drew his title from the remark of Sir Toby Belch to Malvolio in William Shakespeare's Twelfth Night... |
| Focused | Two of his later novels were based on historical people: The Moon and Sixpence is about the life of Paul Gauguin; and Cakes and Ale contains what were taken as thinly veiled and unflattering characterizations of the authors Thomas Hardy (who had died two years previously) and Hugh Walpole. | 1 | 0.00 | 0 | That book is The Moon and Sixpence. In 1916, Maugham travelled to the Pacific to research his novel The Moon and Sixpence, based on the life of Paul Gauguin. Based on four of his short stories. A third collection of Maug... |
| AnswerSurvival | Of Human Bondage (1915) is a novel by W. Cakes and Ale, or, The Skeleton in the Cupboard (1930) is a novel by the British author W. The Modern Library ranked Of Human Bondage No. | 1 | 0.00 | 0 | That book is The Moon and Sixpence. In 1916, Maugham travelled to the Pacific to research his novel The Moon and Sixpence, based on the life of Paul Gauguin. Based on four of his short stories. Another collection based o... |
