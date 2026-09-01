# Findings
I compared equivalent World Health Organization (WHO) hypertension-prevention passages. English used 272 tokens with `cl100k_base`(tokenizer for GPT-4) and 269 tokens with `o200k_base` (tokenizer for GPT-4o and greater models); Spanish used 437 and 361 tokens, respectively. This means Spanish required 61% more tokens with GPT-4’s tokenizer and 34% more with GPT-4o’s. Consequently, a 128,000-token window held about 470 English copies but only 292 Spanish copies using cl100k_base.

## Reasoning 

The difference likely results from how byte-pair encoding (BPE) builds its vocabulary. BPE originated as a data compression technique and repeatedly merges character or byte sequences that occur frequently in its training data. Common English sequences therefore tend to receive complete tokens, while less-represented Spanish sequences remain split. In the notebook, `pressure`, `women`, and `medicine` each used one token, whereas their spanish equivalent `tensión`, `mujeres`, and `medicamentos` each required three tokens. The reduction from a 61% disparity with `cl100k_base` to 34% with `o200k_base` is consistent with improved multilingual vocabulary coverage likely due to the increased vocabulary size `100k` -> `200k`.

The apostrophe comparison in my failure case demonstrates the same frequency-based behavior. `Don't` with the straight ASCII apostrophe (U+0027) was one `o200k_base` token, while `Don’t` with the curly apostrophe (U+2019) required two tokens. Although they look similar, they are different byte sequences, and only the more frequently encountered form received a complete merge to a single token. Normalizing the apostrophes can reduce unnecessary tokens when preserving the original punctuation is not required. In the notebook I offered the code below as a simple mitigation strategy for normalizing the apostrphe. 

``` python
def normalize_apostrophes(text):
    return text.replace("’", "'")
```
One limitation is that the Spanish translation was also longer: 267 words versus 220 English words. Therefore, the total token difference reflects both translation length and less-efficient Spanish tokenization.