# Week 2 Research Note: Inference and Sampling

## Scope

This file is an overview of the notebook `week2_inference_sampling.ipynb` which examined how temperature, top-k, and top-p change DistilGPT-2's next-token distribution for the prompt, `"The most famous movie star in 2026 is"`.

## Part 3: Predictions vs. Actual Results

| Setting | Prediction | Actual result and finding |
|---|---|---|
| Temperature `1e-6`, top-p `1.0` | A very sharp distribution with 3-5 tokens retained and a maximum probability near `0.8`. | Entropy was approximately `0`, the maximum probability was `1.000`, and only one token was retained. Near-zero temperature made the distribution effectively deterministic, even more sharply than predicted. |
| Temperature `0.7`, top-p `1.0` | A maximum probability around `0.3-0.4`, higher entropy, and nearly the entire vocabulary retained. | Entropy was `4.161`, the maximum probability was `0.257`, and the full vocabulary was effectively retained. The reported count of `50,258` is an off-by-one artifact in the notebook's top-p function when `p=1.0`; DistilGPT-2 has `50,257` vocabulary entries. The overall prediction was correct, but the distribution was flatter than expected. |
| Temperature `1.3`, top-p `0.9` | A lower maximum probability, higher entropy, and roughly 30,000 retained tokens. | Entropy rose to `7.761`, the maximum probability fell to `0.027`, and only `4,394` tokens were needed to reach 90% probability mass. The direction of the prediction was correct, but the retained set was much smaller than expected. |

These results show that temperature strongly changes the concentration of probability. Near-zero temperature collapses probability onto one token, while higher temperature spreads probability across many tokens and increases entropy. However, a high-entropy distribution does not mean every token contributes equally: at temperature `1.3`, fewer than 4,400 tokens still contained 90% of the probability mass.

## Part 4: Failure Case

The failure case used a fixed top-k value of `10` at temperatures `0.5` and `2.0`. At temperature `0.5`, the top 10 tokens contained `0.864191` probability mass. At temperature `2.0`, those same 10 highest-ranked tokens contained only `0.024412`, so top-k discarded about 97.6% of the original probability mass.

This is a failure because raising temperature is intended to increase variety, but fixed top-k still permits exactly 10 tokens. After top-k removed the rest, renormalization increased the highest token's probability from `0.004602` to `0.188520`. The final distribution therefore made a token look much more likely while excluding nearly all of the diversity created by the higher temperature.

### Explanation and Mitigation

Temperature changes the shape of the distribution, but top-k ignores that shape and always keeps a fixed number of tokens. This works reasonably well when probability is concentrated, but it can be too restrictive when probability is spread broadly.

Top-p provides an adaptive mitigation. It keeps the smallest group of highest-probability tokens whose probabilities add up to at least `p`. At temperature `2.0` and `top_p=0.50`, it retained `1,983` tokens with a combined probability mass of `0.500070`, then renormalized them to sum to 1. Unlike fixed top-k, top-p preserved a broader set of choices when the distribution became flatter.

## Conclusion

 The main practical finding is that temperature and truncation (top-p or top-k) must be considered together: high temperature alone does not ensure diverse sampling when a small fixed top-k immediately removes most of the resulting probability mass. Top-p sampling better preserves the intended effect of temperature.
