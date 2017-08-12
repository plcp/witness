
# witness

Knowledge abstraction layer, provides automation for:
 - Knowledge extraction
 - Evidence aggregation
 - Semantic examination
(…and more)

# Quick setup

Please note `numpy` is required as dependency :
```sh
pip install numpy
pip install witness
```

You can also use the repository:
```sh
git clone https://github.com/plcp/witness
cd witness
python -i example.py
```
We support **python2.7** and **python3.6** (other versions left untested).

# TL;DR

We handle information as clusters of [beta-binomial
distributions](https://en.wikipedia.org/wiki/Beta-binomial_distribution)
 and borrow some abstractions to
[subjective logics](https://scholar.google.fr/scholar?q=subjective+logic).

Then, we provide several interfaces to ease clear usage of these
abstractions and to automate our typical work flow:
 1. **Extract** knowledge from a stream of raw data.
 2. **Aggregate** the gathered evidences within a knowledge base.
 3. **Query** the knowledge base for pieces of useful insights.

We support a tag-based semantic abstraction to enable an intuitive use of the
API by the end-user while remaining open to more subtle approaches.
Thus, being able to write readable code such as:

```python
>>> import witness as wit
>>> from example import weather_labels
>>> o = wit.oracle.new(wit.backends.naive)
>>> o.add_labels(weather_labels)
>>> o.submit('!warm')
>>> o.query('cold')
['cold']
>>> o.submit('thunder')
>>> o.query('thunderstorm')
['cloudly', 'thunder']
>>> o.submit('rainstorm')
>>> o.query('thunderstorm')
['thunderstorm', 'rainy', 'thunder', 'cloudly']
```

We also support various opinion-related abstractions to provide easy means to
weight and discount information based on reputation or apriori. Further work is
needed to provide more components for a seamless "plug and play" experience.

# Development status

Active, Work in progress.

**API still subject to frequent backward-incompatible revisions.**
