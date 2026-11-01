# Offline English frequency data

`en_9k.txt` is an adapted subset of 9,000 alphabetic, length-capped, deduplicated entries from [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords), file [content/2018/en/en_50k.txt](https://github.com/hermitdave/FrequencyWords/blob/master/content/2018/en/en_50k.txt). The source is an OpenSubtitles 2018 word-frequency compilation, sorted from most to least frequent.

The source data is licensed **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. Source and license: [FrequencyWords README](https://github.com/hermitdave/FrequencyWords#license) and [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Attribution: hermitdave/FrequencyWords and the OpenSubtitles corpus contributors. The changes are filtering to letters a-z, dropping duplicates, restricting length to 22 characters, and retaining the first 9,000 surviving entries. This adapted data is distributed under CC BY-SA 4.0.

No network download or package installation is necessary at runtime. Only this compact list is bundled; the predictor uses a lightweight in-memory prefix lookup, not a serialized tree or large language model.
