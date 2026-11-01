# Offline English frequency data

`en_9k.txt` is an adapted subset of 9,000 alphabetic, length-capped, deduplicated entries from [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords), file [content/2018/en/en_50k.txt](https://github.com/hermitdave/FrequencyWords/blob/master/content/2018/en/en_50k.txt). The source is an OpenSubtitles 2018 word-frequency compilation, sorted from most to least frequent.

The source data is licensed **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. Source and license: [FrequencyWords README](https://github.com/hermitdave/FrequencyWords#license) and [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Attribution: hermitdave/FrequencyWords and the OpenSubtitles corpus contributors. The changes are filtering to letters a-z, dropping duplicates, restricting length to 22 characters, and retaining the first 9,000 surviving entries. This adapted data is distributed under CC BY-SA 4.0.

No network download or package installation is necessary at runtime. Only this compact list is bundled; the predictor uses a lightweight in-memory prefix lookup, not a serialized tree or large language model.

# Static English next-word context data

`en_context_bigrams.tsv` is a compact, **modified subset** of
[synth-inc/predictive-bigrams](https://github.com/synth-inc/predictive-bigrams),
source file [data/en_bigrams_50k.txt](https://github.com/synth-inc/predictive-bigrams/blob/main/data/en_bigrams_50k.txt),
blob SHA `208514436252cbb3834207d562f36773227e682d`.

The source supplies word-pair frequency counts derived from the
[Leipzig Corpora Collection](https://wortschatz.uni-leipzig.de/), with
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
attribution to the Leipzig project and corpus contributors. This derivative
retains lower-case alphabetic word pairs with source counts >= 50, aggregates
duplicate pairs, selects at most eight continuations per predecessor, sorts
them deterministically, and stores the counts in base-36 notation. These
counts support **relative conditional ranking** within a pruned context, not
fully calibrated probabilities.

Original upstream compilation: synth-inc/predictive-bigrams (OnitKeyboard).
Original corpus: Leipzig Corpora Collection. Both are credited for the adapted
data. No original corpus sentences, code from other keyboard implementations,
or external model weights are bundled. The adapted data is shared with its
source attribution under CC BY 4.0.

The Python runtime never downloads data. When the optional table or module is
absent, Firefly retains its original frequency/personal-context predictor.
